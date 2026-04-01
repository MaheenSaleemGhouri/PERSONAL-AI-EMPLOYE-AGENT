# draft-facebook-post

Draft a Facebook Page post and queue it for human approval before publishing.

## Arguments

```
/draft-facebook-post [topic or context]
```

Optional topic. If omitted, Claude infers from recent activity and Company_Handbook.md.

## Instructions

When invoked:

1. **Gather context**:
   - Read `Company_Handbook.md` for business tone, audience, and content rules.
   - If a topic argument is given, use it as the focus.
   - If no topic, scan `/Logs/` and `/Done/` for recent wins or announcements.

2. **Draft the Facebook post**:
   - Length: 100–250 words (optimal for Facebook engagement).
   - Tone: conversational, engaging, on-brand.
   - Structure:
     - **Hook** (first 1-2 lines — must grab attention)
     - **Body** (value, story, or insight — 2-3 short paragraphs)
     - **Call to Action** (like, comment, share, visit link)
     - **Hashtags** (3-5 relevant hashtags)
   - Do NOT include pricing, unverified claims, or confidential details.

3. **Create an approval file** in `/Pending_Approval/`:

```markdown
---
created: <ISO timestamp>
type: facebook_post
status: pending_approval
risk: medium
platform: facebook
---

## Action Requested
Post the following content to the Facebook Page.

## Draft Post

<full post text here>

## Reasoning
<Why this topic was chosen and what business goal it serves>

## To Approve
Move this file to `/Approved/` or set `status: approved`.

## To Reject
Set `status: rejected` and add a note.
```

4. **Do NOT post to Facebook autonomously** — always wait for approval.

5. **Log** to `/Logs/YYYY-MM-DD.md`.

6. **Update Dashboard.md** with the pending approval item.

## Rules

- Never post publicly without explicit human approval.
- Do not fabricate testimonials, metrics, or client names.
- One draft per invocation.
