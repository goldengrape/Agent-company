# 模型服务 (Providers)

本文档对应当前实现：`nanobot/providers/base.py`、`nanobot/providers/registry.py`、`nanobot/providers/litellm_provider.py`、`nanobot/providers/openai_codex_provider.py`。

## 统一接口

`LLMProvider` 定义统一异步接口：
- `chat(messages, tools, model, max_tokens, temperature)`
- `get_default_model()`

返回结构为 `LLMResponse`，可包含普通文本与 tool calls。

## Provider 选择机制

Provider 元数据集中在 `ProviderSpec`（`registry.py`）中，作为单一事实来源。

匹配顺序：
1. 按模型关键词匹配标准 provider。
2. 回退到可用 provider（网关优先，按注册表顺序）。
3. OAuth provider（如 `openai_codex`）需显式选择，不参与普通 key 回退。

网关/本地识别支持：
- `provider_name` 直接命中
- `api_key` 前缀识别
- `api_base` 关键字识别

## 当前配置格式

配置使用 JSON，不使用 `config.yaml`。
关键节点：
- `agents.defaults.model`
- `providers.<provider>.apiKey`
- `providers.<provider>.apiBase`
- `providers.<provider>.extraHeaders`

示例：

```json
{
  "agents": {
    "defaults": {
      "model": "anthropic/claude-opus-4-5"
    }
  },
  "providers": {
    "openrouter": {
      "apiKey": "sk-or-...",
      "apiBase": "https://openrouter.ai/api/v1"
    }
  }
}
```

## OAuth Provider

- `openai_codex`
- `github_copilot`

CLI 登录入口：
- `nanobot provider login openai-codex`
