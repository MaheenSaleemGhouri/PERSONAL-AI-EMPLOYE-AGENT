# social-media-summary

Generate a comprehensive summary of Facebook, Instagram, Twitter/X, and LinkedIn social media activity.

## Arguments

```
/social-media-summary [period]
```

Optional period: `today`, `week` (default), `month`.

## Instructions

When invoked:

1. **Gather data from all social platforms**:

   **Facebook + Instagram** (via `watchers/facebook_watcher.py`):
   - Call `watcher.generate_summary()` for post metrics and engagement stats.

   **Twitter/X** (via `watchers/twitter_watcher.py`):
   - Call `watcher.generate_summary()` for tweet metrics and engagement stats.

   **LinkedIn** (from vault data):
   - Scan `/Done/` for completed LinkedIn posts within the period.
   - Count published posts and note any engagement data in the files.

2. **Compile the unified summary** and save to `/Logs/Social_Summary_YYYYMMDD.md`:

```markdown
---
created: <ISO timestamp>
type: social_media_summary
period: <period>
---

# Social Media Summary — <Date Range>

## Overview
| Platform | Posts | Likes | Comments | Shares/Retweets |
|----------|-------|-------|----------|-----------------|
| Facebook | X | X | X | X |
| Instagram | X | X | X | N/A |
| Twitter/X | X | X | X | X |
| LinkedIn | X | — | — | — |

## Facebook Highlights
<Top performing posts, engagement trends>

## Instagram Highlights
<Top performing media, engagement trends>

## Twitter/X Highlights
<Top tweets, mentions, engagement>

## LinkedIn Highlights
<Published posts from the period>

## Recommendations
1. <Content suggestion based on what performed well>
2. <Timing or frequency suggestion>
3. <Audience engagement opportunity>
```

3. **Update Dashboard.md** with social media stats.

4. **Log** to `/Logs/YYYY-MM-DD.md`.

## Rules

- Only report data that actually exists — do not fabricate metrics.
- If a platform is not configured, note it as "Not connected" rather than skipping.
- Keep recommendations actionable and specific.
