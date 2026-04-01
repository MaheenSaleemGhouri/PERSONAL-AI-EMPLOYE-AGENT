# draft-linkedin-post

Draft a LinkedIn post for business promotion and queue it for human approval before publishing.

## Arguments

```
/draft-linkedin-post [topic or context]
```

Optional topic: a specific product, service, achievement, or campaign to highlight.
If omitted, Claude will infer a relevant topic from recent `/Done/` items and the Company_Handbook.md business context.

## Instructions

When invoked:

1. **Gather context**:
   - Read `Company_Handbook.md` to understand the business, tone, audience, and any content restrictions.
   - If a topic argument is given, use it as the focus.
   - If no topic, scan the last 5 entries in `/Logs/` and `/Done/` for recent wins, completed projects, or announcements worth sharing.

2. **Draft the LinkedIn post**:
   - Length: 150–300 words (optimal for LinkedIn engagement).
   - Tone: professional but human, first-person voice.
   - Structure:
     - **Hook** (first line — must stop the scroll)
     - **Body** (2–3 short paragraphs: context, insight, value)
     - **Call to Action** (comment, DM, visit link)
     - **Hashtags** (3–5 relevant hashtags)
   - Do NOT include any pricing, unverified claims, or confidential client details.

3. **Create an approval file** in `/Pending_Approval/` named `APPROVAL_REQUIRED_LinkedIn_Post_<YYYYMMDD>.md` with:

```markdown
---
created: <ISO timestamp>
type: linkedin_post
status: pending_approval
risk: medium
---

## Action Requested
Post the following content to LinkedIn.

## Draft Post

<full post text here>

## Reasoning
<Why this topic was chosen and what business goal it serves>

## To Approve
Move this file to `/Approved/` or set `status: approved` to trigger posting.

## To Reject
Set `status: rejected` and add a note explaining the issue.
```

4. **Do NOT post to LinkedIn autonomously** — always wait for human approval.

5. **Log the draft creation** in `/Logs/YYYY-MM-DD.md`.

6. **Update Dashboard.md** to show a pending approval item.

## Rules

- Never post publicly without explicit human approval.
- Do not fabricate testimonials, metrics, or client names.
- Respect Company_Handbook.md content and communication guidelines.
- One draft per invocation; do not batch-post.

## Example Usage

```
/draft-linkedin-post
/draft-linkedin-post "We just launched our new AI automation service for small businesses"
/draft-linkedin-post "Share our Q1 milestone: 10 clients onboarded"
```
