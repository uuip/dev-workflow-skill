# Changelog

所有重要的项目变更都会记录在此文件中。

## [1.1.0] - 2026-06-08

### Fixed
- 区分 Claude Code plan mode 与工作流阶段门控：明确 ExitPlanMode 批准不等于阶段确认，避免借 plan 批准跳过中间阶段
- `advance.py`：缺少 `--confirmation` 时报错改为"停下询问用户"，并拒绝模型自编的确认文本（如引用 plan mode 批准）
- 阶段确认权与 Gate 判定权归还用户：Stage 0-2 的 Gate 通过与 design-reviewer 阻断问题修复需用户确认，模型不得自评
- 强化集成测试规范（`references/integration-testing.md`）：要求先实证勘察真实基础设施再下结论（反确认偏误/事实锚定），禁止用 mock 替代真实基础设施依赖，明确测试数据值可随机或假造的例外
- `references/design-2.md`：Stage 3 的 Test Plan 只列单元测试计划，集成/端到端测试留给 Stage 6

### Added
- PreToolUse hook（`hooks/pre-tool-use.py`）：工作流处于 Stage < 4 时硬拦截 ExitPlanMode
- 启动时引导进入 plan 模式：SKILL.md Start 首步与 UserPromptSubmit hook 在 dev-workflow 启动时提示调用 EnterPlanMode（Stage 0-3 为只读阶段）
- 集成测试 UI 验证要求：涉及 UI 的流程必须用 playwright-cli skill 跑真实浏览器流程（当环境提供时），不得用类型检查/代码审查代替
- `references/workflow.md`：Global Rules 新增第 13-18 条（含全局事实锚定原则：先查证再下结论，不得"先猜答案再找理由"）
- `SKILL.md`：新增 "Plan Mode vs Dev-Workflow Stages" 一节

## [1.0.0] - 2026-06-02

### Added
- 9 阶段门控工作流
- 状态持久化（`.claude/dev-workflow-state.json`）
- UserPromptSubmit hook 自动阻断
- 前三个阶段的人工确认门
- 阶段回退支持

### Dependencies
- 依赖 superpowers 插件

[1.1.0]: https://github.com/uuip/dev-workflow-skill/releases/tag/v1.1.0
[1.0.0]: https://github.com/uuip/dev-workflow-skill/releases/tag/v1.0.0
