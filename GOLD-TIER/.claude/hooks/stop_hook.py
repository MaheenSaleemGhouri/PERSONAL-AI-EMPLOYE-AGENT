# .claude/hooks/stop_hook.py — Ralph Wiggum Stop Hook
# Prevents Claude from exiting until the task completion signal is found

import sys
import os
from pathlib import Path

VAULT_PATH = Path(os.getenv('VAULT_PATH', './AI_Employee_Vault'))
PROMISE_SIGNAL = os.getenv('RALPH_PROMISE', 'TASK_COMPLETE')
MAX_ITERATIONS = int(os.getenv('RALPH_MAX_ITERATIONS', '10'))

# Read current iteration count from state file
state_file = Path('/tmp/ralph_state.txt')
iteration = 0
if state_file.exists():
    try:
        iteration = int(state_file.read_text().strip())
    except ValueError:
        iteration = 0

iteration += 1
state_file.write_text(str(iteration))

# Check if max iterations reached
if iteration >= MAX_ITERATIONS:
    print(f"Ralph Wiggum: Max iterations ({MAX_ITERATIONS}) reached — allowing exit")
    state_file.unlink(missing_ok=True)
    sys.exit(0)  # Allow exit

# Check if completion signal was output by Claude
claude_output = sys.stdin.read() if not sys.stdin.isatty() else ""
if PROMISE_SIGNAL in claude_output:
    print(f"Ralph Wiggum: Completion signal found — task complete (iteration {iteration})")
    state_file.unlink(missing_ok=True)
    sys.exit(0)  # Allow exit

# Task not complete — block exit and re-inject
print(f"Ralph Wiggum: Task incomplete (iteration {iteration}/{MAX_ITERATIONS}) — continuing...")
sys.exit(1)  # Block exit, Claude will re-run
