# Company Factory 冒烟测试记录（2026-02-24）

## 1. 测试目标

- 验证 `company_factory` 能否生成一个最小可用 Agent Company。
- 验证新生成公司是否可被 `nanobot company run --path ...` 实际执行。
- 重点观察默认流程在 `list_posts` / `spawn_worker` / `wait_for_tasks` 下的可用性。

## 2. 测试命令与结果

### 2.1 生成最小公司（首次执行）

命令：

```powershell
$env:PYTHONIOENCODING='utf-8'
python -X utf8 -m nanobot company run --name company_factory --task "创建一个最小测试公司，仅包含一个Manager和一个Worker岗位，输出完整四个配置文件。" --output workspace/deliverables/company_factory_smoke
```

关键结果：

- 执行成功，退出码 `0`。
- 生成目录：`workspace/deliverables/company_factory_smoke/`。
- 核心文件存在：`SKILL.md`、`POSTS.md`、`DOCS_SCHEMA.md`、`WORKFLOWS.md`。
- 运行日志显示 Manager 已按顺序调用：
  - `list_posts`
  - `spawn_worker`
  - `wait_for_tasks`
- 日志时间段：`2026-02-23 22:40:42` 至 `2026-02-23 22:44:15`（本地时区）。

### 2.2 运行生成的新公司（功能验证）

命令：

```powershell
$env:PYTHONIOENCODING='utf-8'
python -X utf8 -m nanobot company run --path workspace/deliverables/company_factory_smoke --task "请完成一次冒烟测试：创建一份Doc_Task_Order与一份Doc_Work_Report，并写入可验证内容。" --output workspace/deliverables/company_factory_smoke_runtime
```

关键结果：

- 执行成功，退出码 `0`。
- 生成目录：`workspace/deliverables/company_factory_smoke_runtime/`。
- 产物文件：
  - `Doc_Task_Order.md`
  - `Doc_Work_Report.md`
- `Doc_Work_Report.md` 中包含可验证标识：`SMOKE TEST SUCCESSFUL`。
- 日志时间段：`2026-02-23 22:44:32` 至 `2026-02-23 22:45:01`（本地时区）。

## 3. 观察结论

- 本轮修订后，默认流程稳定性明显提升：
  - Manager 能先枚举岗位再委派，减少错误 `post_id` 重试。
  - 委派后能显式等待子任务完成，避免阶段提前推进。
- 在真实执行中未触发“重复相同工具调用死循环”的阻断；loop guard 由自动化测试覆盖验证。

## 4. 备注

- 首次运行曾因 Windows 控制台编码（CP1252）无法打印 logo emoji 报错。
- 通过设置 `PYTHONIOENCODING=utf-8` + `python -X utf8` 解决，非业务逻辑缺陷。
