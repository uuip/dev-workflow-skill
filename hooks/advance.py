#!/usr/bin/env python3
"""Dev-workflow stage advancement script.

Manages the workflow state file at <project>/.claude/dev-workflow-state.json.
"""

import argparse
import json
import sys
from datetime import datetime, timezone
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

VALID_FALLBACKS = {
    0: set(),
    1: {0},
    2: {1},
    3: {2},
    4: {3, 1, 2},
    5: {4, 3},
    6: {5, 4, 3},
    7: {6, 5, 3, 1},
    8: {6, 5, 7, 2, 3},
}

HUMAN_CONFIRMATION_TRANSITIONS = {
    (0, 1): "enter_design",
    (1, 2): "design_approved",
    (2, 3): "design_docs_accepted_for_planning",
}

# Confirmation text must be the user's own words. These phrases signal the model
# invented the confirmation from a plan-mode approval instead of asking the user.
INVENTED_CONFIRMATION_MARKERS = (
    "exitplanmode",
    "approved plan with",
    "plan mode",
    "计划模式",
    "退出计划",
)


def looks_invented(confirmation: str) -> bool:
    text = confirmation.lower()
    return any(marker in text for marker in INVENTED_CONFIRMATION_MARKERS)


def state_path(project_dir: Path) -> Path:
    return project_dir / ".claude" / "dev-workflow-state.json"


def read_state(path: Path) -> dict | None:
    if not path.exists():
        return None
    return json.loads(path.read_text())


def write_state(path: Path, state: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(state, indent=2, ensure_ascii=False) + "\n")


def now_iso() -> str:
    return datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")


def cmd_init(project_dir: Path) -> int:
    path = state_path(project_dir)
    if path.exists():
        state = read_state(path)
        if state is None:
            print(f"State file already exists but could not be read: {path}", file=sys.stderr)
            return 1
        stage = state.get("stage", 0)
        print(f"State file already exists: Stage {stage}: {STAGE_NAMES.get(stage, 'Unknown')}")
        return 0
    state = {
        "stage": 0,
        "started_at": now_iso(),
        "confirmations": {},
        "gate_evidence": {},
        "history": [],
    }
    write_state(path, state)
    print(f"Initialized at Stage 0: {STAGE_NAMES[0]}")
    return 0


def cmd_to(project_dir: Path, target: int, reason: str | None, confirmation: str | None) -> int:
    path = state_path(project_dir)
    state = read_state(path)
    if state is None:
        if target == 0:
            return cmd_init(project_dir)
        if target != 1:
            print("No state file found. Run with --init first, or advance to Stage 1 from a new workflow.", file=sys.stderr)
            return 1
        state = {
            "stage": 0,
            "started_at": now_iso(),
            "confirmations": {},
            "gate_evidence": {},
            "history": [],
        }

    current = state["stage"]
    state.setdefault("confirmations", {})
    state.setdefault("gate_evidence", {})

    if target == current:
        print(f"Already at Stage {current}: {STAGE_NAMES[current]}")
        return 0

    max_stage = max(STAGE_NAMES)
    if target < 0 or target > max_stage:
        print(f"Invalid stage: {target}. Must be 0-{max_stage}.", file=sys.stderr)
        return 1

    if not reason:
        print(
            "Gate evidence or fallback reason is required. Pass --reason with the evidence or reason.",
            file=sys.stderr,
        )
        return 1

    if target == current + 1:
        confirmation_key = HUMAN_CONFIRMATION_TRANSITIONS.get((current, target))
        if confirmation_key and not confirmation:
            print(
                f"Human confirmation is required to advance from Stage {current} to Stage {target}. "
                f"STOP. Do NOT retry by inventing confirmation text. Ask the user to confirm the "
                f"Gate, then pass their exact words via --confirmation (and --reason with the Gate evidence).",
                file=sys.stderr,
            )
            return 1
        if confirmation_key and confirmation and looks_invented(confirmation):
            print(
                "Refused: --confirmation must be the user's real answer, not a plan-mode approval. "
                "A stage Gate before Stage 3 is confirmed by the user, not by ExitPlanMode. "
                "Ask the user and pass their exact words.",
                file=sys.stderr,
            )
            return 1
        pass  # forward by 1 is always valid
    elif target < current and target in VALID_FALLBACKS.get(current, set()):
        pass  # valid fallback
    else:
        if target > current:
            print(
                f"Cannot jump from Stage {current} to Stage {target}. Only +1 forward allowed.",
                file=sys.stderr,
            )
        else:
            allowed = sorted(VALID_FALLBACKS.get(current, set()))
            print(
                f"Cannot fall back from Stage {current} to Stage {target}. "
                f"Allowed fallbacks: {allowed}",
                file=sys.stderr,
            )
        return 1

    entry = {"from": current, "to": target, "at": now_iso()}
    if reason:
        entry["reason"] = reason
    if confirmation:
        entry["confirmation"] = confirmation
    confirmation_key = HUMAN_CONFIRMATION_TRANSITIONS.get((current, target))
    if confirmation_key:
        state["confirmations"][confirmation_key] = {
            "at": entry["at"],
            "stage": current,
            "text": confirmation,
        }
    if reason:
        state["gate_evidence"][str(current)] = {
            "at": entry["at"],
            "result": "passed",
            "evidence": reason,
        }
    state["history"].append(entry)
    state["stage"] = target
    state["started_at"] = now_iso()
    write_state(path, state)

    direction = "Advanced" if target > current else "Fell back"
    print(f"{direction} to Stage {target}: {STAGE_NAMES[target]}")
    return 0


def cmd_reset(project_dir: Path) -> int:
    path = state_path(project_dir)
    if path.exists():
        path.unlink()
        print("State file removed.")
    else:
        print("No state file to remove.")
    return 0


def cmd_show(project_dir: Path) -> int:
    path = state_path(project_dir)
    state = read_state(path)
    if state is None:
        print("No active workflow.")
        return 0
    stage = state["stage"]
    print(f"Stage {stage}: {STAGE_NAMES[stage]}")
    print(f"Since: {state['started_at']}")
    if state["history"]:
        print(f"Transitions: {len(state['history'])}")
        last = state["history"][-1]
        print(f"Last: Stage {last['from']} -> Stage {last['to']} at {last['at']}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Dev-workflow state manager")
    parser.add_argument("--project-dir", type=Path, default=Path.cwd())

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--init", action="store_true", help="Initialize at Stage 0")
    group.add_argument("--to", type=int, metavar="STAGE", help="Advance/fallback to stage")
    group.add_argument("--reset", action="store_true", help="Remove state file")
    group.add_argument("--show", action="store_true", help="Show current state")

    parser.add_argument("--reason", type=str, help="Reason for transition")
    parser.add_argument("--confirmation", type=str, help="User confirmation text for Stage 0-2 forward transitions")

    args = parser.parse_args()

    if args.init:
        return cmd_init(args.project_dir)
    elif args.to is not None:
        return cmd_to(args.project_dir, args.to, args.reason, args.confirmation)
    elif args.reset:
        return cmd_reset(args.project_dir)
    elif args.show:
        return cmd_show(args.project_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
