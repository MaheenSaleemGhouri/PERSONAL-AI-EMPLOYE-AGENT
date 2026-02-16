---
skill_name: ceo-briefing
version: 1.0
tier: gold
trigger: SCHEDULED_WeeklyAudit_*.md in /Needs_Action/
---

# Skill: Monday Morning CEO Briefing Generator

## Purpose
Autonomously audit the week's activity and generate a comprehensive CEO Briefing report.

## Input
- Weekly audit task file in /Needs_Action/
- Business_Goals.md for targets
- /Done/ files from this week
- /Accounting/Current_Month.md
- /Social/Social_Summaries/ for this week
- /Logs/ for this week

## Steps
Follow /Audit/Weekly_Audit_Template.md exactly, then:

1. Read Business_Goals.md — extract monthly targets and alert thresholds
2. Count and categorize all /Done/ files created this week
3. Read Accounting/Current_Month.md — extract revenue, expenses, flagged transactions
4. Read this week's social summary from /Social/Social_Summaries/
5. Read /Logs/ — count total actions, errors, alerts
6. Check /Pending_Approval/ for overdue items (>24 hours)
7. Identify bottlenecks (tasks that created multiple action files or failed)
8. Generate proactive suggestions (max 3 — cost savings, missed opportunities, upcoming risks)
9. Save complete briefing to:
   /Briefings/YYYY-MM-DD_Monday_Briefing.md
10. Update Dashboard.md Gold section
11. Log the audit via audit_logger
12. Move task file to /Done/

## CEO Briefing Output Format

```markdown
# Monday Morning CEO Briefing — [Date]

## Executive Summary
[3 sentences max — overall week summary]

## Revenue
- This Week: $X
- MTD: $X (X% of $Y target)
- Trend: On track / Behind / Ahead

## Completed Tasks
[List of completed tasks by category]

## Bottlenecks
[Table of delayed/failed tasks]

## Social Performance
[Posts per platform this week]

## Subscription Audit
[Any subscriptions flagged per Business_Goals.md rules]

## Proactive Suggestions
1. [Suggestion 1]
2. [Suggestion 2]
3. [Suggestion 3]

## Upcoming Deadlines
[Next 7 days]
```
