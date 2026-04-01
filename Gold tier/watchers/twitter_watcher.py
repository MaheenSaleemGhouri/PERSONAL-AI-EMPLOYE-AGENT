"""
twitter_watcher.py — Twitter/X Watcher for AI Employee (Gold Tier)

Monitors Twitter/X for mentions, DMs, and engagement via the Twitter API v2.
Creates action files in the vault for Claude to process.

Usage:
    python watchers/twitter_watcher.py --vault AI_Employee_Vault --interval 120
    python watchers/twitter_watcher.py --setup   # Test API connection

Environment variables (.env):
    TWITTER_BEARER_TOKEN=<your bearer token>
    TWITTER_API_KEY=<API key>
    TWITTER_API_SECRET=<API secret>
    TWITTER_ACCESS_TOKEN=<access token>
    TWITTER_ACCESS_SECRET=<access token secret>

Setup:
    1. Apply for Twitter Developer access at https://developer.twitter.com/
    2. Create a Project and App with OAuth 1.0a + OAuth 2.0
    3. Generate all tokens and set them in .env
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
from requests_oauthlib import OAuth1

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
logger = logging.getLogger("TwitterWatcher")

TWITTER_API_BASE = "https://api.twitter.com/2"


class TwitterWatcher(BaseWatcher):
    """Watch Twitter/X for mentions, replies, and engagement."""

    def __init__(
        self,
        vault_path: str,
        check_interval: int = 120,
    ):
        super().__init__(vault_path, check_interval)
        self.bearer_token = os.getenv("TWITTER_BEARER_TOKEN", "")
        self.api_key = os.getenv("TWITTER_API_KEY", "")
        self.api_secret = os.getenv("TWITTER_API_SECRET", "")
        self.access_token = os.getenv("TWITTER_ACCESS_TOKEN", "")
        self.access_secret = os.getenv("TWITTER_ACCESS_SECRET", "")
        self.processed_file = Path(vault_path) / ".twitter_processed.json"
        self.processed_ids: set[str] = set()
        self._user_id: str | None = None
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

    def _bearer_headers(self) -> dict:
        return {"Authorization": f"Bearer {self.bearer_token}"}

    def _oauth1(self) -> OAuth1:
        return OAuth1(
            self.api_key, self.api_secret,
            self.access_token, self.access_secret,
        )

    # ── API Methods ──────────────────────────────────────────────

    def get_me(self) -> dict:
        """Get authenticated user info."""
        resp = requests.get(
            f"{TWITTER_API_BASE}/users/me",
            headers=self._bearer_headers(),
            params={"user.fields": "id,name,username,public_metrics"},
            timeout=15,
        )
        resp.raise_for_status()
        return resp.json().get("data", {})

    @property
    def user_id(self) -> str:
        if self._user_id is None:
            me = self.get_me()
            self._user_id = me["id"]
        return self._user_id

    def get_mentions(self, limit: int = 10) -> list[dict]:
        """Get recent mentions of the authenticated user."""
        resp = requests.get(
            f"{TWITTER_API_BASE}/users/{self.user_id}/mentions",
            headers=self._bearer_headers(),
            params={
                "max_results": str(min(limit, 100)),
                "tweet.fields": "author_id,created_at,text,public_metrics",
                "expansions": "author_id",
                "user.fields": "username,name",
            },
            timeout=15,
        )
        resp.raise_for_status()
        data = resp.json()
        tweets = data.get("data", [])
        users = {u["id"]: u for u in data.get("includes", {}).get("users", [])}
        for tweet in tweets:
            author = users.get(tweet.get("author_id"), {})
            tweet["author_username"] = author.get("username", "unknown")
            tweet["author_name"] = author.get("name", "Unknown")
        return tweets

    def get_user_tweets(self, limit: int = 10) -> list[dict]:
        """Get recent tweets by the authenticated user."""
        resp = requests.get(
            f"{TWITTER_API_BASE}/users/{self.user_id}/tweets",
            headers=self._bearer_headers(),
            params={
                "max_results": str(min(limit, 100)),
                "tweet.fields": "created_at,text,public_metrics",
            },
            timeout=15,
        )
        resp.raise_for_status()
        return resp.json().get("data", [])

    def post_tweet(self, text: str) -> dict:
        """Post a tweet using OAuth 1.0a."""
        resp = requests.post(
            f"{TWITTER_API_BASE}/tweets",
            auth=self._oauth1(),
            json={"text": text},
            timeout=15,
        )
        resp.raise_for_status()
        return resp.json().get("data", {})

    # ── Watcher Interface ────────────────────────────────────────

    def check_for_updates(self) -> list:
        items = []
        try:
            mentions = self.get_mentions(limit=10)
            for mention in mentions:
                tid = mention["id"]
                if tid not in self.processed_ids:
                    items.append({
                        "type": "twitter_mention",
                        "id": tid,
                        "author": mention.get("author_username", "unknown"),
                        "author_name": mention.get("author_name", "Unknown"),
                        "text": mention.get("text", ""),
                        "created_at": mention.get("created_at", ""),
                        "metrics": mention.get("public_metrics", {}),
                    })
        except Exception as e:
            logger.warning(f"Error checking Twitter mentions: {e}")
        return items

    def create_action_file(self, item) -> Path:
        now = datetime.now()
        content = f"""---
type: twitter_mention
author: @{item['author']}
author_name: {item['author_name']}
tweet_id: {item['id']}
created_at: {item['created_at']}
priority: medium
status: pending
---

## Twitter Mention

**From:** @{item['author']} ({item['author_name']})
**Tweet:** {item['text']}
**Engagement:** {item['metrics'].get('like_count', 0)} likes, {item['metrics'].get('retweet_count', 0)} retweets, {item['metrics'].get('reply_count', 0)} replies

## Suggested Actions
- [ ] Reply to mention
- [ ] Like the tweet
- [ ] Retweet
- [ ] Flag for review
- [ ] Archive
"""
        filename = f"TWITTER_MENTION_{item['id']}_{now.strftime('%Y%m%d_%H%M%S')}.md"
        filepath = self.needs_action / filename
        filepath.write_text(content, encoding="utf-8")

        self.processed_ids.add(item["id"])
        self._save_processed()
        self.logger.info(f"Created action file: {filename}")
        return filepath

    # ── Summary ──────────────────────────────────────────────────

    def generate_summary(self) -> str:
        lines = [f"## Twitter/X Summary — {datetime.now().strftime('%Y-%m-%d')}\n"]
        try:
            me = self.get_me()
            metrics = me.get("public_metrics", {})
            lines.append(f"**Account:** @{me.get('username', '?')} ({me.get('name', '?')})")
            lines.append(f"**Followers:** {metrics.get('followers_count', 0)} | **Following:** {metrics.get('following_count', 0)}")
            lines.append(f"**Total Tweets:** {metrics.get('tweet_count', 0)}\n")
        except Exception as e:
            lines.append(f"_Account info unavailable: {e}_\n")

        try:
            tweets = self.get_user_tweets(limit=10)
            lines.append("### Recent Tweets\n")
            lines.append("| Date | Tweet | Likes | RTs | Replies |")
            lines.append("|------|-------|-------|-----|---------|")
            for t in tweets:
                text = t.get("text", "")[:60].replace("|", " ")
                m = t.get("public_metrics", {})
                dt = t.get("created_at", "")[:10]
                lines.append(f"| {dt} | {text}... | {m.get('like_count', 0)} | {m.get('retweet_count', 0)} | {m.get('reply_count', 0)} |")
            lines.append("")
        except Exception as e:
            lines.append(f"_Tweet data unavailable: {e}_\n")

        try:
            mentions = self.get_mentions(limit=10)
            lines.append(f"### Recent Mentions: {len(mentions)}\n")
        except Exception:
            pass

        return "\n".join(lines)


# ── CLI ──────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Twitter/X Watcher")
    parser.add_argument("--vault", default=os.getenv("VAULT_PATH", "AI_Employee_Vault"))
    parser.add_argument("--interval", type=int, default=120)
    parser.add_argument("--setup", action="store_true", help="Test API connection and exit")
    args = parser.parse_args()

    watcher = TwitterWatcher(vault_path=args.vault, check_interval=args.interval)

    if args.setup:
        print("Testing Twitter API v2 connection...")
        if not watcher.bearer_token:
            print("ERROR: TWITTER_BEARER_TOKEN not set in .env")
            sys.exit(1)
        try:
            me = watcher.get_me()
            print(f"OK — Authenticated as @{me.get('username')} ({me.get('name')})")
            print(f"     Followers: {me.get('public_metrics', {}).get('followers_count', 0)}")
            print("\nSetup complete! Run without --setup to start watching.")
        except Exception as e:
            print(f"ERROR: {e}")
            sys.exit(1)
        return

    watcher.run()


if __name__ == "__main__":
    main()
