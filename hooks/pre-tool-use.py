#!/usr/bin/env python3
"""Dev-workflow PreToolUse hook.

Two responsibilities, both gated on the workflow state file:

1. Block ExitPlanMode while the workflow is in an early stage (< 4). Claude Code
   plan mode and the dev-workflow stage gate are different approval systems;
   approving a plan with ExitPlanMode is NOT a stage confirmation. This stops
   the model from using a plan-mode approval to skip the gated stages.

2. Block writing a design document under the project `docs/` while the workflow
   is in Stage 0 (Requirement Clarification) or Stage 1 (Software Design).
   Writing the design doc is Stage 2's job. Letting Stage 0/1 write it collapses
   the stage boundary: the model formalizes a doc before the design draft is
   reviewed, then reviews the doc instead of the draft. `docs/superpowers/` is
   exempt (superpowers plan/brainstorm archive).

Fail-open: any error, missing state, or non-matching tool lets the call through,
so this never blocks normal (non-dev-workflow) usage.
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

# Stages where writing a project design doc is premature (Stage 2 owns doc write-out).
DOC_WRITE_BLOCKED_STAGES = (0, 1)

# File-writing tools whose target path we inspect for the docs guard.
DOC_WRITE_TOOLS = ("Write", "Edit", "MultiEdit")


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


def load_stage(cwd: str | None) -> int | None:
    """Return the current dev-workflow stage, or None when not in a workflow."""
    if not cwd:
        return None
    state_file = Path(cwd) / ".claude" / "dev-workflow-state.json"
    if not state_file.exists():
        return None
    try:
        state = json.loads(state_file.read_text())
        return int(state.get("stage", 0))
    except Exception:
        return None


def check_exit_plan_mode(stage: int) -> int:
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


def check_doc_write(stage: int, cwd: str, tool_input: dict) -> int:
    if stage not in DOC_WRITE_BLOCKED_STAGES:
        return allow()
    file_path = tool_input.get("file_path")
    if not file_path:
        return allow()
    try:
        target = Path(file_path)
        if not target.is_absolute():
            target = Path(cwd) / target
        target = target.resolve()
        docs_root = (Path(cwd) / "docs").resolve()
        superpowers_root = docs_root / "superpowers"
        in_docs = target == docs_root or docs_root in target.parents
        in_superpowers = target == superpowers_root or superpowers_root in target.parents
    except Exception:
        return allow()

    if not (in_docs and not in_superpowers):
        return allow()

    stage_name = STAGE_NAMES.get(stage, "Unknown")
    return deny(
        f"dev-workflow is at Stage {stage} ({stage_name}). Writing a design document under "
        f"the project `docs/` is Stage 2's (Design Documentation) job. In Stage 0 only clarify "
        f"requirements; in Stage 1 only produce and review the DESIGN DRAFT — design-reviewer "
        f"reviews the draft itself, not a doc. Pass the current stage Gate (with user "
        f"confirmation) and advance to Stage 2 before writing the doc. (`docs/superpowers/` is exempt.)"
    )


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except Exception:
        return allow()

    tool_name = payload.get("tool_name")
    cwd = payload.get("cwd")

    stage = load_stage(cwd)
    if stage is None:
        return allow()

    if tool_name == "ExitPlanMode":
        return check_exit_plan_mode(stage)
    if tool_name in DOC_WRITE_TOOLS:
        return check_doc_write(stage, cwd, payload.get("tool_input") or {})
    return allow()


if __name__ == "__main__":
    raise SystemExit(main())
