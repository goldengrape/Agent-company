# Session 会话管理 (Session Management)

`nanobot/session` 组件负责管理多轮对话的状态持久化。它允许 Agent 同时与多个用户或在多个频道中保持独立的上下文，互不干扰。

## 核心概念

- **Session (会话)**: 一个独立的对话上下文，包含一组历史消息。
- **Session Key**: 唯一标识符，通常格式为 `{channel}:{chat_id}` (e.g., `telegram:123456789`, `cli:direct`)。

## 存储机制

会话数据以 JSON 格式存储在 `workspace/memory/sessions/` 目录下。文件名是 Session Key 的 URL 安全编码版本。

### 数据结构 (`SessionData`)

- `id`: Session Key
- `messages`: 消息列表 `List[Dict[str, Any]]` (OpenAI 格式)
- `created_at`: 创建时间戳
- `updated_at`: 最后更新时间戳
- `metadata`: 附加信息 (如用户名称、最后使用的模型等)

## Session Manager (`manager.py`)

`SessionManager` 类提供了对会话的 CRUD 操作。

### 主要方法

- `load_session(session_key)`: 加载指定会话。如果不存在，则创建一个新的空会话。
- `save_session(session_key, messages)`: 保存会话状态。通常在每一轮对话结束后调用。
- `list_sessions()`: 列出所有活跃的会话。
- `clear_session(session_key)`: 清空特定会话的历史记录。

### 上下文管理

Nanobot 采用 **按需加载** 的策略：
1.  收到消息时，根据 Channel 和 Sender ID 生成 `session_key`。
2.  `SessionManager` 从磁盘读取对应的历史记录。
3.  `ContextBuilder` 将这些历史记录通过 `build_messages` 方法构建进 Prompt。
    - 注意：`MEMORY.md` (长期记忆) 是全局共享的，而 `Session History` (短期记忆) 是隔离的。
4.  LLM 生成回复。
5.  新的用户消息和助手回复被追加到列表中。
6.  `SessionManager` 将更新后的列表写回磁盘。

## 代码示例

### 集成到 Agent Loop

```python
# 1. 确定 Session Key
session_key = f"{channel}:{chat_id}"

# 2. 加载历史
history = session_manager.load_session(session_key)

# 3. 处理对话
# ... (LLM 交互) ...

# 4. 保存更新后的历史
session_manager.save_session(session_key, updated_history)
```

### 清除记忆 (CLI 命令)

CLI 可以通过调用 Session Manager 来实现 `/reset` 指令：

```python
if user_input == "/reset":
    session_manager.clear_session(current_session_key)
    print("Memory cleared.")
```
