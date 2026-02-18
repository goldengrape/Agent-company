# CLI 命令行接口 (Command Line Interface)

`nanobot/cli` 组件提供了与系统交互的主要入口。它基于 `Typer` 构建，支持丰富的终端交互体验（Rich, Prompt Toolkit）。

## 命令概览

主要命令结构如下：

```bash
nanobot
├── onboard     # 初始化配置和工作区
├── agent       # 直接与 Agent 对话
├── gateway     # 启动网关服务 (Gateway Service)
├── company     # 公司管理相关指令
│   ├── init    # 初始化公司结构
│   └── run     # 运行公司经理 (处理任务)
├── channels    # 渠道管理相关指令
│   ├── status  # 查看渠道状态
│   └── login   # 扫码登录 (如 WhatsApp)
└── cron        # 定时任务管理
    ├── list    # 列出任务
    └── add     # 添加任务
```

## 核心命令详解

### 1. `onboard` (初始化)

这是用户使用 Nanobot 的第一步。
- **功能**:
    - 创建默认配置文件 `~/.nanobot/config.json`。
    - 创建工作区目录 `~/.nanobot/workspace`。
    - 生成 Bootstrap 模板文件 (`AGENTS.md`, `SOUL.md`, `USER.md`)。
    - 初始化记忆文件 (`MEMORY.md`, `HISTORY.md`)。

### 2. `agent` (对话)

直接在终端与 Agent 进行交互。

- **交互模式**: 运行 `nanobot agent` 进入 REPL 模式。支持上下键历史记录、多行粘贴。
- **单次模式**: `nanobot agent -m "Hello"` 执行一次并退出，适合脚本调用。
- **参数**:
    - `--logs`: 开启详细运行日志（调试用）。
    - `--no-markdown`:虽然默认渲染 Markdown，但可关闭以获取原始文本。

### 3. `gateway` (网关服务)

启动常驻后台的服务进。

- **功能**:
    - 启动 `Message Bus`。
    - 启动 `Agent Loop`。
    - 启动外部通信 `Channel Manager` (Telegram, WhatsApp 等)。
    - 启动 `Cron Service` (定时任务) 和 `Heartbeat Service` (心跳检测)。
- **端口**: 默认为 `18790`。

### 4. `company` (公司管理)

- `init`: 确保 `workspace/company` 目录存在。
- `run`: 手动触发一次公司经理的任务扫描循环 (`CompanyManager.run()`)。这是目前触发任务处理的主要方式。

## 技术实现细节

- **框架**: 使用 `Typer` 定义命令行参数。
- **UI 渲染**: 使用 `Rich` 库渲染 Markdown、表格和彩色输出。
- **交互输入**: 使用 `prompt_toolkit` 处理复杂的终端输入（如多行编辑），解决了标准 `input()` 的诸多限制。
- **异步支持**: 虽然 Typer 本身是同步的，但内部通过 `asyncio.run()` 调用异步的 Agent 和 Service 逻辑。
