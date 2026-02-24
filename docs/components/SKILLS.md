# 技能系统 (Skills)

本文档对应当前实现：`nanobot/agent/skills.py`。

## 技能来源与优先级

`SkillsLoader` 当前支持三层来源：
1. `workspace/skills`（最高优先级）
2. 公司级 `skills_dir`（来自 `SKILL.md`）
3. 内置技能目录 `nanobot/skills`

同名技能按上述顺序覆盖，避免重复加载。

## SKILL.md 结构

每个技能目录包含一个 `SKILL.md`，可带 frontmatter 元数据。

常见元数据：
- `name`
- `description`
- `metadata`（可包含 `nanobot.requires` 等约束）

## 运行时使用方式

- Worker 根据岗位定义的 `post.skills` 精确加载技能内容。
- 可通过 `list_skills(filter_unavailable=True)` 过滤依赖未满足的技能。

## 注意事项

- 公司级 `skills_dir` 由公司配置解析后注入运行时，不需要改动全局内置技能目录。
- 技能文档是提示词资产，不是 Python 插件加载机制。
