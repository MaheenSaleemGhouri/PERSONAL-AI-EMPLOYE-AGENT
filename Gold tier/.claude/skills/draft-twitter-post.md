# draft-twitter-post

Draft a tweet for Twitter/X and queue for human approval.

## Arguments

```
/draft-twitter-post [topic or context]
```

## Instructions

When invoked:

1. **Gather context** from Company_Handbook.md and recent vault activity.

2. **Draft the tweet**:
   - Maximum 280 characters.
   - Tone: concise, engaging, on-brand.
   - Include 1-3 relevant hashtags.
   - Optional: include a link if relevant.

3. **Create approval file** in `/Pending_Approval/`:

```markdown
---
created: <ISO timestamp>
type: twitter_post
status: pending_approval
risk: medium
platform: twitter
char_count: <number>
---

## Action Requested
Post the following tweet to Twitter/X.

## Draft Tweet

<tweet text — must be ≤280 characters>

## Character Count: <X>/280

## Reasoning
<Why this topic and angle>

## To Approve
Move to `/Approved/` or set `status: approved`.

## To Reject
Set `status: rejected`.
```

4. **Do NOT post** — wait for approval.
5. **Log** and **update Dashboard.md**.

## Rules

- Hard limit: 280 characters. Reject drafts that exceed this.
- Never post without approval.
- One tweet per invocation.
