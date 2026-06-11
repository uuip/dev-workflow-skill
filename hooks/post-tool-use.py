#!/usr/bin/env python3
"""Dev-workflow PostToolUse hook.

Records mechanical evidence during the implementation/test stages (Stage 5/6) so
the 6->7 advance gate cannot be passed by merely claiming the work was done:

- frontend_touched: a frontend source file was created/edited (Write/Edit/MultiEdit
  on a .tsx/.vue/.css/... path). Means the change has a UI surface.
- ui_verified: a real playwright-cli browser run happened (Bash command containing
  `playwright-cli`, or an `mcp__playwright__*` tool). Means UI verification ran.

`advance.py` reads these from state["impl_evidence"] when advancing Stage 6 -> 7.

Fail-open: any error, missing state, wrong stage, or non-matching tool is a no-op.
This hook never blocks (PostToolUse runs after the tool); it only annotates state.
"""

import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

# Evidence is only meaningful during implementation (Stage 5) and integration
# testing (Stage 6). Frontend edits usually happen in Stage 5; UI verification in
# Stage 6. Both stages are accepted so a real playwright run in either counts.
EVIDENCE_STAGES = (5, 6)

FRONTEND_SUFFIXES = (
    ".tsx", ".jsx", ".vue", ".svelte",
    ".css", ".scss", ".sass", ".less",
    ".html", ".htm", ".astro",
)

WRITE_TOOLS = ("Write", "Edit", "MultiEdit")

# um-login uses compound commands like `... && playwright-cli fill ...`, so match
# the binary anywhere in the command, not just at the start.
PLAYWRIGHT_CLI_RE = re.compile(r"playwright-cli\b")


def now_iso() -> str:
    return datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except Exception:
        return 0

    cwd = payload.get("cwd")
    if not cwd:
        return 0

    state_file = Path(cwd) / ".claude" / "dev-workflow-state.json"
    if not state_file.exists():
        return 0

    try:
        state = json.loads(state_file.read_text())
        stage = int(state.get("stage", 0))
    except Exception:
        return 0

    if stage not in EVIDENCE_STAGES:
        return 0

    tool_name = payload.get("tool_name", "")
    tool_input = payload.get("tool_input") or {}

    evidence_key = None
    detail = {}

    if tool_name in WRITE_TOOLS:
        file_path = tool_input.get("file_path")
        if file_path and Path(file_path).suffix.lower() in FRONTEND_SUFFIXES:
            evidence_key = "frontend_touched"
            detail = {"last_file": file_path}
    elif tool_name == "Bash":
        if PLAYWRIGHT_CLI_RE.search(tool_input.get("command", "")):
            evidence_key = "ui_verified"
    elif tool_name.startswith("mcp__playwright__"):
        evidence_key = "ui_verified"

    if not evidence_key:
        return 0

    try:
        impl = state.get("impl_evidence")
        if not isinstance(impl, dict):
            impl = {}
        entry = {"at": now_iso(), "stage": stage}
        entry.update(detail)
        impl[evidence_key] = entry
        state["impl_evidence"] = impl
        state_file.write_text(json.dumps(state, indent=2, ensure_ascii=False) + "\n")
    except Exception:
        return 0

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
