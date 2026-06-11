---
name: workflow
description: Use when the user invokes /dev-workflow:workflow, asks to run a software development workflow from a raw requirement, or wants a gated pipeline for requirement clarification, design, docs, task planning, coding, integration testing, review, and verification.
---

# Dev Workflow

Run the user's software development workflow as a gated pipeline.

## State Management

State file: `<project>/.claude/dev-workflow-state.json`

Commands:
- Initialize: `python3 "${CLAUDE_PLUGIN_ROOT}/hooks/advance.py" --init`
- Advance: `python3 "${CLAUDE_PLUGIN_ROOT}/hooks/advance.py" --to <stage> --reason "<gate evidence>"`
- Advance before Stage 3: `python3 "${CLAUDE_PLUGIN_ROOT}/hooks/advance.py" --to <stage> --reason "<gate evidence>" --confirmation "<user confirmation text>"`
- Show: `python3 "${CLAUDE_PLUGIN_ROOT}/hooks/advance.py" --show`
- Reset: `python3 "${CLAUDE_PLUGIN_ROOT}/hooks/advance.py" --reset`

Rules:
- On workflow start, run `--init` to create or reuse the state file at Stage 0.
- If `--to 1` is called before the state file exists, the state script may initialize Stage 0 but still requires `--reason` and `--confirmation`.
- Before Stage 3, after a Gate passes AND the user confirms, run `--to <next_stage> --reason "<gate evidence>" --confirmation "<user confirmation text>"` to advance.
- From Stage 3 onward, run `--to <next_stage> --reason "<gate evidence>"` when the Gate passes; do not require extra human confirmation unless the stage is blocked, asks for missing external input, or the user explicitly requests a pause.
- On fallback, run `--to <fallback_stage> --reason "<why>"`.
- On workflow completion (Stage 8 Gate passes), run `--reset`.
- Never advance from Stage 0, Stage 1, or Stage 2 without user confirmation.

## Start

On Claude Code, when this workflow begins (a new dev-workflow run, before or right after `--init`),
call EnterPlanMode immediately. Stages 0-3 are read-only (clarify, design, plan); plan mode matches them.
Do not call ExitPlanMode to skip stages — advance only via `advance.py` (see Plan Mode vs Dev-Workflow Stages).

Always begin by reading `references/workflow.md`.

Then:
1. Run `advance.py --show` to check current state. If no state file exists and this is a new workflow, run `--init`.
2. Load only the reference file for the current stage.
3. Execute only the actions allowed by that stage.
4. Stop if required inputs are missing and state exactly what is missing.
5. If the user has said required documents, files, credentials, API keys, accounts, or other external resources will be provided, do not skip that dependency; wait for the user or record it as unverified only with explicit user approval.
6. Before Stage 3, do not advance until the stage Gate passes and required human confirmation is recorded with `--confirmation`.
7. From Stage 3 onward, advance with `--reason "<gate evidence>"` when the stage Gate passes; do not require extra human confirmation unless the stage is blocked, asks for missing external input, or the user explicitly requests a pause.

## Platform Support

- Reviewer agents are configured by exact name: `design-reviewer`, `verification-reviewer`.
- Use the named reviewer agent at the stages specified in `references/workflow.md` when this runtime supports agent delegation.
- Claude Code has a `UserPromptSubmit` hook configured that injects a workflow Gate reminder for `/dev-workflow:workflow` and risky stage-transition prompts.
- Claude Code has a `PreToolUse` hook that, while in Stage 0 or Stage 1, denies writing a design document under the project `docs/` (except `docs/superpowers/`). Design-doc write-out is Stage 2's job; this hard-stops the Stage 1 -> Stage 2 boundary from collapsing.

## Invocation

Treat any of these as invocation:
- `/dev-workflow:workflow <requirement>`
- "dev-workflow 我的需求..."
- A request to start the workflow from a raw feature description
- A request to continue this workflow from existing artifacts

If the user includes a raw requirement with `/dev-workflow:workflow`, initialize or continue the workflow at Stage 0 unless the state file already shows a later approved stage. Do not skip requirement clarification, design, or human confirmation.

## References

- `references/workflow.md` - pipeline state machine and Gates
- `references/requirements.md` - requirement material and first clarification prompt
- `references/design-1.md` - software design
- `references/design-docs.md` - write confirmed design to project docs
- `references/design-2.md` - implementation plan and task breakdown
- `references/coding-plan.md` - pre-coding confirmation
- `references/tdd-implementation.md` - TDD implementation
- `references/integration-testing.md` - full business-flow integration testing with real infrastructure
- `references/review.md` - code quality review prompt
- `references/verification.md` - completion verification prompt

## Human Confirmation Gates

Require explicit user confirmation before:
- Accepting requirement assumptions that affect behavior
- Entering software design
- Treating the design as approved

Before requesting the Stage 0->1 confirmation, the model must self-check and state that Stage 0 only clarified requirements and produced no solution, UI, interface, or data design; design work belongs to Stage 1.

From Stage 3 onward, human confirmation is not required for forward stage advancement. Gates still require evidence; missing required input or external resources still block the workflow. (Exact gate criteria for each stage are in `workflow.md`.)

## Plan Mode vs Dev-Workflow Stages

Claude Code's "plan mode" (ExitPlanMode) is a SEPARATE approval system from the
dev-workflow stage gate. The `advance.py` stage gate is the ONLY way to advance:
a plan approved via ExitPlanMode is NOT a stage confirmation and must never advance
or skip a stage. While in Stage 0-3, do NOT call ExitPlanMode; exiting plan mode to
implementation is only appropriate at the Stage 4 -> Stage 5 transition.

The detailed rules — `--confirmation` must carry the user's real words (never
invented), no self-certification of a Gate before Stage 3, and a `design-reviewer`
blocking finding is "fixed" only after the user confirms each fix — live in
`workflow.md` Global Rules (the plan-mode and confirmation rules). `workflow.md` is
the authoritative source for all stage rules; this section is only a pointer.

## Completion

Before any completion claim, use the verification stage. Completion requires evidence, not confidence.
After Stage 8 Gate passes, run `advance.py --reset` to clear the state file.
