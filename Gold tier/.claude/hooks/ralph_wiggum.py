"""
ralph_wiggum.py — Ralph Wiggum Stop Hook for AI Employee (Gold Tier)

A "stop hook" that intercepts Claude Code's exit and feeds the prompt back
if the task is not yet complete. This keeps the AI Employee working autonomously
until multi-step tasks are finished.

Completion Strategies:
  1. Promise-based: Claude outputs <promise>TASK_COMPLETE</promise>
  2. File-movement: Task file has been moved to /Done/

Usage (in .claude/settings.json hooks):
    {
      "hooks": {
        "Stop": [
          {
            "command": "python .claude/hooks/ralph_wiggum.py \"${prompt}\" --vault AI_Employee_Vault --max-iterations 10"
          }
        ]
      }
    }

Or invoke manually via the skill:
    /ralph-loop "Process all Needs_Action items" --max-iterations 10
"""

import argparse
import json
import logging
import sys
import time
from datetime import datetime
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [RALPH] %(message)s",
)
logger = logging.getLogger("RalphWiggum")

STATE_FILE = ".ralph_wiggum_state.json"


def load_state(vault_path: Path) -> dict:
    state_file = vault_path / STATE_FILE
    if state_file.exists():
        return json.loads(state_file.read_text(encoding="utf-8"))
    return {}


def save_state(vault_path: Path, state: dict):
    state_file = vault_path / STATE_FILE
    state_file.write_text(json.dumps(state, indent=2), encoding="utf-8")


def check_promise_completion(output: str) -> bool:
    """Check if Claude output contains the TASK_COMPLETE promise."""
    return "<promise>TASK_COMPLETE</promise>" in output or "TASK_COMPLETE" in output


def check_file_completion(vault_path: Path, task_file: str) -> bool:
    """Check if the task file has been moved to /Done/."""
    done_path = vault_path / "Done" / task_file
    original_path = vault_path / "Needs_Action" / task_file
    return done_path.exists() and not original_path.exists()


def check_needs_action_empty(vault_path: Path) -> bool:
    """Check if /Needs_Action/ is empty (all items processed)."""
    needs_action = vault_path / "Needs_Action"
    if not needs_action.exists():
        return True
    items = [f for f in needs_action.iterdir() if f.suffix == ".md"]
    return len(items) == 0


def ralph_wiggum_check(
    prompt: str,
    vault_path: str,
    max_iterations: int = 10,
    completion_mode: str = "promise",
    task_file: str = "",
    claude_output: str = "",
) -> dict:
    """
    Main Ralph Wiggum logic.

    Returns:
        dict with keys:
            - should_continue (bool): True if Claude should keep going
            - iteration (int): Current iteration number
            - reason (str): Why continuing or stopping
            - prompt (str): The prompt to re-inject (if continuing)
    """
    vault = Path(vault_path)
    state = load_state(vault)

    iteration = state.get("iteration", 0) + 1
    original_prompt = state.get("original_prompt", prompt)

    # Check max iterations
    if iteration > max_iterations:
        logger.info(f"Max iterations ({max_iterations}) reached. Stopping.")
        save_state(vault, {})  # Clear state
        return {
            "should_continue": False,
            "iteration": iteration,
            "reason": f"Max iterations ({max_iterations}) reached",
            "prompt": "",
        }

    # Check completion
    is_complete = False
    reason = ""

    if completion_mode == "promise":
        is_complete = check_promise_completion(claude_output)
        reason = "TASK_COMPLETE promise found" if is_complete else "No completion promise"
    elif completion_mode == "file":
        if task_file:
            is_complete = check_file_completion(vault, task_file)
            reason = f"Task file '{task_file}' moved to /Done/" if is_complete else f"Task file '{task_file}' not yet in /Done/"
        else:
            is_complete = check_needs_action_empty(vault)
            reason = "/Needs_Action/ is empty" if is_complete else "/Needs_Action/ still has items"
    elif completion_mode == "auto":
        # Try both strategies
        if check_promise_completion(claude_output):
            is_complete = True
            reason = "TASK_COMPLETE promise found"
        elif check_needs_action_empty(vault):
            is_complete = True
            reason = "/Needs_Action/ is empty"

    if is_complete:
        logger.info(f"Task complete at iteration {iteration}. Reason: {reason}")
        # Log completion
        log_ralph_event(vault, "COMPLETE", iteration, reason)
        save_state(vault, {})  # Clear state
        return {
            "should_continue": False,
            "iteration": iteration,
            "reason": reason,
            "prompt": "",
        }

    # Not complete — continue
    logger.info(f"Iteration {iteration}/{max_iterations}. {reason}. Continuing...")

    # Save state for next iteration
    save_state(vault, {
        "original_prompt": original_prompt,
        "iteration": iteration,
        "started_at": state.get("started_at", datetime.now().isoformat()),
        "last_check": datetime.now().isoformat(),
        "completion_mode": completion_mode,
        "task_file": task_file,
    })

    # Build the re-injection prompt
    continuation_prompt = (
        f"[Ralph Wiggum — Iteration {iteration}/{max_iterations}]\n"
        f"Task is NOT complete. {reason}.\n"
        f"Continue working on: {original_prompt}\n"
        f"Check /Needs_Action/ for remaining items. "
        f"When done, output <promise>TASK_COMPLETE</promise>."
    )

    log_ralph_event(vault, "CONTINUE", iteration, reason)

    return {
        "should_continue": True,
        "iteration": iteration,
        "reason": reason,
        "prompt": continuation_prompt,
    }


def log_ralph_event(vault: Path, event: str, iteration: int, reason: str):
    """Append to the daily log."""
    log_dir = vault / "Logs"
    log_dir.mkdir(exist_ok=True)
    log_file = log_dir / f"{datetime.now().strftime('%Y-%m-%d')}.md"
    entry = f"[{datetime.now().strftime('%H:%M:%S')}] [RALPH_WIGGUM] {event} — iteration {iteration}: {reason}\n"
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(entry)


# ── CLI entry point ──────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Ralph Wiggum Stop Hook")
    parser.add_argument("prompt", nargs="?", default="", help="The original task prompt")
    parser.add_argument("--vault", default="AI_Employee_Vault")
    parser.add_argument("--max-iterations", type=int, default=10)
    parser.add_argument("--mode", choices=["promise", "file", "auto"], default="auto")
    parser.add_argument("--task-file", default="", help="Specific task file to track")
    parser.add_argument("--output", default="", help="Claude's last output (for promise check)")
    parser.add_argument("--status", action="store_true", help="Show current Ralph state")
    args = parser.parse_args()

    vault = Path(args.vault)

    if args.status:
        state = load_state(vault)
        if state:
            print(json.dumps(state, indent=2))
        else:
            print("No active Ralph Wiggum loop.")
        return

    result = ralph_wiggum_check(
        prompt=args.prompt,
        vault_path=args.vault,
        max_iterations=args.max_iterations,
        completion_mode=args.mode,
        task_file=args.task_file,
        claude_output=args.output,
    )

    # Output result as JSON for the hook to consume
    print(json.dumps(result, indent=2))

    # Exit code: 0 = continue (block exit), 1 = complete (allow exit)
    sys.exit(0 if result["should_continue"] else 1)


if __name__ == "__main__":
    main()
