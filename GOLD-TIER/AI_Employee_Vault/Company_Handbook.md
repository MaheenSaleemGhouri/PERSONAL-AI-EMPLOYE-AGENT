---
last_updated: 2026-02-15
version: 1.0
---

# Company Handbook — Rules of Engagement

## Communication Rules
- Always be polite and professional in all replies
- Response time target: within 24 hours
- Never send emails to new contacts without human approval

## Financial Rules
- Flag ANY payment over $100 for human approval
- Never auto-approve payments to new recipients
- Log all transactions regardless of amount

## Email Triage Rules
- Mark emails from unknown senders as `priority: low`
- Mark emails with keywords ["urgent", "invoice", "payment", "ASAP"] as `priority: high`
- Draft replies for high-priority emails — never auto-send

## File Processing Rules
- Process files dropped into /Inbox within 5 minutes
- Create a `.md` metadata file for every processed file
- Move originals to /Done after processing

## Always Require Human Approval For:
- Sending any email
- Any payment or financial action
- Deleting any file
- Contacting new/unknown people

## Allowed Without Approval:
- Reading and categorizing emails
- Creating summary/plan files in the vault
- Moving files between vault folders
- Updating Dashboard.md

---
*Version 1.0 — Modify these rules to match your preferences*

---

## 📱 WhatsApp Rules (Silver Tier Addition)
- Monitor messages for keywords: ["urgent", "asap", "invoice", "payment", "help", "pricing"]
- HIGH priority keyword match → immediately create an action file in /Needs_Action/
- NORMAL messages → log only, no action file created
- NEVER reply on WhatsApp without explicit human approval
- WhatsApp session credentials must stay LOCAL — never sync to cloud

## 🔗 LinkedIn Rules (Silver Tier Addition)
- Post 3 times per week: Monday, Wednesday, Friday
- Post topics: business updates, tips, client success stories (NO personal or client info)
- Tone: Professional, helpful, never salesy or promotional
- All drafted posts go to /Social/LinkedIn_Drafts/ first
- Human must move the draft to /Approved/ before any posting happens
- After a post goes live, archive it in /Social/Posted/

## 📤 Email Sending Rules (Silver Tier Addition — MCP Enabled)
- Replies to KNOWN contacts → Draft first, then require approval before sending
- Emails to NEW/UNKNOWN contacts → Always require explicit human approval with stated reason
- Bulk sends → ALWAYS blocked — never allowed under any circumstance
- Max 10 emails per hour (rate limit enforced at the MCP server level)
- Every sent email must be logged to /Logs/ with timestamp, recipient, and subject

## ⏰ Scheduling Rules (Silver Tier Addition)
- Daily Briefing task file is created at 8:00 AM every day automatically
- LinkedIn draft task runs Monday, Wednesday, Friday at 10:00 AM
- No scheduled tasks execute between 11 PM and 7 AM (quiet hours policy)
- If a scheduled task fails → log the failure in Dashboard.md, do NOT retry more than 3 times

---
*Version 2.0 — Silver Tier Rules Added*

---

## 📊 Odoo Accounting Rules (Gold Tier Addition)
- Odoo is self-hosted locally — never expose it to the public internet
- AI can READ transactions and create DRAFT invoices only
- AI can NEVER post invoices or record payments without human approval
- Every Odoo API call must be logged to /Logs/ with timestamp and action
- Invoice drafts go to /Accounting/Invoices/ for human review
- Flag any transaction over $100 as requiring human review in CEO Briefing

## 📱 Facebook + Instagram Rules (Gold Tier Addition)
- Post content must be professional and brand-appropriate
- Images or media require explicit human approval before posting
- Text-only posts: draft → /Social/Facebook_Drafts/ or /Social/Instagram_Drafts/ → approval → post
- After posting: log to /Social/Posted/ with platform, timestamp, and content preview
- Generate weekly engagement summary every Sunday → save to /Social/Social_Summaries/

## 🐦 Twitter/X Rules (Gold Tier Addition)
- Maximum 1 post per day — no spam
- Posts must be under 280 characters
- Draft → /Social/Twitter_Drafts/ → approval → post
- Replies and DMs require explicit human approval — never auto-respond
- Generate weekly Twitter summary every Sunday → include in CEO Briefing

## 📋 Weekly Audit Rules (Gold Tier Addition)
- Audit runs automatically every Sunday at 8:00 PM
- Claude reads: Business_Goals.md + all Done/ files + Accounting/Current_Month.md + all social Posted/ files
- Output: Monday Morning CEO Briefing saved to /Briefings/YYYY-MM-DD_Monday_Briefing.md
- CEO Briefing must include: revenue, completed tasks, bottlenecks, social performance, proactive suggestions
- Briefing is informational only — no actions taken without human review

## 🔄 Error Recovery Rules (Gold Tier Addition)
- Any script failure: log error to /Logs/, update Dashboard.md with ALERT, retry max 3 times
- API timeouts: exponential backoff (1s → 2s → 4s), then alert human
- Odoo connection failure: queue actions locally, never retry payments automatically
- If orchestrator crashes: watchdog restarts it within 60 seconds

## 📝 Audit Logging Rules (Gold Tier Addition)
- Every single AI action must be logged to /Logs/YYYY-MM-DD.json
- Log format: timestamp, action_type, actor, target, parameters, approval_status, result
- Logs retained for minimum 90 days
- Never log credentials, passwords, or sensitive personal data

---
*Version 3.0 — Gold Tier Rules Added*
