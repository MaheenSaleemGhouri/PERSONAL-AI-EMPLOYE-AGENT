---
skill_name: facebook-instagram-poster
version: 1.0
tier: gold
trigger: SCHEDULED_*Facebook*.md or SCHEDULED_*Instagram*.md in /Needs_Action/
---

# Skill: Facebook + Instagram Post Drafter

## Purpose
Draft professional social media posts for Facebook and Instagram, then route for approval.

## Input
- Scheduled task file in /Needs_Action/
- Business_Goals.md for context
- /Social/Posted/ to avoid repeating topics

## Steps
1. Read Business_Goals.md social media goals
2. Scan /Social/Posted/ — note last 3 posts per platform (avoid repeats)
3. Draft content appropriate for the platform:
   - Facebook: 100-250 words, conversational, can include questions
   - Instagram: 80-150 words, visual-friendly language, 5-8 hashtags
4. Save Facebook draft: /Social/Facebook_Drafts/DRAFT_<timestamp>.md
5. Save Instagram draft: /Social/Instagram_Drafts/DRAFT_<timestamp>.md
6. Create approval files in /Pending_Approval/ for each platform
7. Update Dashboard.md social section
8. Log action via audit_logger
9. Move task file to /Done/

## Hard Rules
- NO client names, NO personal data
- Facebook: max 1 post per day
- Instagram: max 1 post per day
- Images require separate human-added media — text only via MCP
