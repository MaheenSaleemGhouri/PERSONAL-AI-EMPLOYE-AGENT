# ralph-loop

Start a Ralph Wiggum autonomous loop that keeps Claude working until a task is complete.

## Arguments

```
/ralph-loop "<task description>" [--mode promise|file|auto] [--max-iterations N] [--task-file <filename>]
```

- `task description`: What Claude should accomplish.
- `--mode`: Completion detection strategy (default: `auto`).
  - `promise`: Claude outputs `<promise>TASK_COMPLETE</promise>` when done.
  - `file`: Tracks when a specific task file moves to `/Done/`.
  - `auto`: Uses both strategies (first to trigger wins).
- `--max-iterations`: Safety limit (default: 10).
- `--task-file`: Specific file in `/Needs_Action/` to track (for `file` mode).

## Instructions

When invoked:

1. **Parse arguments** and validate inputs.

2. **Initialize the Ralph Wiggum state** by writing `.ralph_wiggum_state.json` in the vault:
   ```json
   {
     "original_prompt": "<task description>",
     "iteration": 0,
     "started_at": "<ISO timestamp>",
     "completion_mode": "<mode>",
     "task_file": "<filename or empty>",
     "max_iterations": <N>
   }
   ```

3. **Begin working on the task**:
   - Read `/Needs_Action/` for pending items.
   - Process items according to the task description.
   - Use appropriate skills (process-inbox, process-gmail, process-facebook, etc.).

4. **After each processing cycle**, check completion:
   - If `auto` mode: check both `/Needs_Action/` empty AND for `TASK_COMPLETE` in output.
   - If task is NOT complete: log the iteration, continue to next cycle.
   - If task IS complete: output `<promise>TASK_COMPLETE</promise>`, clean up state.

5. **On completion or max iterations**:
   - Log final status to `/Logs/YYYY-MM-DD.md`.
   - Clean up `.ralph_wiggum_state.json`.
   - Update Dashboard.md.

## Example Usage

```
/ralph-loop "Process all items in /Needs_Action and move to /Done" --max-iterations 10
/ralph-loop "Triage all emails and draft replies" --mode auto --max-iterations 5
/ralph-loop "Complete invoice processing" --mode file --task-file "EMAIL_abc123.md"
```

## Rules

- Always respect max-iterations as a hard safety limit.
- Log every iteration to the audit log.
- If an error occurs mid-loop, log it and continue to the next item (graceful degradation).
- Never loop infinitely — the max-iterations guard must always be enforced.
