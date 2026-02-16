---
skill_name: whatsapp-monitor
version: 1.0
tier: silver
trigger: WHATSAPP_*.md file appears in /Needs_Action/
---

# Skill: WhatsApp Message Monitor

## Purpose
Triage urgent WhatsApp messages and draft appropriate replies for human approval.

## Input
A file named `WHATSAPP_*.md` in `/Needs_Action/`

## Steps
1. Read sender name, matched keywords, and message preview from the file
2. Check Company_Handbook.md WhatsApp Rules for guidance
3. Draft an appropriate reply based on the keyword type:
   - "invoice" / "payment" → Draft a payment status update reply
   - "pricing" / "quote" → Draft a general pricing inquiry response (no actual numbers without approval)
   - "urgent" / "help" → Draft a warm, fast acknowledgment reply
4. Save the draft reply to: `/Plans/WHATSAPP_REPLY_<timestamp>.md`
5. Create an approval request at: `/Pending_Approval/WHATSAPP_<timestamp>.md`
6. Update the Dashboard.md WhatsApp section (messages today + 1)
7. Move the original action file to /Done/

## Hard Rules
- NEVER auto-reply on WhatsApp under any circumstances
- NEVER include actual pricing in drafts without explicit human approval
- Always maintain a warm, professional tone in all drafted replies
