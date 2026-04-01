"""
facebook_watcher.py — Facebook & Instagram Watcher for AI Employee (Gold Tier)

Monitors Facebook Page and Instagram Business account via the Meta Graph API.
Detects new comments, messages, and mentions, then creates action files
in the vault for Claude to process.

Usage:
    python watchers/facebook_watcher.py --vault AI_Employee_Vault --interval 120
    python watchers/facebook_watcher.py --setup   # Test API connection

Environment variables (.env):
    FACEBOOK_PAGE_ACCESS_TOKEN=<long-lived page access token>
    FACEBOOK_PAGE_ID=<your page ID>
    INSTAGRAM_BUSINESS_ID=<your Instagram business account ID>  (optional)

Setup:
    1. Create a Meta App at https://developers.facebook.com/apps/
    2. Add "Pages" and "Instagram Basic Display" products
    3. Generate a Page Access Token (long-lived, 60-day)
    4. Set FACEBOOK_PAGE_ACCESS_TOKEN and FACEBOOK_PAGE_ID in .env
"""

import argparse
import json
import logging
import os
import sys
import time
import requests
from datetime import datetime
from pathlib import Path

# Load .env
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

sys.path.insert(0, str(Path(__file__).parent))
from base_watcher import BaseWatcher

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
)
logger = logging.getLogger("FacebookWatcher")

GRAPH_API_BASE = "https://graph.facebook.com/v21.0"


class FacebookWatcher(BaseWatcher):
    """Watch Facebook Page + Instagram for new interactions via Graph API."""

    def __init__(
        self,
        vault_path: str,
        page_access_token: str | None = None,
        page_id: str | None = None,
        instagram_id: str | None = None,
        check_interval: int = 120,
    ):
        super().__init__(vault_path, check_interval)
        self.token = page_access_token or os.getenv("FACEBOOK_PAGE_ACCESS_TOKEN", "")
        self.page_id = page_id or os.getenv("FACEBOOK_PAGE_ID", "")
        self.instagram_id = instagram_id or os.getenv("INSTAGRAM_BUSINESS_ID", "")
        self.processed_file = Path(vault_path) / ".facebook_processed.json"
        self.processed_ids: set[str] = set()
        self._load_processed()

    def _load_processed(self):
        if self.processed_file.exists():
            try:
                data = json.loads(self.processed_file.read_text(encoding="utf-8"))
                self.processed_ids = set(data.get("ids", []))
            except Exception:
                self.processed_ids = set()

    def _save_processed(self):
        self.processed_file.write_text(
            json.dumps({"ids": list(self.processed_ids)}, indent=2),
            encoding="utf-8",
        )

    def _graph_get(self, endpoint: str, params: dict | None = None) -> dict:
        """Make a GET request to the Meta Graph API."""
        params = params or {}
        params["access_token"] = self.token
        resp = requests.get(f"{GRAPH_API_BASE}/{endpoint}", params=params, timeout=30)
        resp.raise_for_status()
        return resp.json()

    def _graph_post(self, endpoint: str, data: dict) -> dict:
        """Make a POST request to the Meta Graph API."""
        data["access_token"] = self.token
        resp = requests.post(f"{GRAPH_API_BASE}/{endpoint}", data=data, timeout=30)
        resp.raise_for_status()
        return resp.json()

    # ── Facebook Page Methods ────────────────────────────────────

    def get_page_posts(self, limit: int = 10) -> list[dict]:
        """Get recent posts from the Facebook Page."""
        result = self._graph_get(
            f"{self.page_id}/posts",
            {"fields": "id,message,created_time,permalink_url,shares,likes.summary(true),comments.summary(true)", "limit": str(limit)},
        )
        return result.get("data", [])

    def get_post_comments(self, post_id: str, limit: int = 25) -> list[dict]:
        """Get comments on a specific post."""
        result = self._graph_get(
            f"{post_id}/comments",
            {"fields": "id,from,message,created_time", "limit": str(limit)},
        )
        return result.get("data", [])

    def get_page_conversations(self, limit: int = 10) -> list[dict]:
        """Get recent Page inbox conversations (Messenger)."""
        result = self._graph_get(
            f"{self.page_id}/conversations",
            {"fields": "id,updated_time,participants,messages.limit(1){message,from,created_time}", "limit": str(limit)},
        )
        return result.get("data", [])

    def publish_post(self, message: str, link: str = "") -> dict:
        """Publish a post to the Facebook Page."""
        data = {"message": message}
        if link:
            data["link"] = link
        return self._graph_post(f"{self.page_id}/feed", data)

    def reply_to_comment(self, comment_id: str, message: str) -> dict:
        """Reply to a Facebook comment on a Page post."""
        return self._graph_post(f"{comment_id}/comments", {"message": message})

    def like_comment(self, comment_id: str) -> dict:
        """Like a comment on behalf of the Page."""
        return self._graph_post(f"{comment_id}/likes", {})

    def send_messenger_reply(self, recipient_id: str, message: str) -> dict:
        """Send a reply via Facebook Messenger (Page inbox)."""
        return self._graph_post(
            f"{self.page_id}/messages",
            {"recipient": json.dumps({"id": recipient_id}), "message": json.dumps({"text": message})},
        )

    def get_page_insights(self, metric: str = "page_impressions,page_engaged_users,page_fans", period: str = "day") -> list[dict]:
        """Get Page-level insights/analytics."""
        try:
            result = self._graph_get(
                f"{self.page_id}/insights",
                {"metric": metric, "period": period},
            )
            return result.get("data", [])
        except Exception as e:
            logger.warning(f"Could not fetch page insights: {e}")
            return []

    # ── Instagram Methods ────────────────────────────────────────

    def get_instagram_media(self, limit: int = 10) -> list[dict]:
        """Get recent Instagram media (requires Instagram Business account)."""
        if not self.instagram_id:
            return []
        result = self._graph_get(
            f"{self.instagram_id}/media",
            {"fields": "id,caption,media_type,timestamp,permalink,like_count,comments_count", "limit": str(limit)},
        )
        return result.get("data", [])

    def get_instagram_comments(self, media_id: str) -> list[dict]:
        """Get comments on an Instagram post."""
        result = self._graph_get(
            f"{media_id}/comments",
            {"fields": "id,text,username,timestamp"},
        )
        return result.get("data", [])

    def reply_to_instagram_comment(self, comment_id: str, message: str) -> dict:
        """Reply to an Instagram comment."""
        return self._graph_post(f"{comment_id}/replies", {"message": message})

    def get_instagram_insights(self, media_id: str) -> list[dict]:
        """Get insights for a specific Instagram media post."""
        try:
            result = self._graph_get(
                f"{media_id}/insights",
                {"metric": "impressions,reach,engagement"},
            )
            return result.get("data", [])
        except Exception as e:
            logger.warning(f"Could not fetch IG insights for {media_id}: {e}")
            return []

    # ── Watcher Interface ────────────────────────────────────────

    def check_for_updates(self) -> list:
        items = []

        # 1. Check Facebook Page post comments
        try:
            posts = self.get_page_posts(limit=5)
            for post in posts:
                comments_data = post.get("comments", {}).get("data", [])
                for comment in comments_data:
                    cid = comment["id"]
                    if cid not in self.processed_ids:
                        items.append({
                            "type": "facebook_comment",
                            "id": cid,
                            "post_id": post["id"],
                            "from": comment.get("from", {}).get("name", "Unknown"),
                            "message": comment.get("message", ""),
                            "created_time": comment.get("created_time", ""),
                            "post_message": post.get("message", "")[:100],
                        })
        except Exception as e:
            logger.warning(f"Error checking FB comments: {e}")

        # 2. Check Facebook Page messages (Messenger)
        try:
            convos = self.get_page_conversations(limit=5)
            for convo in convos:
                messages = convo.get("messages", {}).get("data", [])
                for msg in messages:
                    mid = f"msg_{convo['id']}_{msg.get('created_time', '')}"
                    if mid not in self.processed_ids:
                        sender = msg.get("from", {}).get("name", "Unknown")
                        items.append({
                            "type": "facebook_message",
                            "id": mid,
                            "conversation_id": convo["id"],
                            "from": sender,
                            "message": msg.get("message", ""),
                            "created_time": msg.get("created_time", ""),
                        })
        except Exception as e:
            logger.warning(f"Error checking FB messages: {e}")

        # 3. Check Instagram comments
        if self.instagram_id:
            try:
                media_list = self.get_instagram_media(limit=5)
                for media in media_list:
                    if media.get("comments_count", 0) > 0:
                        comments = self.get_instagram_comments(media["id"])
                        for comment in comments:
                            cid = f"ig_{comment['id']}"
                            if cid not in self.processed_ids:
                                items.append({
                                    "type": "instagram_comment",
                                    "id": cid,
                                    "media_id": media["id"],
                                    "username": comment.get("username", "Unknown"),
                                    "text": comment.get("text", ""),
                                    "timestamp": comment.get("timestamp", ""),
                                    "media_caption": media.get("caption", "")[:100],
                                })
            except Exception as e:
                logger.warning(f"Error checking IG comments: {e}")

        return items

    def create_action_file(self, item) -> Path:
        item_type = item["type"]
        item_id = item["id"]
        now = datetime.now()

        if item_type == "facebook_comment":
            content = f"""---
type: facebook_comment
from: {item['from']}
post_id: {item['post_id']}
created_time: {item['created_time']}
priority: medium
status: pending
---

## Facebook Comment

**From:** {item['from']}
**On post:** {item['post_message']}...
**Comment:** {item['message']}

## Suggested Actions
- [ ] Reply to comment
- [ ] Like the comment
- [ ] Flag for review
- [ ] Archive
"""
        elif item_type == "facebook_message":
            content = f"""---
type: facebook_message
from: {item['from']}
conversation_id: {item['conversation_id']}
created_time: {item['created_time']}
priority: high
status: pending
---

## Facebook Page Message

**From:** {item['from']}
**Message:** {item['message']}

## Suggested Actions
- [ ] Reply via Messenger
- [ ] Forward to team
- [ ] Archive
"""
        elif item_type == "instagram_comment":
            content = f"""---
type: instagram_comment
username: {item['username']}
media_id: {item['media_id']}
timestamp: {item['timestamp']}
priority: medium
status: pending
---

## Instagram Comment

**From:** @{item['username']}
**On post:** {item['media_caption']}...
**Comment:** {item['text']}

## Suggested Actions
- [ ] Reply to comment
- [ ] Like the comment
- [ ] Flag for review
- [ ] Archive
"""
        else:
            content = f"---\ntype: {item_type}\nstatus: pending\n---\n\nUnknown item: {json.dumps(item, indent=2)}\n"

        safe_id = item_id.replace("/", "_").replace(":", "_")[:60]
        filename = f"FB_{item_type.upper()}_{safe_id}_{now.strftime('%Y%m%d_%H%M%S')}.md"
        filepath = self.needs_action / filename
        filepath.write_text(content, encoding="utf-8")

        self.processed_ids.add(item_id)
        self._save_processed()

        self.logger.info(f"Created action file: {filename}")
        return filepath

    # ── Summary Generation ───────────────────────────────────────

    def generate_summary(self) -> str:
        """Generate a markdown summary of recent Facebook + Instagram activity."""
        lines = [f"# Social Media Summary — {datetime.now().strftime('%Y-%m-%d')}\n"]

        # Facebook Page Insights
        insights = self.get_page_insights()
        if insights:
            lines.append("## Facebook Page Overview\n")
            for metric in insights:
                name = metric.get("title", metric.get("name", ""))
                values = metric.get("values", [{}])
                latest = values[-1].get("value", "N/A") if values else "N/A"
                lines.append(f"- **{name}:** {latest}")
            lines.append("")

        # Facebook posts
        try:
            posts = self.get_page_posts(limit=10)
            total_likes = 0
            total_comments = 0
            total_shares = 0
            lines.append("## Facebook Page Posts\n")
            lines.append("| Date | Post | Likes | Comments | Shares |")
            lines.append("|------|------|-------|----------|--------|")
            for p in posts:
                msg = (p.get("message") or "")[:60].replace("|", " ")
                likes = p.get("likes", {}).get("summary", {}).get("total_count", 0)
                comments = p.get("comments", {}).get("summary", {}).get("total_count", 0)
                shares = p.get("shares", {}).get("count", 0)
                total_likes += likes
                total_comments += comments
                total_shares += shares
                dt = p.get("created_time", "")[:10]
                lines.append(f"| {dt} | {msg}... | {likes} | {comments} | {shares} |")
            lines.append(f"| **Total** | | **{total_likes}** | **{total_comments}** | **{total_shares}** |")
            lines.append("")
        except Exception as e:
            lines.append(f"_Facebook data unavailable: {e}_\n")

        # Instagram media
        if self.instagram_id:
            try:
                media = self.get_instagram_media(limit=10)
                total_ig_likes = 0
                total_ig_comments = 0
                lines.append("## Instagram Posts\n")
                lines.append("| Date | Caption | Type | Likes | Comments |")
                lines.append("|------|---------|------|-------|----------|")
                for m in media:
                    caption = (m.get("caption") or "")[:50].replace("|", " ")
                    dt = m.get("timestamp", "")[:10]
                    ig_likes = m.get("like_count", 0)
                    ig_comments = m.get("comments_count", 0)
                    total_ig_likes += ig_likes
                    total_ig_comments += ig_comments
                    lines.append(
                        f"| {dt} | {caption}... | {m.get('media_type', '?')} | "
                        f"{ig_likes} | {ig_comments} |"
                    )
                lines.append(f"| **Total** | | | **{total_ig_likes}** | **{total_ig_comments}** |")
                lines.append("")
            except Exception as e:
                lines.append(f"_Instagram data unavailable: {e}_\n")
        else:
            lines.append("## Instagram\n_Not connected — set INSTAGRAM_BUSINESS_ID in .env_\n")

        return "\n".join(lines)


# ── CLI ──────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Facebook & Instagram Watcher")
    parser.add_argument("--vault", default=os.getenv("VAULT_PATH", "AI_Employee_Vault"))
    parser.add_argument("--interval", type=int, default=120)
    parser.add_argument("--setup", action="store_true", help="Test API connection and exit")
    args = parser.parse_args()

    watcher = FacebookWatcher(vault_path=args.vault, check_interval=args.interval)

    if args.setup:
        print("Testing Facebook Graph API connection...")
        if not watcher.token:
            print("ERROR: FACEBOOK_PAGE_ACCESS_TOKEN not set in .env")
            sys.exit(1)
        if not watcher.page_id:
            print("ERROR: FACEBOOK_PAGE_ID not set in .env")
            sys.exit(1)
        try:
            posts = watcher.get_page_posts(limit=1)
            print(f"OK — Connected to page. Found {len(posts)} recent post(s).")
            if watcher.instagram_id:
                media = watcher.get_instagram_media(limit=1)
                print(f"OK — Instagram connected. Found {len(media)} recent media.")
            else:
                print("INFO — No INSTAGRAM_BUSINESS_ID set; Instagram monitoring disabled.")
            print("\nSetup complete! Run without --setup to start watching.")
        except Exception as e:
            print(f"ERROR: {e}")
            sys.exit(1)
        return

    watcher.run()


if __name__ == "__main__":
    main()
