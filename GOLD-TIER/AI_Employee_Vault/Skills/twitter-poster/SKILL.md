---
skill_name: twitter-poster
version: 1.0
tier: gold
trigger: SCHEDULED_*Twitter*.md in /Needs_Action/
---

# Skill: Twitter/X Post Drafter

## Purpose
Draft concise Twitter/X posts aligned with business goals.

## Input
- Scheduled task file in /Needs_Action/
- Business_Goals.md for context
- /Social/Twitter_Drafts/ to avoid repeating recent tweets

## Steps
1. Read Business_Goals.md current focus
2. Check last 5 entries in /Social/Twitter_Drafts/ or /Social/Posted/
3. Write tweet: maximum 260 characters (leave 20 chars buffer from 280 limit)
4. Include 1-2 hashtags maximum
5. Save to: /Social/Twitter_Drafts/TWEET_<timestamp>.md
6. Create approval: /Pending_Approval/TWITTER_<timestamp>.md
7. Update Dashboard.md Twitter section
8. Log action via audit_logger
9. Move task file to /Done/

## Hard Rules
- Max 1 tweet per day — enforce strictly
- Max 280 characters — MCP server will reject longer tweets
- No replies or DMs without explicit human approval
- Content must be brand-appropriate and professional
