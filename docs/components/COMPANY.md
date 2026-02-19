# Company 公司管理 (Company Management)

`nanobot/company` 组件实现了 "Agent Company" 的抽象，允许用户通过定义职位（Posts）和工作流来组织多个 Agent 协同工作。

## 核心概念

1.  **Company (公司)**: 虚拟的组织实体，由多个 Worker Agent 组成。
2.  **Post (职位)**: 定义了一个 Worker 的角色、职责、技能和工具权限。
3.  **Worker (员工)**: `Post` 的运行时实例（即 Subagent）。
4.  **Task (任务)**: 分配给 Worker 的具体工作。

## 模块详解

### 1. Company Manager (`manager.py`)

`CompanyManager` 是公司的运营中心，负责管理员工的生命周期和任务分配。

**主要职责：**
- **扫描任务**: 监控 `workspace/tasks` 目录下的新任务文件 (`TASK_*.md`)。
- **任务分发**: 根据文件名或内容判断任务类型，并将其分配给合适的 Post。
- **员工招聘 (Spawn)**: 调用 `SubagentManager` 创建并启动 Worker 实例。
- **进度监控**: 跟踪活跃 Worker 的状态，直到所有任务完成。

**任务分配逻辑:**
1.  **路由优先**: 检查 `routes.json` (如果存在)，匹配文件名正则。
2.  **默认回退**: 如果没有匹配路由，检查 `SKILL.md` 中的 `default_post`。
3.  **丢弃**: 如果两者皆无，则忽略该文件。

### 2. Company Config Loader (`loader.py`)

负责从 Markdown 文件中解析公司的组织架构定义。这也体现了 "Configuration as Code" 和 "Prompt Engineering" 的结合。

#### 支持的配置文件：

- **`companies/<name>/SKILL.md`**: 公司定义入口。
    - 支持字段: `default_post`, `default_task_template`。

- **`company/POSTS.md`**: 定义职位列表。
    - 解析逻辑：查找三级标题 `###` 作为职位定义，提取描述、技能列表、工具列表和上下文 Prompt。
    
- **`company/DOCS_SCHEMA.md`**: 定义文档标准（Schema）。
    - 解析逻辑：提取文档模板、命名规范和存储路径，用于指导 Agent 生成标准化的文档。

### 3. 数据流示例

1.  用户创建任务文件 `workspace/tasks/TASK_WEATHER_001.md`。
2.  `CompanyManager` 扫描到该文件。
3.  识别任务类型，决定由 `Post_Weather_Analyst` 处理。
4.  `CompanyConfigLoader` 加载 `POSTS.md`，获取 `Post_Weather_Analyst` 的定义（Prompt, Skills, Tools）。
5.  `SubagentManager` 启动一个新的 Subagent：
    - 加载对应的 System Prompt。
    - 挂载指定的 Skills 和 Tools。
    - 隔离的 Memory 和 Context。
6.  Worker 执行任务，并生成结果。
7.  Worker 销毁，结果回传给主系统。

## 配置示例 (`POSTS.md`)

```markdown
### 2.1 Weather Analyst (Post_Weather_Analyst)
- **Description**: 负责分析天气数据。
- **Skills**:
  - `weather_service`
- **Tools**: `web_search`
- **Context**:
  > 你是专业的气象分析师...
```
## 简化配置 (Simplified Configuration)

对于大多数专精型公司（如“天气预报公司”），可以直接在 `SKILL.md` 中指定默认岗位，从而免去编写 `routes.json`。

**示例 `SKILL.md`**:
```yaml
name: Weather Co
default_post: Post_Weather_Analyst
default_task_template: |
  请处理以下天气任务:
  文件名: {filename}
  内容: {content}
components:
  posts: "./POSTS.md"
```

启用后，所有放入 `workspace/tasks` 的文件都会自动由 `Post_Weather_Analyst` 处理。
