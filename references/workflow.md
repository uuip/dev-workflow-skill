# Dev Workflow Pipeline

This file controls the workflow. It does not replace node prompts.
When running this skill, determine the current stage, then read only the referenced node file.

## Global Rules

1. Do not skip stages.
2. Execute only actions allowed by the current stage.
3. If required inputs are missing, stop and state exactly what is missing.
4. A stage must pass its Gate before the next stage starts.
5. If a previous artifact is incomplete, go back to the stage that owns it.
6. Do not cross human confirmation Gates before Stage 3.
7. Before coding, requirement clarification, design, design docs, and task planning must be complete.
8. Before claiming completion, use `superpowers:verification-before-completion` and the verification stage.
9. When a stage references another skill, invoke that skill by its exact name, for example `superpowers:brainstorming`.
10. When a stage requires review, delegate to the configured reviewer agent by exact name when the platform supports agents:
    - `design-reviewer`
    - `verification-reviewer`
11. If the user says required documents, files, screenshots, logs, API docs, credentials, API keys, tokens, accounts, or other external resources will be provided, stop at the owning stage until those inputs are actually available. Do not invent, skip, mock, or mark them optional unless the user explicitly changes the requirement.
12. If verification or tests require external resources only the user can provide, such as API keys, cloud accounts, paid services, private endpoints, captcha/manual login, or production-like data, stop and ask for the missing resource or for explicit permission to record that check as unverified.
13. Claude Code plan mode approval (ExitPlanMode) is NOT a stage confirmation. Never advance a stage because a plan was approved in plan mode. Stage confirmation before Stage 3 requires an explicit user answer recorded via `advance.py --confirmation` with the user's own words.
14. Do not call ExitPlanMode while the workflow is in Stage 0-3. Plan-mode exit to implementation is only appropriate at Stage 4 to Stage 5 on Claude Code.
15. Before Stage 3, the model does not self-certify that a stage Gate passed. State the evidence, ask the user, and advance only after the user explicitly confirms. From Stage 3 onward, forward advancement on evidence is allowed per the rules above.
16. A `design-reviewer` blocking finding counts as "fixed" only after the user confirms each fix. Updating the plan or design file is not user confirmation.
17. Stay within the current stage's Allowed list. Do not perform a later stage's work (for example, no Stage 6 integration test design while in Stage 3). When unsure, re-read the current stage's Allowed and Forbidden lists before acting.
18. Ground every factual claim before acting on it. This applies to ALL stages. For any claim about what exists or how the project works — files, infrastructure, configs, APIs, dependencies, conventions — verify it by reading the actual project (search, read files, run a read-only check) before you state it or build on it. Never let a prior or a "most common pattern" stand in for verification. Do not degrade "should check first" into "guess the most likely answer, then justify the guess" (confirmation bias + hallucinated completion + missing grounding). When you cannot verify, say so explicitly and ask, rather than assuming.

## Platform Notes

- Claude Code: `/dev-workflow:workflow` is provided as a slash command. Claude reviewer agents are installed under `~/.claude/agents`.
- Codex: use the `dev-workflow` skill by saying `/dev-workflow ...` or `使用 dev-workflow ...`. Codex reviewer agents are installed under `~/.codex/agents`.
- Codex hooks are not configured here because no supported local hook schema was found in this environment. Codex Gates are enforced by this skill and reviewer agents.
- Claude hooks may be configured separately to remind or block unsafe stage transitions.
- Human archive design docs belong under the target project `docs` directory, not `docs/superpowers`.

## Stage 0: Requirement Clarification

Node file: `references/requirements.md`

Required skill:
- `superpowers:brainstorming`

Input:
- Raw feature description
- Known information
- Existing system context
- User-promised supporting documents, files, screenshots, logs, API docs, credentials, or external resources, if any

Allowed:
- Organize requirement material
- Clarify missing information
- Ask the most important question first
- Scan obvious missing roles, permissions, flows, data rules, edge cases, and deployment risks

Forbidden:
- No detailed design
- No task breakdown
- No coding

Output:
- Organized requirement material
- Clarification questions and answers
- Accepted assumptions
- Risk and missing-information list
- Decision on whether design may start

Gate:
- Raw feature description exists
- Any user-promised required supporting material has been provided, or the user explicitly removes that requirement
- Critical questions are answered or explicit assumptions are accepted by the user
- Risks and missing information are recorded
- User confirms entering design

Next:
- Stage 1

Fallback:
- Stay in Stage 0 if material, answers, or assumptions are insufficient

## Stage 1: Software Design

Node file: `references/design-1.md`

Required skill:
- `superpowers:brainstorming`

Reviewer agent:
- `design-reviewer`

Input:
- Confirmed requirement clarification
- Confirmed assumptions and risk list

Allowed:
- Produce design options and tradeoffs
- Recommend the simplest sufficient design
- Define boundaries, modules, interfaces, data, errors, permissions, concurrency, deployment, and rollback
- Produce Mermaid diagrams
- Self-review the design
- Delegate design review to `design-reviewer` after the design draft is ready

Forbidden:
- No design documentation write-out
- No task breakdown
- No coding

Output:
- Confirmed design draft
- Diagrams
- Design self-review
- Design reviewer findings

Gate:
- Design covers clarified requirements and risk list
- Diagrams are present or explicitly marked not applicable
- No unresolved critical assumption remains
- `design-reviewer` has no blocking finding, or blocking findings are fixed
- User confirms the design

Next:
- Stage 2

Fallback:
- Stage 0 if scope or requirement assumptions are unclear
- Stage 1 if design or review findings need correction

## Stage 2: Design Documentation

Node file: `references/design-docs.md`

Reviewer agent:
- `design-reviewer`

Input:
- User-confirmed design
- Confirmed Mermaid diagrams
- Project directory

Allowed:
- Create or update a design document under project `docs`
- Write confirmed design and Mermaid diagrams
- Check the document for placeholders, contradictions, missing diagrams, missing error paths, and unconfirmed assumptions
- Delegate document review to `design-reviewer`

Forbidden:
- Do not change confirmed design meaning
- Do not write the human archive design document under `docs/superpowers`
- No task breakdown
- No coding

Output:
- Project `docs` design document
- Design document review result

Gate:
- Design doc exists under project `docs`
- Design doc path is not under `docs/superpowers`
- It contains confirmed design and key diagrams
- No obvious placeholders, contradictions, missing diagrams, or unconfirmed assumptions
- `design-reviewer` has no blocking document finding, or blocking findings are fixed
- User confirms the doc can drive task planning

Next:
- Stage 3

Fallback:
- Stage 2 if docs are incomplete
- Stage 1 if design itself is wrong

## Stage 3: Implementation Plan

Node file: `references/design-2.md`

Required skill:
- `superpowers:writing-plans`

Input:
- Project `docs` design document
- Confirmed design

Allowed:
- Break work into small verifiable tasks
- Define inputs, outputs, dependencies, implementation notes, test requirements, and acceptance criteria
- Define what each task must not do

Forbidden:
- No coding
- Do not omit tests

Output:
- Development task list
- Test plan
- Acceptance criteria

Gate:
- Each task is independently developable and verifiable
- Each task has tests and acceptance criteria
- Tasks cover key design points

Next:
- Stage 4

Fallback:
- Stage 2 if design docs are incomplete
- Stage 3 if tasks are too coarse

## Stage 4: Pre-Coding Confirmation

Node file: `references/coding-plan.md`

Input:
- Confirmed implementation task
- Current codebase

Allowed:
- Read related code style
- State planned file changes
- State why each new function/class/module is necessary
- State verification method
- State first failing tests to write

Forbidden:
- No coding before this stage Gate passes
- No unplanned abstractions
- No unrelated refactoring

Output:
- Pre-coding change plan
- Test-first plan

Gate:
- File scope is clear
- New object necessity is clear
- Non-goals are clear
- Verification method is clear

Next:
- Stage 5

Fallback:
- Stage 3 if the task is unclear
- Stage 1 or Stage 2 if the design blocks implementation

## Stage 5: TDD Implementation

Node file: `references/tdd-implementation.md`

Required skill:
- `superpowers:test-driven-development`

Input:
- Confirmed pre-coding plan
- Confirmed implementation task
- Confirmed failing-test list

Allowed:
- Write failing test first
- Verify the failure reason
- Write minimal implementation
- Verify tests pass
- Clean up only after green

Forbidden:
- No production code before failing test
- No unplanned features
- No unrelated refactoring
- Do not treat local unit or narrow API tests as integration testing

Output:
- Code changes
- Test changes
- Test output

Gate:
- Failing test was observed first
- Minimal implementation passed tests
- No unplanned feature exists
- No unrelated refactor exists

Next:
- Stage 6

Fallback:
- Stage 4 if tests cannot be planned
- Stage 3 if task acceptance is unclear

## Stage 6: Integration Testing

Node file: `references/integration-testing.md`

Input:
- Project `docs` design document
- Confirmed implementation plan
- Code changes
- Passed TDD test output
- Project local run and dependency setup

Allowed:
- Use real or project-approved local infrastructure such as PostgreSQL, MySQL, Redis, Nginx, message queues, object storage, or docker compose/testcontainers
- Design and run full business-flow tests from workflow entry to workflow end
- Verify real data writes, reads, state changes, permissions, cleanup, and failure outcomes
- Stop and request required external resources when checks need user-provided API keys, tokens, accounts, private services, manual login, or similar inputs

Forbidden:
- No unit-test-only evidence
- No single-function, single-repository, or single-interface-only checks
- No HTTP-200-only checks
- No replacing required infrastructure interactions with mocks
- No silently skipping externally blocked checks
- No unrelated production abstractions for test convenience

Output:
- Integration test scenarios
- Infrastructure used
- Test data setup and cleanup strategy
- Integration test files or commands
- Integration test output and exit codes
- Externally blocked checks, if any

Gate:
- Core business flow coverage list was produced
- Every new or modified core business flow has a complete successful-path test, or an uncovered reason is recorded with user acknowledgement
- Permission, state transition, duplicate submission, concurrency, cache, async job, and external-service flows are covered when applicable, or uncovered reasons are recorded with user acknowledgement
- Required real infrastructure was used, or missing external resources are recorded with user acknowledgement
- Integration test output and exit codes were read
- Test data setup and cleanup are clear
- No blocking integration failure remains

Next:
- Stage 7

Fallback:
- Stage 5 if implementation needs fixes
- Stage 4 if integration test scope or setup was not planned
- Stage 3 if task acceptance is unclear

## Stage 7: Code Review

Node file: `references/review.md`

Required skill:
- `superpowers:requesting-code-review`

Reviewer agent:
- None. Use `superpowers:requesting-code-review` for the review workflow.

Input:
- Code changes
- Task acceptance criteria
- Pre-coding plan
- Integration test result

Allowed:
- Review over-design, unclear names, scope drift, missing tests, and low-quality implementation
- List findings before edits

Forbidden:
- Do not modify code during review
- No feature expansion

Output:
- Code review findings
- Must-fix decision

Gate:
- No Critical or Important issue remains
- Must-fix findings are fixed and re-reviewed

Next:
- Stage 8

Fallback:
- Stage 6 if integration coverage or evidence is insufficient
- Stage 5 if implementation needs fixes
- Stage 3 if task definition is wrong
- Stage 1 if design is wrong

## Stage 8: Completion Verification

Node file: `references/verification.md`

Required skill:
- `superpowers:verification-before-completion`

Reviewer agent:
- `verification-reviewer`

Input:
- Requirement clarification result
- Project `docs` design document
- Implementation plan
- Code changes
- Integration test result
- Review result

Allowed:
- Run necessary final verification commands
- Read full output and exit codes
- Check docs, TDD test evidence, integration test evidence, lint, build, and acceptance criteria
- Stop and request required external resources when checks need user-provided API keys, tokens, accounts, private services, manual login, or similar inputs
- Delegate evidence review to `verification-reviewer`

Forbidden:
- Do not claim completion before verification
- Do not redesign or add new integration scenarios here; go back to Stage 6 if integration testing is missing or insufficient
- Do not replace evidence with “should”, “looks”, or “probably”
- Do not skip externally blocked checks silently

Output:
- Verification commands or checks
- Verification evidence
- Integration test evidence check
- Unverified or failed items
- Completion decision

Gate:
- Necessary final checks ran
- Stage 6 integration test evidence exists and is sufficient, or externally blocked checks are listed with user acknowledgement
- Externally blocked checks are either completed after the user provides the resource or explicitly listed as unverified with user acknowledgement
- Outputs were read
- Acceptance criteria were checked one by one
- `verification-reviewer` has no blocking evidence gap

Next:
- Complete

Fallback:
- Stage 6 if integration tests fail or integration evidence is missing
- Stage 5 if tests or build fail because implementation needs fixes
- Stage 7 if review issues remain
- Stage 2 if design docs are missing
- Stage 3 if implementation plan coverage is insufficient
