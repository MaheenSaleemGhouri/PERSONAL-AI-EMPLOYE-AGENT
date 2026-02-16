---
skill_name: plan-creator
version: 1.0
tier: silver
trigger: Any complex task that requires 3 or more steps, or involves multiple systems
---

# Skill: Plan Creator (Reasoning Loop)

## Purpose
Create a structured Plan.md file BEFORE taking any action on complex tasks.

## When to Use
- The task requires 3 or more distinct steps
- Multiple systems are involved (e.g., email + file system + dashboard update)
- An MCP call will be needed
- There is ambiguity about how to proceed — plan first, then ask

## Plan File Location
Save all plans to: `/Plans/PLAN_<task_name>_<timestamp>.md`

## Plan Template
```markdown
---
plan_id: PLAN_<task>_<timestamp>
created: <iso_timestamp>
status: in_progress
---

# Plan: <Task Description in One Line>

## Objective
<What needs to be accomplished — one clear sentence>

## Steps
- [ ] Step 1: <specific, concrete action>
- [ ] Step 2: <specific, concrete action>
- [ ] Step 3: <specific, concrete action>

## Approvals Required
- [ ] <What action requires human approval before proceeding>

## Completion Criteria
Task is complete when: <specific and measurable condition>
```

## Execution Rules
- Always create the Plan file FIRST — never execute before planning
- Check off each step as it is completed
- Set `status: complete` in frontmatter when all steps are done
- Move the Plan file to /Done/ once all checkboxes are ticked
- If a step fails, update the plan with a failure note before stopping
