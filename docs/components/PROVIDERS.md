# 模型服务 (Providers)

Providers 模块负责管理大型语言模型 (LLM) 和其他 AI 服务的连接与调用。它通过统一的接口屏蔽了不同模型供应商 (OpenAI, Anthropic, Google, Local LLMs 等) 的 API 差异。

## 1. 核心架构

所有 LLM Provider 都实现了 `LLMProvider` 抽象基类。

### 1.1 LLMProvider 接口

文件位置: `nanobot/providers/base.py`

`LLMProvider` 定义了标准化的交互方法：

- **`chat(messages, tools, ...)`**: 发送对话请求，支持 Function Calling (Tools)。
- **`complete(prompt, ...)`**: 发送文本补全请求 (Legacy)。
- **`embed(text)`**: 获取文本的向量表示 (Embeddings)。
- **`get_default_model()`**: 获取该 Provider 配置的默认模型名称。

## 2. 支持的 Provider

### 2.1 LiteLLM Provider (推荐)

文件位置: `nanobot/providers/litellm_provider.py`

这是系统的主力 Provider，基于 [LiteLLM](https://github.com/BerriAI/litellm) 库构建。

- **功能**: 支持 100+ 种主流 LLM，包括 GPT-4, Claude 3, Gemini, Mistral, 以及通过 Ollama 运行的本地模型。
- **配置**: 通过环境变量或配置文件设置模型名称（如 `gpt-4o`, `claude-3-opus`, `ollama/llama3`）。
- **优势**: 统一了 Token 计算、重试逻辑和错误处理。

### 2.2 OpenAI Codex Provider

文件位置: `nanobot/providers/openai_codex_provider.py`

直接集成 OpenAI 官方 SDK 的 Provider。

- **用途**: 主要用于需要特定 OpenAI 高级特性或在 LiteLLM 覆盖不到的边缘情况。
- **配置**: 需要 `OPENAI_API_KEY`。

### 2.3 Transcription Provider

文件位置: `nanobot/providers/transcription.py`

专门处理音频转文字 (STT) 任务的 Provider。

- **功能**: 将音频文件转换为文本，通常用于语音输入处理。

## 3. Provider 注册与工厂 (Registry)

文件位置: `nanobot/providers/registry.py`

`ProviderRegistry` 负责根据配置实例化具体的 Provider。系统启动时会读取 `config.yaml` 中的 `llm` 部分，决定初始化哪个 Provider。

## 4. 配置示例

在 `config.yaml` 中配置：

```yaml
llm:
  provider: "litellm"  # 或 "openai"
  model: "gpt-4o"      # 默认模型
  temperature: 0.7
  api_key: "${OPENAI_API_KEY}"
  api_base: null       # 可选，用于代理或本地服务
```
