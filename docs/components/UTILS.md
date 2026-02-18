# 通用工具 (Utils)

Utils 模块封装了系统及其组件使用的通用辅助函数。主要位于 `nanobot/utils/helpers.py`。

## 1. 核心功能

### 1.1 文件系统辅助
- **`ensure_dir(path: Path) -> Path`**: 确保目录存在，如果不存在则创建（包含父目录）。返回 Path 对象。

### 1.2 文本与数据处理
- **`clean_json_markdown(text: str) -> str`**: 从 Markdown 代码块（如 ` ```json ... ``` `）中提取原始 JSON 字符串，常用于处理 LLM 产生的格式化输出。
- **`truncate_text(text: str, max_length: int = 100) -> str`**: 截断长文本并添加省略号，用于日志记录或摘要显示。

### 1.3 计费与统计
- **`calculate_cost(model: str, usage: dict) -> float`**: 根据模型名称和 Token 用量计算大致的 API 调用成本（美元）。支持 GPT-4, GPT-3.5, Claude 3 等主流模型的定价策略。
- **`format_token_usage(usage: dict) -> str`**: 将 Token 用量字典格式化为易读的字符串（如 `Prompt: 100, Completion: 50, Total: 150`）。

## 2. 使用示例

```python
from nanobot.utils.helpers import ensure_dir, clean_json_markdown

# 确保日志目录存在
log_dir = ensure_dir(workspace / "logs")

# 解析 LLM 返回的 JSON
raw_response = "Here is the data:\n```json\n{\"id\": 1}\n```"
json_str = clean_json_markdown(raw_response)
data = json.loads(json_str) 
```
