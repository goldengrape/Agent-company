# Heartbeat 心跳服务 (Heartbeat Service)

`nanobot/heartbeat` 组件赋予了 Agent "主动性"。不同于被动等待用户消息，心跳服务允许 Agent 定期自我唤醒，检查系统状态或执行后台维护。

## 核心理念

传统的 Chatbot 是 **Reactive (反应式)** 的：用户输入 -> Bot 回复。
Nanobot 通过 Heartbeat 实现了 **Proactive (主动式)** 行为：
1.  定时触发 (例如每 30 分钟)。
2.  发送一条系统级的 Prompt 给 Agent (例如 "System Heartbeat: check pending tasks")。
3.  Agent 即使没有收到用户消息，也能借此机会思考、检查 `hooks`、运行 `Cron` 任务或处理 `Memory` 压缩。

## 服务实现 (`service.py`)

`HeartbeatService` 是一个简单的异步循环。

### 主要参数

- `interval_s`: 心跳间隔（秒）。
- `on_heartbeat`: 回调函数。通常绑定到 `AgentLoop.process_direct`。
- `enabled`: 开关。

### 工作流程

1.  启动后台 `loop`。
2.  休眠 `interval_s` 秒。
3.  调用 `on_heartbeat("System Heartbeat: ...")`。
    - 这会被 Agent 视为一条来自 `system` 来源的特殊消息。
    - Agent 会执行标准的 `ReAct` 循环。
    - 如果 Agent 决定不采取行动（例如没有积压任务），它可能会回复 "Nothing to report" 或直接结束。

## 代码示例

### 在 Gateway 中集成

```python
from nanobot.heartbeat.service import HeartbeatService

async def on_heartbeat(prompt: str):
    # 以 "heartbeat" 身份调用 Agent
    await agent.process_direct(prompt, session_key="heartbeat")

service = HeartbeatService(
    workspace=Path("."),
    on_heartbeat=on_heartbeat,
    interval_s=1800,  # 30 分钟
    enabled=True
)

await service.start()
```

### 结合已有的 Hook 系统

心跳服务通常与 Agent 的 Hook 系统配合使用。
例如，`Phase 4` 实现的服务监测逻辑：
1.  Heartbeat 触发 Agent。
2.  Agent Loop 运行 `pre_observation` hooks。
3.  Hook 检查 `workspace/tasks` 是否有超时任务。
4.  如果有，Hook 注入提示信息。
5.  Agent 收到提示，决定发送报警消息给管理员。
