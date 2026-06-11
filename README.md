# Dev Workflow Plugin

门控式软件开发流水线，用于 Claude Code 的 9 阶段开发工作流：需求澄清 → 软件设计 → 设计文档 → 实现计划 → 编码前确认 → TDD 实现 → 集成测试 → 代码审查 → 完成验证。

## 特性

- **9 阶段门控流水线**：每个阶段都有明确的 Gate 条件，只有通过才能进入下一阶段
- **状态持久化**：工作流状态保存在项目的 `.claude/dev-workflow-state.json`
- **人工确认门**：前三个关键阶段（进入设计、设计批准、设计文档验收）需要用户明确确认
- **自动阻断**：通过 UserPromptSubmit hook 自动阻止跳过阶段的尝试
- **阶段回退**：支持在特定阶段之间回退，便于迭代修正

## 工作流阶段

### 阶段表

| 阶段 | 名称 | Gate 要求 | 人工确认 |
|------|------|-----------|----------|
| 0 | Requirement Clarification | 需求已澄清并文档化 | ✓ |
| 1 | Software Design | 设计方案完整 | ✓ |
| 2 | Design Documentation | 设计文档已写入项目 | ✓ |
| 3 | Implementation Plan | 任务分解完成 | - |
| 4 | Pre-Coding Confirmation | 预检清单通过 | - |
| 5 | TDD Implementation | 测试和实现完成 | - |
| 6 | Integration Testing | 集成测试通过 | - |
| 7 | Code Review | 审查通过 | - |
| 8 | Completion Verification | 验收完成 | - |

## 依赖与配置

### 依赖插件

本插件依赖以下 superpowers skills：

- `superpowers:brainstorming` - 用于 Stage 0 和 Stage 1
- `superpowers:writing-plans` - 用于 Stage 3
- `superpowers:test-driven-development` - 用于 Stage 5
- `superpowers:requesting-code-review` - 用于 Stage 7
- `superpowers:verification-before-completion` - 用于 Stage 8

这些 skills 来自 [superpowers](https://github.com/obra/superpowers) 插件，需要单独安装。

本插件依赖 [playwright-cli skill](https://github.com/microsoft/playwright-cli)

### Hook 支持

本插件使用 Claude Code 的 UserPromptSubmit hook 来自动阻止跳过阶段的行为。

**支持的平台**：
- ✅ Claude Code - 完整支持（包括 hook）
- ⚠️ 其他平台 - 部分支持（仅 skill，无 hook 自动阻断）

确保你的 Claude Code 版本支持 hooks 功能。如果使用其他平台，工作流仍可正常使用，但需要手动遵守阶段规则。

### 系统要求

- Python 3.7+
- 无外部依赖（仅使用标准库）

## 安装

> 前置要求：Claude Code 需支持插件市场（`/plugin` 命令）。若 `/plugin` 不可用，先升级：`npm update -g @anthropic-ai/claude-code`。

### 1. 安装依赖插件

```bash
/plugin install superpowers@claude-plugins-official

npm install -g @playwright/cli@latest
playwright-cli --help
playwright-cli install --skills
```

### 2. 安装本插件

```bash
/plugin marketplace add uuip/dev-workflow-skill
/plugin install dev-workflow@dev-workflow
/reload-plugins
```

## 使用

### 启动工作流

使用 skill 命令：

```text
/plan
/dev-workflow:workflow 实现用户登录功能
```

或在对话中直接提及：

```text
dev-workflow 我需要添加支付模块
```

### 状态管理

工作流状态保存在：

```
<project>/.claude/dev-workflow-state.json
```

## 最佳实践

1. **不要跳过阶段**：每个阶段都有其价值，跳过会导致问题累积
2. **充分澄清需求**：在 Stage 0 多花时间，后续会更顺畅
3. **保存设计文档**：Stage 2 的设计文档应写入项目，作为持久参考
4. **写测试先行**：Stage 5 使用 TDD，先写测试再实现
5. **完整验收**：Stage 8 验证所有功能、测试、文档是否完整

## 常见问题

### Q: 可以跳过某些阶段吗？

A: 不建议。每个阶段都有 Gate 条件，跳过会导致质量问题。如果项目很简单，可以快速通过各阶段，但不应跳过。

### Q: 可以在工作流外修改代码吗？

A: 可以，但工作流不会追踪这些修改。建议小的修复可以在工作流外进行，大的功能开发应使用工作流。

### Q: 状态文件丢失了怎么办？

A: 可以手动初始化到合适的阶段，但需要确保前置阶段的工件（需求文档、设计文档等）已存在。

### Q: 如何自定义工作流？

A: Fork 本项目，修改 `references/` 下的文档和 `advance.py` 中的状态机定义。

## 贡献

欢迎提交 Issue 和 Pull Request！

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/amazing-feature`)
3. 提交修改 (`git commit -m 'Add amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 开启 Pull Request

## 许可证

MIT License - 详见 [LICENSE](LICENSE) 文件

## 致谢

本插件基于软件工程最佳实践设计，参考了：

- TDD (Test-Driven Development)
- Gated Development Process
- Requirements Engineering
- Design Documentation

---

**作者**: uuip  
**仓库**: https://github.com/uuip/dev-workflow-skill
