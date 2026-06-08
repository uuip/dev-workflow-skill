#!/usr/bin/env python3
"""Dev-workflow UserPromptSubmit hook.

Reads the workflow state file and:
- Injects the current stage info into every prompt
- Blocks implementation prompts when stage < 5
- Reminds that completion claims require Stage 8
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

CODING_KEYWORDS = [
    "开始编码",
    "写代码",
    "实现",
    "直接开发",
    "直接实现",
    "start coding",
    "implement",
]

COMPLETION_KEYWORDS = [
    "完成了",
    "done",
    "complete",
]


def find_state_file() -> Path | None:
    cwd = Path.cwd()
    path = cwd / ".claude" / "dev-workflow-state.json"
    if path.exists():
        return path
    return None


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except Exception:
        return 0

    prompt = payload.get("prompt", "")
    if not isinstance(prompt, str):
        return 0

    text = prompt.lower()
    mentions_workflow = "/dev-workflow" in text or "dev-workflow" in text

    state_file = find_state_file()
    state = None
    if state_file:
        try:
            state = json.loads(state_file.read_text())
        except Exception:
            pass

    if state is not None:
        stage = state.get("stage", 0)
        stage_name = STAGE_NAMES.get(stage, "Unknown")

        has_coding_keyword = any(kw in text for kw in CODING_KEYWORDS)
        has_completion_keyword = any(kw in text for kw in COMPLETION_KEYWORDS)

        if stage < 5 and has_coding_keyword and not mentions_workflow:
            print(
                f"BLOCKED: Current stage is {stage} ({stage_name}). "
                f"Implementation is not allowed until Stage 5 (TDD Implementation). "
                f"Stage 4 must first produce the pre-coding confirmation and pass its Gate. "
                f"Complete the current stage Gate first."
            )
            return 1

        if stage < 8 and has_completion_keyword and not mentions_workflow:
            print(
                f"REMINDER: Current stage is {stage} ({stage_name}). "
                f"Completion claims require Stage 8 (Completion Verification). "
                f"Do not skip stages."
            )
            return 0

        reminder = (
            f"Dev Workflow State: Stage {stage} — {stage_name}.\n"
            f"Read the dev-workflow skill and references/workflow.md. "
            f"Execute only actions allowed by Stage {stage}. Do not skip Gates.\n"
            f"Use `python3 \"${{CLAUDE_PLUGIN_ROOT}}/hooks/advance.py\" --to <stage> --reason \"<gate evidence>\"` "
            f"to advance after Gate passes. Add `--confirmation \"<user confirmation text>\"` before Stage 3."
        )
        print(reminder)
        return 0

    if not mentions_workflow:
        risky_transition = any(
            token in text
            for token in CODING_KEYWORDS + COMPLETION_KEYWORDS + ["跳过"]
        )
        if not risky_transition:
            return 0

    reminder = (
        "Dev Workflow Gate Reminder:\n"
        "On Claude Code, enter plan mode now (EnterPlanMode) before starting — "
        "Stages 0-3 are read-only and plan mode matches them. Do not use ExitPlanMode to skip stages.\n"
        "Read the dev-workflow skill and references/workflow.md first. "
        "Identify the current stage, load only that stage reference, and do not skip Gates. "
        "Before coding, requirement clarification, design, design docs, and task planning must pass. "
        "Human confirmation is required only before Stage 3. "
        "Before completion claims, use superpowers:verification-before-completion."
    )
    print(reminder)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
