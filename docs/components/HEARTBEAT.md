# Heartbeat 心跳服务 (Heartbeat Service)

本文档对应当前实现：`nanobot/heartbeat/service.py`。

## 作用

Heartbeat 不是固定业务流程引擎，而是周期唤醒机制：
- 周期扫描任务目录状态
- 在 `HEARTBEAT.md` 有可执行内容时唤醒 Agent

## 核心参数

- `interval_s`：默认 1800 秒（30 分钟）
- `enabled`
- `on_heartbeat`：回调（通常在 gateway 中绑定到 `AgentLoop.process_direct`）

## 当前行为

每次 tick：
1. 扫描 `workspace/workspace/tasks/TASK_*.md` 的状态并记录日志。
2. 读取 `<workspace>/HEARTBEAT.md`。
3. 若 HEARTBEAT 文档为空/无动作项，则跳过。
4. 否则调用 `on_heartbeat(HEARTBEAT_PROMPT)`。

默认 prompt：
- 让 Agent 读取 `HEARTBEAT.md`
- 无需处理时返回 `HEARTBEAT_OK`

## 与 Gateway 集成

在 `nanobot gateway` 中：
- 默认每 30 分钟触发一次
- 与 CronService 并行运行
