# Session 会话管理 (Session Management)

本文档对应当前实现：`nanobot/session/manager.py`。

## 存储位置

会话文件存储在：`~/.nanobot/sessions/`

注意：不是 `workspace/memory/sessions/`。

## 文件格式

每个会话是一个 `.jsonl` 文件：
- 第 1 行：`_type=metadata` 元数据
- 后续行：消息记录（append-only）

会话键（如 `telegram:123456`）会转换成安全文件名存储。

## 数据结构

`Session` 包含：
- `key`
- `messages`
- `created_at`
- `updated_at`
- `metadata`
- `last_consolidated`

## SessionManager 主要方法

- `get_or_create(key)`
- `save(session)`
- `list_sessions()`
- `invalidate(key)`

## 设计要点

- 消息历史默认 append-only，便于缓存与审计。
- 内存压缩/归档不会直接篡改已有消息记录的语义。
