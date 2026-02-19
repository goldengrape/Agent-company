"""MCP (Model Context Protocol) 单元测试。

测试覆盖：
- MCPToolWrapper 属性与执行
- connect_mcp_servers 连接逻辑
- MCPServerConfig 配置 schema
- AgentLoop MCP 集成（惰性连接、清理）
"""

import asyncio
from contextlib import AsyncExitStack
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from nanobot.agent.tools.mcp import MCPToolWrapper, connect_mcp_servers
from nanobot.agent.tools.registry import ToolRegistry
from nanobot.config.schema import MCPServerConfig, ToolsConfig


# ---------------------------------------------------------------------------
# Fakes / Helpers
# ---------------------------------------------------------------------------

@dataclass
class FakeToolDef:
    """模拟 MCP SDK 的 tool definition 对象。"""
    name: str = "echo"
    description: str = "Echo input back"
    inputSchema: dict = field(default_factory=lambda: {
        "type": "object",
        "properties": {"text": {"type": "string"}},
        "required": ["text"],
    })


@dataclass
class FakeCallToolResult:
    """模拟 session.call_tool 返回结果。"""
    content: list = field(default_factory=list)


@dataclass
class FakeListToolsResult:
    """模拟 session.list_tools 返回结果。"""
    tools: list = field(default_factory=list)


def _make_text_content(text: str = "hello world"):
    """创建与 mcp.types.TextContent isinstance 检查兼容的 fake 对象。"""
    from mcp import types
    return types.TextContent(type="text", text=text)


@dataclass
class FakeImageContent:
    """模拟非文本内容块（不是 TextContent 实例）。"""
    type: str = "image"
    data: str = "base64data"


class FakeSession:
    """模拟 MCP ClientSession，支持 async context manager。"""

    def __init__(self, tools: list[FakeToolDef] | None = None,
                 call_result: FakeCallToolResult | None = None):
        self._tools = tools or []
        self._call_result = call_result or FakeCallToolResult(
            content=[_make_text_content()]
        )

    async def initialize(self):
        pass

    async def list_tools(self):
        return FakeListToolsResult(tools=self._tools)

    async def call_tool(self, name: str, arguments: dict | None = None):
        return self._call_result

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        pass


# ============================================================================
# MCPToolWrapper 测试
# ============================================================================

class TestMCPToolWrapper:
    """MCPToolWrapper 属性与行为测试。"""

    def _make_wrapper(self, server_name="test_server",
                      tool_def: FakeToolDef | None = None,
                      session: FakeSession | None = None) -> MCPToolWrapper:
        return MCPToolWrapper(
            session=session or FakeSession(),
            server_name=server_name,
            tool_def=tool_def or FakeToolDef(),
        )

    def test_name_format(self):
        """工具名称应为 mcp_{server}_{tool}。"""
        wrapper = self._make_wrapper("github", FakeToolDef(name="get_repo"))
        assert wrapper.name == "mcp_github_get_repo"

    def test_description_from_tool_def(self):
        """描述应来自 tool definition。"""
        wrapper = self._make_wrapper(tool_def=FakeToolDef(description="Do something"))
        assert wrapper.description == "Do something"

    def test_description_fallback_to_name(self):
        """描述为空时应回退到工具名称。"""
        wrapper = self._make_wrapper(tool_def=FakeToolDef(name="my_tool", description=None))
        assert wrapper.description == "my_tool"

    def test_parameters_from_input_schema(self):
        """参数 schema 应直接来自 inputSchema。"""
        schema = {"type": "object", "properties": {"x": {"type": "integer"}}}
        wrapper = self._make_wrapper(tool_def=FakeToolDef(inputSchema=schema))
        assert wrapper.parameters == schema

    def test_parameters_default_when_none(self):
        """inputSchema 为 None 时应返回默认空 schema。"""
        wrapper = self._make_wrapper(tool_def=FakeToolDef(inputSchema=None))
        assert wrapper.parameters == {"type": "object", "properties": {}}

    def test_to_schema_openai_format(self):
        """to_schema() 应输出符合 OpenAI 函数调用格式的字典。"""
        wrapper = self._make_wrapper("srv", FakeToolDef(name="ping", description="Ping"))
        schema = wrapper.to_schema()
        assert schema["type"] == "function"
        assert schema["function"]["name"] == "mcp_srv_ping"
        assert schema["function"]["description"] == "Ping"
        assert "properties" in schema["function"]["parameters"]

    @pytest.mark.asyncio
    async def test_execute_returns_text(self):
        """execute() 应返回文本结果。"""
        result = FakeCallToolResult(content=[_make_text_content("pong")])
        session = FakeSession(call_result=result)
        wrapper = self._make_wrapper(session=session)
        output = await wrapper.execute(text="ping")
        assert output == "pong"

    @pytest.mark.asyncio
    async def test_execute_multiple_blocks(self):
        """execute() 应正确合并多个文本块。"""
        result = FakeCallToolResult(content=[
            _make_text_content("line1"),
            _make_text_content("line2"),
        ])
        session = FakeSession(call_result=result)
        wrapper = self._make_wrapper(session=session)
        output = await wrapper.execute()
        assert output == "line1\nline2"

    @pytest.mark.asyncio
    async def test_execute_empty_result(self):
        """无内容时应返回 '(no output)'。"""
        result = FakeCallToolResult(content=[])
        session = FakeSession(call_result=result)
        wrapper = self._make_wrapper(session=session)
        output = await wrapper.execute()
        assert output == "(no output)"

    @pytest.mark.asyncio
    async def test_execute_non_text_content(self):
        """非文本内容块应通过 str() 转换。"""
        result = FakeCallToolResult(content=[FakeImageContent()])
        session = FakeSession(call_result=result)
        wrapper = self._make_wrapper(session=session)
        output = await wrapper.execute()
        # 应包含 FakeImageContent 的字符串表示
        assert "FakeImageContent" in output or "image" in output.lower()

    @pytest.mark.asyncio
    async def test_execute_mixed_content(self):
        """混合内容：文本 + 非文本应正确处理。"""
        result = FakeCallToolResult(content=[
            _make_text_content("text part"),
            FakeImageContent(),
        ])
        session = FakeSession(call_result=result)
        wrapper = self._make_wrapper(session=session)
        output = await wrapper.execute()
        assert "text part" in output


# ============================================================================
# connect_mcp_servers 测试
# ============================================================================

class TestConnectMCPServers:
    """connect_mcp_servers 连接与注册逻辑测试。"""

    @pytest.mark.asyncio
    async def test_stdio_connect_registers_tools(self):
        """stdio 模式应连接并注册工具到 registry。"""
        tool_defs = [FakeToolDef(name="tool_a"), FakeToolDef(name="tool_b")]
        fake_session = FakeSession(tools=tool_defs)
        cfg = MCPServerConfig(command="echo", args=["hello"])
        registry = ToolRegistry()

        with patch("mcp.client.stdio.stdio_client") as mock_stdio, \
             patch("mcp.ClientSession") as mock_cs:
            # stdio_client returns (read, write) as async context manager
            mock_stdio.return_value.__aenter__ = AsyncMock(return_value=(MagicMock(), MagicMock()))
            mock_stdio.return_value.__aexit__ = AsyncMock(return_value=False)

            mock_cs.return_value.__aenter__ = AsyncMock(return_value=fake_session)
            mock_cs.return_value.__aexit__ = AsyncMock(return_value=False)

            stack = AsyncExitStack()
            async with stack:
                await connect_mcp_servers({"my_server": cfg}, registry, stack)

            assert registry.has("mcp_my_server_tool_a")
            assert registry.has("mcp_my_server_tool_b")
            assert len(registry) >= 2

    @pytest.mark.asyncio
    async def test_http_connect_registers_tools(self):
        """HTTP 模式应连接并注册工具到 registry。"""
        tool_defs = [FakeToolDef(name="remote_tool")]
        fake_session = FakeSession(tools=tool_defs)
        cfg = MCPServerConfig(url="http://localhost:8080/mcp")
        registry = ToolRegistry()

        with patch("mcp.client.streamable_http.streamable_http_client") as mock_http, \
             patch("mcp.ClientSession") as mock_cs:
            mock_http.return_value.__aenter__ = AsyncMock(
                return_value=(MagicMock(), MagicMock(), MagicMock())
            )
            mock_http.return_value.__aexit__ = AsyncMock(return_value=False)

            mock_cs.return_value.__aenter__ = AsyncMock(return_value=fake_session)
            mock_cs.return_value.__aexit__ = AsyncMock(return_value=False)

            stack = AsyncExitStack()
            async with stack:
                await connect_mcp_servers({"remote": cfg}, registry, stack)

            assert registry.has("mcp_remote_remote_tool")

    @pytest.mark.asyncio
    async def test_skip_when_no_command_or_url(self):
        """command 和 url 都为空时应跳过，不注册任何工具。"""
        cfg = MCPServerConfig()  # 默认 command="" url=""
        registry = ToolRegistry()

        stack = AsyncExitStack()
        async with stack:
            await connect_mcp_servers({"empty": cfg}, registry, stack)

        assert len(registry) == 0

    @pytest.mark.asyncio
    async def test_empty_servers_dict(self):
        """空服务器字典不应报错。"""
        registry = ToolRegistry()
        stack = AsyncExitStack()
        async with stack:
            await connect_mcp_servers({}, registry, stack)
        assert len(registry) == 0

    @pytest.mark.asyncio
    async def test_connection_failure_graceful(self):
        """连接失败时应优雅处理异常，不中断其他服务器。"""
        cfg = MCPServerConfig(command="nonexistent_cmd")
        registry = ToolRegistry()

        with patch("mcp.client.stdio.stdio_client") as mock_stdio:
            mock_stdio.side_effect = Exception("Connection refused")

            stack = AsyncExitStack()
            async with stack:
                # 不应抛出异常
                await connect_mcp_servers({"broken": cfg}, registry, stack)

            assert len(registry) == 0

    @pytest.mark.asyncio
    async def test_multiple_servers(self):
        """多个服务器应各自独立注册工具。"""
        tool_a = [FakeToolDef(name="alpha")]
        tool_b = [FakeToolDef(name="beta")]
        session_a = FakeSession(tools=tool_a)
        session_b = FakeSession(tools=tool_b)

        cfg_a = MCPServerConfig(command="cmd_a")
        cfg_b = MCPServerConfig(command="cmd_b")
        registry = ToolRegistry()

        call_count = 0

        async def fake_stdio_enter(*args, **kwargs):
            return (MagicMock(), MagicMock())

        async def fake_cs_enter(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            return session_a if call_count == 1 else session_b

        with patch("mcp.client.stdio.stdio_client") as mock_stdio, \
             patch("mcp.ClientSession") as mock_cs:
            mock_stdio.return_value.__aenter__ = fake_stdio_enter
            mock_stdio.return_value.__aexit__ = AsyncMock(return_value=False)
            mock_cs.return_value.__aenter__ = fake_cs_enter
            mock_cs.return_value.__aexit__ = AsyncMock(return_value=False)

            stack = AsyncExitStack()
            async with stack:
                await connect_mcp_servers(
                    {"server_a": cfg_a, "server_b": cfg_b}, registry, stack
                )

            assert registry.has("mcp_server_a_alpha")
            assert registry.has("mcp_server_b_beta")


# ============================================================================
# MCPServerConfig 配置 Schema 测试
# ============================================================================

class TestMCPServerConfig:
    """MCPServerConfig 配置模型测试。"""

    def test_default_values(self):
        """默认值应为空字符串和空列表/字典。"""
        cfg = MCPServerConfig()
        assert cfg.command == ""
        assert cfg.args == []
        assert cfg.env == {}
        assert cfg.url == ""

    def test_stdio_config(self):
        """stdio 配置应正确设置 command 和 args。"""
        cfg = MCPServerConfig(command="npx", args=["-y", "@mcp/server"])
        assert cfg.command == "npx"
        assert cfg.args == ["-y", "@mcp/server"]

    def test_http_config(self):
        """HTTP 配置应正确设置 url。"""
        cfg = MCPServerConfig(url="http://localhost:3000/mcp")
        assert cfg.url == "http://localhost:3000/mcp"

    def test_env_vars(self):
        """环境变量应正确传递。"""
        cfg = MCPServerConfig(
            command="docker",
            args=["run", "-i", "mcp-server"],
            env={"API_KEY": "secret123"},
        )
        assert cfg.env["API_KEY"] == "secret123"

    def test_tools_config_mcp_servers_field(self):
        """ToolsConfig 的 mcp_servers 字段应为空字典默认值。"""
        tools = ToolsConfig()
        assert tools.mcp_servers == {}

    def test_tools_config_with_servers(self):
        """ToolsConfig 应能包含多个 MCP 服务器配置。"""
        tools = ToolsConfig(mcp_servers={
            "github": MCPServerConfig(command="docker", args=["run", "ghcr.io/github/github-mcp-server"]),
            "filesystem": MCPServerConfig(command="npx", args=["-y", "@mcp/filesystem"]),
        })
        assert "github" in tools.mcp_servers
        assert "filesystem" in tools.mcp_servers
        assert tools.mcp_servers["github"].command == "docker"


# ============================================================================
# AgentLoop MCP 集成测试
# ============================================================================

class TestAgentLoopMCPIntegration:
    """AgentLoop 中 MCP 集成逻辑的单元测试。"""

    def _make_agent_loop(self, mcp_servers=None):
        """创建最小化的 AgentLoop 用于测试 MCP 集成。"""
        from nanobot.agent.loop import AgentLoop
        from nanobot.bus.queue import MessageBus

        bus = MessageBus()
        provider = MagicMock()
        provider.get_default_model.return_value = "test/model"

        import tempfile
        workspace = Path(tempfile.mkdtemp())

        loop = AgentLoop(
            bus=bus,
            provider=provider,
            workspace=workspace,
            mcp_servers=mcp_servers,
        )
        return loop

    def test_mcp_not_connected_on_init(self):
        """初始化后 MCP 不应立即连接（惰性连接）。"""
        loop = self._make_agent_loop(mcp_servers={"s": MCPServerConfig(command="echo")})
        assert loop._mcp_connected is False
        assert loop._mcp_stack is None

    def test_no_mcp_servers_empty_dict(self):
        """无 MCP 配置时 _mcp_servers 应为空字典。"""
        loop = self._make_agent_loop()
        assert loop._mcp_servers == {}

    @pytest.mark.asyncio
    async def test_connect_mcp_skips_when_empty(self):
        """_mcp_servers 为空时 _connect_mcp 应直接跳过。"""
        loop = self._make_agent_loop()
        await loop._connect_mcp()
        assert loop._mcp_connected is False
        assert loop._mcp_stack is None

    @pytest.mark.asyncio
    async def test_connect_mcp_only_once(self):
        """_connect_mcp 应只连接一次（幂等性）。"""
        loop = self._make_agent_loop(mcp_servers={"s": MCPServerConfig(command="echo")})

        with patch("nanobot.agent.tools.mcp.connect_mcp_servers", new_callable=AsyncMock) as mock_connect:
            await loop._connect_mcp()
            await loop._connect_mcp()  # 第二次调用
            assert mock_connect.call_count == 1
            assert loop._mcp_connected is True

    @pytest.mark.asyncio
    async def test_close_mcp_cleans_up(self):
        """close_mcp 应清理 _mcp_stack。"""
        loop = self._make_agent_loop(mcp_servers={"s": MCPServerConfig(command="echo")})

        with patch("nanobot.agent.tools.mcp.connect_mcp_servers", new_callable=AsyncMock):
            await loop._connect_mcp()
            assert loop._mcp_stack is not None

            await loop.close_mcp()
            assert loop._mcp_stack is None

    @pytest.mark.asyncio
    async def test_close_mcp_noop_when_not_connected(self):
        """未连接时 close_mcp 应无操作，不报错。"""
        loop = self._make_agent_loop()
        # 不应抛出异常
        await loop.close_mcp()
        assert loop._mcp_stack is None


# ============================================================================
# MCPToolWrapper 在 ToolRegistry 中的集成测试
# ============================================================================

class TestMCPToolInRegistry:
    """MCPToolWrapper 与 ToolRegistry 的集成。"""

    @pytest.mark.asyncio
    async def test_register_and_execute(self):
        """MCP 工具应能正常在 registry 中注册并执行。"""
        result = FakeCallToolResult(content=[_make_text_content("executed!")])
        session = FakeSession(call_result=result)
        wrapper = MCPToolWrapper(session, "srv", FakeToolDef(name="run"))

        registry = ToolRegistry()
        registry.register(wrapper)

        assert registry.has("mcp_srv_run")
        output = await registry.execute("mcp_srv_run", {"text": "go"})
        assert output == "executed!"

    @pytest.mark.asyncio
    async def test_tool_definitions_include_mcp(self):
        """get_definitions() 应包含 MCP 工具定义。"""
        wrapper = MCPToolWrapper(FakeSession(), "s", FakeToolDef(name="t"))
        registry = ToolRegistry()
        registry.register(wrapper)

        defs = registry.get_definitions()
        assert len(defs) == 1
        assert defs[0]["function"]["name"] == "mcp_s_t"
