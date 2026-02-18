# 通信渠道 (Channels)

Channels 模块是 Nanobot 与外部世界沟通的桥梁。它定义了统一的接口来适配不同的即时通讯 (IM) 平台，使得 Agent 可以通过统一的消息总线 (Message Bus) 接收指令和发送回复，而无需关心底层的 API 差异。

## 1. 核心架构

所有 Channel 都继承自 `BaseChannel` 抽象基类，并由 `ChannelManager` 统一加载和管理。

### 1.1 BaseChannel 接口

文件位置: `nanobot/channels/base.py`

`BaseChannel` 定义了以下核心方法：

- **`start()`**: 启动 Channel，建立连接或开始轮询，监听入站消息。
- **`stop()`**: 关闭连接，释放资源。
- **`send(msg)`**: 发送出站消息 (`OutboundMessage`) 到指定 Chat ID。
- **`is_allowed(sender_id)`**: 权限检查，验证发送者是否在允许列表中。

### 1.2 消息流转
- **入站 (Inbound)**: Channel 收到消息 -> 封装为 `InboundMessage` -> 发布到 `MessageBus`。
- **出站 (Outbound)**: Agent 发送消息 -> `MessageBus` 路由 -> Channel 调用 `send()` 方法发送。

## 2. 支持的渠道

目前系统支持以下通信渠道：

| 渠道 | 文件 | 描述 | 配置项 (Config) |
| :--- | :--- | :--- | :--- |
| **Console** | (Built-in) | 命令行交互模式，直接在终端输入输出。 | 无 |
| **Discord** | `discord.py` | 通过 Discord Bot API 对接。需要 Bot Token。 | `token`, `allow_from` |
| **Slack** | `slack.py` | 通过 Slack App / Socket Mode 对接。 | `app_token`, `bot_token` |
| **Telegram** | `telegram.py` | 通过 Telegram Bot API (Long Polling) 对接。 | `token`, `allow_from` |
| **Email** | `email.py` | 通过 SMTP/IMAP 协议收发邮件。 | `smtp_server`, `imap_server`, `email`, `password` |
| **Feishu** | `feishu.py` | 对接飞书/Lark 开放平台 (企业自建应用)。 | `app_id`, `app_secret` |
| **DingTalk** | `dingtalk.py` | 对接钉钉机器人。 | `client_id`, `client_secret` |
| **WeChat** | `mochat.py` | 基于 Hook 或模拟协议对接微信 (MoChat)。 | `server_url` |
| **WhatsApp** | `whatsapp.py` | 对接 WhatsApp Business API。 | `api_key`, `phone_number_id` |
| **QQ** | `qq.py` | 对接 QQ 机器人 (go-cqhttp adapter 等)。 | `ws_url` |

## 3. 配置说明

在 `config.yaml` 或环境变量中配置启用的 Channel。

```yaml
channels:
  telegram:
    enabled: true
    token: "YOUR_TELEGRAM_BOT_TOKEN"
    allow_from: ["user_id_123"]  # 仅允许特定用户互动

  slack:
    enabled: false
    app_token: "xapp-..."
    bot_token: "xoxb-..."
```

## 4. 开发新 Channel

要添加新的 Channel 支持：

1. 在 `nanobot/channels/` 下创建新文件（如 `matrix.py`）。
2. 继承 `BaseChannel` 类。
3. 实现 `start`, `stop`, `send` 方法。
4. 在 `nanobot/channels/manager.py` 中注册该 Channel。
