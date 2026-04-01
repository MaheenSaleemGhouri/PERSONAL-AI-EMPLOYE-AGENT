# create-plan

Activate Claude's reasoning loop to produce a structured Plan.md file for any multi-step task.

## Arguments

```
/create-plan [task description or filename]
```

If a filename in `/Needs_Action/` is given, load that item as the task.
If free-text is given, treat it as the task description directly.

## Instructions

When invoked:

1. **Understand the task**:
   - Read the task description or the referenced `/Needs_Action/` file.
   - Identify: goal, constraints, dependencies, risk level, required integrations.

2. **Read Company_Handbook.md** to check rules of engagement before planning any sensitive actions.

3. **Reason through the task** step by step:
   - Break the goal into discrete, ordered action steps.
   - For each step identify: what tool/integration is needed, who executes it (Claude or human), and what the success condition is.
   - Flag any step that requires human approval (financial, external communication, public posts).
   - Identify rollback or fallback if a step fails.

4. **Create a Plan.md file** in `/Plans/` named `PLAN_YYYYMMDD_<short-title>.md` with this structure:

```markdown
---
created: <ISO timestamp>
task: <one-line summary>
status: in_progress
priority: <high|medium|low>
---

## Goal
<What we are trying to achieve>

## Context
<Relevant background from the triggering item or user request>

## Action Steps

- [ ] Step 1 — <description> | executor: Claude | risk: low
- [ ] Step 2 — <description> | executor: human-approval | risk: high
- [ ] Step 3 — <description> | executor: Claude | risk: low
...

## Dependencies
<List any steps that must complete before others>

## Expected Outcome
<What success looks like>

## Rollback
<What to do if a step fails or is rejected>

## Notes
<Any additional reasoning or caveats>
```

5. **If any step requires approval**, create a corresponding file in `/Pending_Approval/` named `APPROVAL_REQUIRED_<short-title>_<step>.md` with:
   - The specific action requiring approval
   - Context and reasoning
   - What Claude will do once approved

6. **Log the plan creation** in `/Logs/YYYY-MM-DD.md`.

7. **Update Dashboard.md** to reflect the new plan.

## Rules

- Never execute high-risk steps autonomously — always gate them behind approval.
- A Plan.md is a living document: update checkboxes as steps complete.
- Mark the plan `status: done` when all steps are checked off.

## Example Usage

```
/create-plan "Onboard new client: send welcome email, create project folder, schedule kickoff call"
/create-plan WHATSAPP_20260302_invoice_request.md
```
