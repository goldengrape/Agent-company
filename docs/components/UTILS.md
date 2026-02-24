# 通用工具 (Utils)

本文档对应当前实现：`nanobot/utils/helpers.py`。

## 当前存在的函数

- `ensure_dir(path)`
- `get_data_path()`
- `get_workspace_path(workspace=None)`
- `get_sessions_path()`
- `get_skills_path(workspace=None)`
- `timestamp()`
- `truncate_string(s, max_len=100, suffix="...")`
- `safe_filename(name)`
- `parse_session_key(key)`

## 说明

- 这些函数主要负责路径初始化、字符串安全化、会话键解析。
- 历史文档中出现的 `clean_json_markdown`、`truncate_text`、`calculate_cost`、`format_token_usage` 不在当前实现中，应视为旧版信息。
