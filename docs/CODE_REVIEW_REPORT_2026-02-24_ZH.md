# 代码审查报告（中文，2026-02-24）

## 一、问题清单（按严重级别排序）

### Critical

1. **文件权限校验存在前缀匹配绕过风险**
   - 证据：
     - `nanobot/agent/tools/filesystem.py:12`
     - `nanobot/agent/tools/filesystem.py:44`
     - `nanobot/agent/tools/filesystem.py:46`
   - 影响：
     - `allowed_dir` 和 `allowed_paths` 都基于字符串 `startswith` 判断。
     - 例如允许目录是 `.../workspace/reports/` 时，`.../workspace/reports2/...` 可能被误判为合法路径。
     - 这会破坏岗位最小权限与隔离要求。

2. **多公司场景下，Worker 角色身份可能回退为默认身份**
   - 证据：
     - `nanobot/agent/context.py:28`
     - `nanobot/agent/context.py:43`
     - `nanobot/agent/context.py:45`
     - `nanobot/agent/subagent.py:217`
   - 影响：
     - `SubagentManager` 为子 Worker 构建 `ContextBuilder` 时没有传递公司上下文（`company_name/company_path`）。
     - 在非默认公司下，`get_agent_identity(post_id)` 可能找不到岗位定义，从而回退到通用 `nanobot` 身份提示。
     - 会导致岗位约束、权限边界与行为预期失效。

### High

3. **`DocumentFlowTool` 未绑定当前公司配置，可能套用默认公司文档规范**
   - 证据：
     - `nanobot/agent/tools/document_flow.py:65`
     - `nanobot/agent/subagent.py:384`
   - 影响：
     - 工具内部固定使用 `CompanyConfigLoader(workspace)` 默认解析路径。
     - 在 `--name`/`--path` 非默认公司时，可能读取错误的 `DOCS_SCHEMA.md`，导致文档模板、命名与目录错误。

4. **岗位工具策略为 fail-open**
   - 证据：
     - `nanobot/agent/subagent.py:391`
     - `nanobot/agent/subagent.py:402`
   - 影响：
     - 当岗位未声明 `tools`（空列表）时，代码会授予全部工具。
     - 与“最小权限”目标相冲突，带来额外安全面。

### Medium

5. **`WORKFLOWS.md` 需求已写入文档，但运行时仍是占位实现**
   - 证据：
     - `nanobot/company/loader.py:65`（`_load_workflows` 仍注释为 Placeholder）
     - `nanobot/company/loader.py:93`
     - `nanobot/company/loader.py:98`
   - 影响：
     - 目前主要依赖 `default_post` + `TASK_*.md` 扫描分发。
     - 文档中强调的基于流程文件驱动 PDCA 的能力尚未完整落地。

6. **README 任务命名示例与实际扫描规则不一致**
   - 证据：
     - `README.md:80`（示例为任意文件名）
     - `nanobot/company/manager.py:111`（仅扫描 `TASK_*.md`）
     - `nanobot/cli/company.py:78`（说明也写 `TASK_*.md`）
   - 影响：
     - 用户可能按 README 示例放入任务但不被处理。

7. **Worker 运行记录会在结束后被清理，审计追踪窗口受限**
   - 证据：
     - `nanobot/company/manager.py:167`
     - `nanobot/company/manager.py:169`
   - 影响：
     - 运行完成后注销 `workers.json` 记录并清除 Worker 内存目录。
     - 不利于后续绩效复盘与历史审计（除非额外归档）。

## 二、文档要求与代码实现对照

| 需求主题 | 文档来源 | 实现状态 | 结论 |
| --- | --- | --- | --- |
| 多公司加载（`--name`/`--path`） | `URD.md`, `MDD.md` | 已实现 | `CompanyConfigLoader._resolve_base_path` 已覆盖优先级。 |
| 任务输入（字符串/文件） | `URD.md`, `MDD.md` | 已实现 | `nanobot/cli/company.py` 支持 `--task` 文件或文本。 |
| 默认岗位分发 | `URD.md`, `MDD.md`, `README.md` | 已实现（有前提） | 依赖 `default_post`，否则任务跳过。 |
| `WORKFLOWS.md` 驱动流程/PDCA | `URD.md`, `MDD.md` | 部分实现 | 运行时未完成工作流解析执行。 |
| `DOCS_SCHEMA.md` 约束公文 | `URD.md`, `MDD.md` | 部分实现 | 有 `DocumentFlowTool`，但校验较弱且未绑定公司上下文。 |
| 每 Agent 独立内存 | `URD.md`, `MDD.md` | 已实现 | Worker 内存按 `workspace/workspace/memory/workers/{id}` 隔离。 |
| 岗位级工具/路径权限 | `URD.md`, `MDD.md`, `POSTS.md` | 部分实现（有关键缺陷） | 存在路径匹配绕过与 fail-open。 |
| Cron 与流程治理联动 | `URD.md`, `MDD.md` | 部分实现 | Cron 服务存在，但与 `WORKFLOWS.md` 语义联动不足。 |
| 公司级 `skills_dir` 子技能体系 | `URD.md` | 未实现 | Loader 未实际加载并传播公司级 `skills_dir`。 |

## 三、文档整理结论（docs 全量）

### 基本准确（可继续作为主文档）
- `docs/URD.md`
- `docs/MDD.md`
- `docs/ADD.md`
- `docs/COMPONENTS.md`

### 需要更新（与当前代码有偏差）
- `docs/introduction.md`（仍提到 `routes.json`）
- `docs/MANUAL_VERIFICATION.md`（本地路径与事件路径描述过旧）
- `docs/components/CLI.md`（`workspace/company` 与实际 `workspace/companies/<name>` 不一致）
- `docs/components/CHANNELS.md`（仍写 `config.yaml`）
- `docs/components/PROVIDERS.md`（仍写 `config.yaml` + `llm:`）
- `docs/components/SESSION.md`（会话存储路径描述不符）
- `docs/components/HEARTBEAT.md`（描述了当前代码里没有的 hook 机制细节）

### 建议归档（历史阶段文档）
- `docs/TRANSFORMATION_PLAN.md`
- `docs/MANAGER_HIERARCHY_ANALYSIS.md`
- `docs/components/UTILS.md`（列出多项当前不存在的 helper API）

## 四、测试与验证

- 在当前目录执行：`python -m pytest -q`
- 结果：`119 passed, 1 warning`

## 五、优先修复建议

1. 将路径权限判断从字符串前缀改为规范化路径边界判断（`resolve` + 父子关系判断）。
2. 将 `company_name/company_path` 贯通到 Subagent 的 `ContextBuilder` 与 `DocumentFlowTool`。
3. 工具授权改为 fail-closed：岗位未声明工具时不应默认全开。
4. 明确 `WORKFLOWS.md`：要么完成解析执行，要么在文档中明确“当前不支持运行时编排”。
5. 批量修正文档路径与配置格式描述，并把历史文档移入归档目录。

