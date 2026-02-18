# Cron 定时任务 (Cron Service)

`nanobot/cron` 组件提供了一个轻量级、持久化的定时任务调度服务，允许 Agent 在后台自动执行预定的任务。

## 核心功能

- **统一调度**: 支持三种类型的调度策略：
    1.  **Interval (Every)**: 每隔 X 秒执行一次。
    2.  **Cron Expression**: 使用标准 Cron 表达式 (e.g., `0 9 * * *`)，支持指定时区。
    3.  **One-time (At)**: 在指定时间点执行一次（之后可自动删除）。
- **持久化**: 任务列表存储在 `data/cron/jobs.json`，重启后自动加载并恢复调度。
- **Agent 集成**: 任务触发时，不仅是执行代码，通过 `Agent Loop` 模拟一次用户交互，拥有完整的上下文和工具调用能力。

## 数据结构 (`types.py`)

### CronJob (定时任务)
- `id`: 唯一标识符
- `name`: 任务名称
- `schedule`: 调度配置 (`CronSchedule`)
- `payload`: 触发时的动作 (`CronPayload`)
- `state`: 运行时状态（下次运行时间、最后状态、错误信息）

### CronPayload (任务载荷)
- `message`: 发送给 Agent 的提示词 (Prompt)。
- `deliver`: 是否将 Agent 的回复发送到外部渠道。
- `channel/to`: 指定回复的目标渠道和接收人。

## 服务实现 (`service.py`)

`CronService` 维护一个 asyncio 的后台循环。

1.  **加载**: 启动时从 JSON 读取任务。
2.  **计算**: 基于当前时间，计算每个任务的 `next_run_at_ms`。
3.  **等待**: 计算最近一个任务的等待时间，设置 `asyncio.sleep`。
4.  **触发**:
    - 调用回调函数（通常是 `AgentLoop.process_direct`）。
    - 传入特殊的 Session ID `cron:{job_id}`，确保每个任务有独立的对话历史。
5.  **更新**: 记录执行结果，重新计算下一次运行时间，保存到磁盘。

## 使用示例

### 1. 每天早上报时 (CLI)

```bash
nanobot cron add \
    --name "Morning Greeting" \
    --cron "0 8 * * *" \
    --tz "Asia/Shanghai" \
    --message "请根据今天的天气和新闻，生成一段早安问候。" \
    --deliver --channel telegram --to 123456789
```

### 2. 每小时检查服务器状态

```bash
nanobot cron add \
    --name "Health Check" \
    --every 3600 \
    --message "使用 exec 工具检查服务器磁盘空间，如果低于 10% 则报警。"
```

### 3. 代码调用

```python
from nanobot.cron.types import CronSchedule

# 添加一个一次性任务
service.add_job(
    name="Remind me later",
    schedule=CronSchedule(kind="at", at_ms=timestamp),
    message="提醒我开会",
    delete_after_run=True
)
```
