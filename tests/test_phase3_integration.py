import pytest
import asyncio
from pathlib import Path
from unittest.mock import MagicMock, AsyncMock

from nanobot.company.loader import CompanyConfigLoader
from nanobot.agent.loop import AgentLoop
from nanobot.agent.tools.document_flow import DocumentFlowTool
from nanobot.bus.queue import MessageBus
from nanobot.providers.base import LLMProvider

# Mock Provider
class MockProvider(LLMProvider):
    def get_default_model(self):
        return "mock-model"
    async def chat(self, **kwargs):
        return MagicMock(content="Mock response", has_tool_calls=False)
    async def stream_chat(self, **kwargs):
        yield "Mock"

@pytest.fixture
def workspace_root(tmp_path):
    # Setup company structure
    company_dir = tmp_path / "company"
    company_dir.mkdir()
    
    # Simple schema
    schema = """
## 1. Task Order (Doc_Task_Order)
**文件命名**: `TASK_{ID}_{Title}.md`
**位置**: `workspace/tasks/`
```markdown
# TASK: {Title}
```
"""
    (company_dir / "DOCS_SCHEMA.md").write_text(schema, encoding="utf-8")
    
    # Workspace tasks dir
    (tmp_path / "workspace" / "tasks").mkdir(parents=True)
    
    return tmp_path

@pytest.mark.asyncio
async def test_agent_loop_integration(workspace_root):
    # 1. Setup AgentLoop
    bus = MessageBus()
    provider = MockProvider()
    
    agent = AgentLoop(
        bus=bus,
        provider=provider,
        workspace=workspace_root,
        max_iterations=1
    )
    
    # Verify DocumentFlowTool is registered
    assert agent.tools.get("document_flow") is not None
    
    # 2. Test Inbox Check (Manual Trigger)
    # Create a dummy task file
    task_file = workspace_root / "workspace" / "tasks" / "TASK_123_Test.md"
    task_file.write_text("# TASK: Test", encoding="utf-8")
    
    # Run _check_inbox (it logs info, so we just verify it runs without error)
    await agent._check_inbox()
    
    # 3. Test Subagent Tool Access
    # Spawn a subagent config and check if it gets the tool
    subagent = agent.subagents
    # We can't easily query internal state of subagent manager's private methods
    # But we can check if _register_tools adds it
    
    from nanobot.agent.tools.registry import ToolRegistry
    registry = ToolRegistry()
    subagent._register_tools(registry, post=None)
    
    assert registry.get("document_flow") is not None
