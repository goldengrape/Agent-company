# 修订说明（2026-02-24）

本文档说明本轮“按 code review 修订”中，代码与文档改动的原因、目标与预期效果。

## 1. 默认流程不稳定：重复调用与无效委派

### 问题现象
- Manager 在部分场景下会重复调用同一工具、使用同一参数，出现循环。
- `spawn_worker` 使用了不存在的 `post_id` 时，报错信息不足，模型容易继续“盲试”。

### 修订内容
- 新增工具 `list_posts`，允许先查询可用岗位 ID，再进行委派。
- `spawn_worker` 的未知岗位错误增加“可用岗位列表”和明确引导。
- 在 `SubagentManager` 增加重复相同工具调用的循环保护（loop guard）。
- 在岗位身份提示中加入委派纪律：先 `list_posts`，委派后 `wait_for_tasks`，失败后不得重复相同调用。

### 原因与收益
- 原因：默认流程高度依赖 LLM 自主规划，缺少“校验岗位 ID”和“防重复执行”这两类硬约束。
- 收益：降低无效工具调用与卡死概率，提高默认流程的可收敛性与可恢复性。

## 2. 文档与代码工具集合不一致

### 问题现象
- 多份 `POSTS.md` 使用了未实现工具名（如 `grep_search`、`run_command`）。
- Manager 的工具清单和流程文档未显式要求 `wait_for_tasks`，导致并发后不同步。

### 修订内容
- 统一修订以下文档中的工具名到当前真实实现：
  - `companies/company_factory/POSTS.md`
  - `companies/template/POSTS.md`
  - `companies/default/POSTS.md`
  - `companies/tech_news_filter/POSTS.md`
- Manager 岗位统一补充：`list_posts` + `wait_for_tasks`。
- `company_factory` 的 `WORKFLOWS.md` 和 `SKILL.md` 增加强制执行纪律与 TODO 队列式默认任务模板。

### 原因与收益
- 原因：文档中出现“工具名漂移”，与运行时能力不一致，误导模型规划。
- 收益：减少“文档要求存在、代码能力不存在”的错配，提升公司模板可执行性。

## 3. 面向回归的测试补强

### 新增/修订测试点
- `list_posts` 工具返回岗位列表与详情。
- `spawn_worker` 在未知岗位时返回可用岗位 ID 与引导信息。
- Subagent 对重复相同工具调用触发 loop guard，并以可解释结果退出。

### 原因与收益
- 原因：此前缺少针对“流程稳定性”关键路径的自动化回归测试。
- 收益：后续重构时可快速发现委派/循环相关退化。

## 4. 与 code review 结论的对应关系

- 对应“默认流程可用性不稳定”的修订：第 1、2、3 节。
- 对应“文档要求与代码实现一致性”修订：第 2 节。
- 本次修订优先处理“可执行性与稳定性”问题；更大范围的流程编排引擎改造（如完整 `WORKFLOWS.md` 解释执行）仍建议后续专项迭代。
