# 技能系统 (Skills)

Skills 是 Nanobot 的可扩展能力单元。通过 Skills，Agent 可以获得特定领域的即时知识（如 GitHub 操作指南、Linux 命令技巧）或特定工具的使用方法。

## 1. 核心架构

Skills 系统基于文件系统设计，每个 Skill 是一个包含 `SKILL.md` 的目录。

### 1.1 目录结构

系统从以下两个位置加载 Skills（优先级从高到低）：

1. **Workspace Skills**: `workspace/skills/` (用户自定义，最高优先级)
2. **Built-in Skills**: `nanobot/skills/` (系统内置)

```text
skills/
├── github/
│   └── SKILL.md
├── weather/
│   └── SKILL.md
└── my-custom-skill/
    └── SKILL.md
```

### 1.2 SKILL.md 格式

`SKILL.md` 是一个带有 YAML Frontmatter 的 Markdown 文件。

```markdown
---
name: weather
description: Get current weather and forecasts.
metadata: {
  "nanobot": {
    "emoji": "🌤️",
    "requires": {
      "bins": ["curl"],
      "env": []
    }
  }
}
---

# Weather

Using `curl wttr.in` to get weather info...
```

- **YAML Frontmatter**: 定义元数据（名称、描述、依赖）。
- **Markdown Body**: 包含给 Agent 阅读的操作指南、示例代码和注意事项。此部分内容会在 Agent 加载该 Skill 时被注入到 System Prompt 中。

### 1.3加载机制 (SkillsLoader)

文件位置: `nanobot/agent/skills.py`

`SkillsLoader` 负责：
1. **扫描**: 遍历 Skills 目录。
2. **过滤**: 检查 `requires` 定义的依赖（如 CLI 工具、环境变量）是否满足。如果不满足，该 Skill 将不可见。
3. **注入**: 当 Agent 需要使用某个 Skill 时（根据 `POSTS.md` 定义），Loader 读取 Markdown 内容并注入到上下文。

## 2. 内置技能 (Built-in Skills)

| 技能 | 描述 | 依赖 |
| :--- | :--- | :--- |
| **github** | GitHub CLI 操作指南，管理 Issue/PR。 | `gh` |
| **weather** | 获取天气信息 (wttr.in)。 | `curl` |
| **cron** | 设置和管理 crontab 定时任务。 | `crontab` |
| **summarize** | 文本/网页摘要能力。 | - |
| **tmux** | 管理 Tmux 会话，保持任务后台运行。 | `tmux` |
| **memory** | 记忆管理技巧 (手动读写 MEMORY.md)。 | - |
| **skill-creator** | 引导 Agent 创建新 Skill 的元技能。 | - |
| **clawhub** | 从 ClawHub 仓库下载社区技能。 | - |

## 3. 在 Worker 中使用

在 `POSTS.md` 中为岗位指定 Skills：

```markdown
# 岗位: GitHub管理员
...
Skills:
- github
- summarize
```

当 `SubagentManager` 启动该 Worker 时，会自动加载对应的 Skill 内容。
