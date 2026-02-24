# 通信渠道 (Channels)

本文档对应当前实现：`nanobot/channels/base.py`、`nanobot/channels/manager.py`。

## 核心接口

所有渠道继承 `BaseChannel`，实现：
- `start()`
- `stop()`
- `send(msg)`
- `is_allowed(sender_id)`

## 渠道管理器

`ChannelManager` 根据配置动态初始化启用渠道，并负责：
- 启动所有渠道（`start_all`）
- 停止所有渠道（`stop_all`）
- 监听 Message Bus 的 outbound 队列并分发

## 当前支持渠道

- telegram
- whatsapp
- discord
- feishu
- mochat
- dingtalk
- email
- slack
- qq

具体实现位于 `nanobot/channels/*.py`。

## 消息流

- 入站：Channel -> `InboundMessage` -> MessageBus
- 出站：Agent/系统 -> `OutboundMessage` -> ChannelManager -> 对应 Channel `send()`

## 配置来源

当前配置文件是 JSON：`config.json`。
渠道配置位于 `channels` 节点，例如：

```json
{
  "channels": {
    "telegram": {
      "enabled": true,
      "token": "...",
      "allowFrom": ["123456"]
    },
    "whatsapp": {
      "enabled": false,
      "bridgeUrl": "ws://localhost:3001"
    }
  }
}
```

字段定义见：`nanobot/config/schema.py`。
