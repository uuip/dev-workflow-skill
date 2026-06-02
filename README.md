# Dev Workflow Plugin

Claude Code 的 9 阶段门控开发工作流：需求澄清、设计、设计文档、实现计划、编码前确认、TDD 实现、集成测试、代码审查、完成验证。

## 安装

本地测试：

```bash
claude --plugin-dir /path/to/dev-workflow-plugin
```

通过本地 marketplace 安装：

```bash
/plugin marketplace add /path/to/dev-workflow-plugin
/plugin install dev-workflow@dev-workflow-local
/reload-plugins
```

## 使用

```text
/dev-workflow 实现用户登录功能
```

或直接在对话中说明：

```text
dev-workflow 我需要添加支付模块
```

工作流状态保存在当前项目的 `.claude/dev-workflow-state.json`。前三个关键阶段需要用户确认；之后由每个阶段的 Gate 证据推进。

## 组件

```text
dev-workflow-plugin/
├── .claude-plugin/
│   ├── marketplace.json
│   └── plugin.json
├── hooks/
│   ├── advance.py
│   ├── hooks.json
│   └── user-prompt-submit.py
├── references/
└── skills/
    └── dev-workflow/
        └── SKILL.md
```

`UserPromptSubmit` hook 会读取当前阶段，提醒 Claude Code 不要跳过 Gate，并在阶段不足时拦截提前编码。

## 验证

```bash
claude plugin validate --strict /path/to/dev-workflow-plugin
claude --plugin-dir /path/to/dev-workflow-plugin plugin details dev-workflow
```
