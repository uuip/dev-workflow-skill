#!/usr/bin/env python3
"""Dev-workflow PreToolUse hook.

Blocks ExitPlanMode while the workflow is in an early stage (< 4).

Claude Code plan mode and the dev-workflow stage gate are two different
approval systems. Approving a plan with ExitPlanMode is NOT a stage
confirmation. This hook stops the model from using a plan-mode approval to
skip the gated stages (requirement clarification, design, design docs,
implementation plan).

Fail-open: any error, missing state, or non-matching tool lets the call
through, so this never blocks normal (non-dev-workflow) usage.
"""

import json
import sys
from pathlib import Path

STAGE_NAMES = {
    0: "Requirement Clarification",
    1: "Software Design",
    2: "Design Documentation",
    3: "Implementation Plan",
    4: "Pre-Coding Confirmation",
    5: "TDD Implementation",
    6: "Integration Testing",
    7: "Code Review",
    8: "Completion Verification",
}

# Plan mode may legitimately exit to implementation only from Stage 4 onward.
ALLOW_EXIT_FROM_STAGE = 4


def allow() -> int:
    return 0


def deny(reason: str) -> int:
    print(
        json.dumps(
            {
                "hookSpecificOutput": {
                    "hookEventName": "PreToolUse",
                    "permissionDecision": "deny",
                    "permissionDecisionReason": reason,
                }
            }
        )
    )
    return 0


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except Exception:
        return allow()

    if payload.get("tool_name") != "ExitPlanMode":
        return allow()

    cwd = payload.get("cwd")
    if not cwd:
        return allow()

    state_file = Path(cwd) / ".claude" / "dev-workflow-state.json"
    if not state_file.exists():
        return allow()

    try:
        state = json.loads(state_file.read_text())
        stage = int(state.get("stage", 0))
    except Exception:
        return allow()

    if stage >= ALLOW_EXIT_FROM_STAGE:
        return allow()

    stage_name = STAGE_NAMES.get(stage, "Unknown")
    return deny(
        f"dev-workflow is at Stage {stage} ({stage_name}). ExitPlanMode is NOT a stage "
        f"confirmation. Do not use plan mode to skip stages. State the gate evidence, ask "
        f"the user to confirm, then advance with "
        f"`advance.py --to <stage> --reason \"<evidence>\" --confirmation \"<user's exact words>\"`. "
        f"Plan-mode exit to implementation is only appropriate from Stage {ALLOW_EXIT_FROM_STAGE}."
    )


if __name__ == "__main__":
    raise SystemExit(main())
