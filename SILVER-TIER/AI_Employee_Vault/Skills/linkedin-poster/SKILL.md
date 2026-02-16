---
skill_name: linkedin-poster
version: 1.0
tier: silver
trigger: SCHEDULED_LinkedInDraft_*.md appears in /Needs_Action/
---

# Skill: LinkedIn Post Drafter

## Purpose
Write a professional LinkedIn post draft aligned with current business goals.

## Input
- Scheduled task file in `/Needs_Action/`
- `Business_Goals.md` for business context and current focus
- `/Social/Posted/` to avoid repeating recent topics

## Steps
1. Read Business_Goals.md — understand current objectives and priorities
2. Scan the last 5 files in /Social/Posted/ — note topics already covered (avoid repeats)
3. Choose a fresh, relevant, and helpful post topic
4. Write the post: 150–300 words, professional and educational tone
5. Place 3–5 relevant hashtags at the very end of the post only
6. End the post with a question or a clear call-to-action
7. Save draft to: `/Social/LinkedIn_Drafts/DRAFT_<timestamp>.md`
8. Create approval file: `/Pending_Approval/LINKEDIN_<timestamp>.md`
9. Update Dashboard.md LinkedIn section (pending drafts + 1)
10. Move the task file to /Done/

## Post Quality Rules
- NO client names, NO personal information of any kind
- Content must be helpful and educational — never purely promotional
- Include exactly ONE call-to-action per post
- Hashtags go at the end only — never inline within the post body

## Approval File Format
```
---
type: approval_request
action: linkedin_post
draft_file: /Social/LinkedIn_Drafts/DRAFT_<timestamp>.md
status: pending
---
Review the draft at the path above.
Move THIS file to /Approved/ to publish the post.
Move THIS file to /Rejected/ to discard it.
```
