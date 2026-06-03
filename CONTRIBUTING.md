# 贡献指南

感谢你对 dev-workflow-skill 的兴趣！

## 开发设置

### 前置要求

- Python 3.7+
- Claude Code CLI

### 本地开发

1. 克隆仓库：

```bash
git clone https://github.com/uuip/dev-workflow-skill.git
cd dev-workflow-skill
```

2. 使用本地插件启动 Claude Code：

```bash
claude --plugin-dir /path/to/dev-workflow-skill
```

3. 测试插件：

```bash
/dev-workflow:workflow 测试功能
```

## 项目结构

```
dev-workflow-skill/
├── .claude-plugin/          # Plugin 元数据
│   ├── plugin.json         # 插件配置
│   └── marketplace.json    # 本地 marketplace 示例
├── hooks/                   # Hook 脚本
│   ├── hooks.json          # Hook 配置
│   ├── advance.py          # 状态推进脚本
│   └── user-prompt-submit.py  # UserPromptSubmit hook
├── skills/                  # Skill 定义
│   └── workflow/
│       └── SKILL.md
├── references/              # 各阶段参考文档
│   ├── workflow.md         # 状态机核心
│   ├── requirements.md     # Stage 0
│   ├── design-1.md         # Stage 1
│   ├── design-docs.md      # Stage 2
│   ├── design-2.md         # Stage 3
│   ├── coding-plan.md      # Stage 4
│   ├── tdd-implementation.md   # Stage 5
│   ├── integration-testing.md  # Stage 6
│   ├── review.md           # Stage 7
│   └── verification.md     # Stage 8
└── README.md
```

## 修改指南

### 修改工作流阶段

1. **修改状态机**：编辑 `hooks/advance.py` 中的 `STAGE_NAMES` 和 `VALID_FALLBACKS`
2. **修改 Gate 定义**：编辑 `references/workflow.md`
3. **修改阶段提示**：编辑 `references/` 下对应的 `.md` 文件
4. **修改 Hook 行为**：编辑 `hooks/user-prompt-submit.py`

### 添加新阶段

1. 在 `advance.py` 的 `STAGE_NAMES` 中添加新阶段
2. 在 `VALID_FALLBACKS` 中定义允许的回退路径
3. 在 `references/workflow.md` 中添加阶段定义和 Gate
4. 在 `references/` 下创建新的阶段参考文档
5. 如需人工确认，更新 `HUMAN_CONFIRMATION_TRANSITIONS`

### 测试修改

```bash
# 测试状态推进脚本
python3 hooks/advance.py --help
python3 hooks/advance.py --init
python3 hooks/advance.py --show

# 测试 Hook
echo '{"prompt": "开始编码"}' | python3 hooks/user-prompt-submit.py
```

## 提交规范

- 提交信息使用中文或英文，简洁明确
- 一个提交只做一件事
- 重要修改请附带说明

### 示例

```
修复: Stage 3 回退到 Stage 1 的逻辑错误

- 更新 VALID_FALLBACKS 允许 Stage 3 回退到 Stage 1
- 在 workflow.md 中记录该回退路径的使用场景
```

## Pull Request

1. Fork 本仓库
2. 创建特性分支：`git checkout -b feature/your-feature`
3. 提交修改：`git commit -m '添加某功能'`
4. 推送分支：`git push origin feature/your-feature`
5. 创建 Pull Request

### PR 检查清单

- [ ] 代码可以正常运行
- [ ] Python 脚本通过基本测试
- [ ] 修改了相关文档
- [ ] 添加了必要的说明

## 许可证

通过提交 PR，你同意你的贡献使用 MIT 许可证。
