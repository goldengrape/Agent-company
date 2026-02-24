
import pytest
import shutil
from pathlib import Path
from unittest.mock import MagicMock, patch, AsyncMock

from nanobot.agent.memory import MemoryStore
from nanobot.agent.context import ContextBuilder
from nanobot.agent.subagent import SubagentManager
from nanobot.company.loader import Post

@pytest.fixture
def mock_workspace(tmp_path):
    # Setup workspace structure
    (tmp_path / "workspace" / "memory").mkdir(parents=True)
    (tmp_path / "company").mkdir()
    (tmp_path / "skills").mkdir()
    
    # Create dummy bootstrap files
    for f in ["AGENTS.md", "SOUL.md", "USER.md", "TOOLS.md", "IDENTITY.md"]:
        (tmp_path / f).write_text(f"# {f}\nContent", encoding="utf-8")
        
    return tmp_path

def test_memory_store_isolation(mock_workspace):
    """Test that MemoryStore creates isolated paths when agent_id is provided."""
    # 1. Main Agent (no ID)
    main_memory = MemoryStore(mock_workspace)
    assert main_memory.memory_dir == mock_workspace / "workspace" / "memory"
    
    # 2. Worker Agent (with ID)
    worker_id = "worker_123"
    worker_memory = MemoryStore(mock_workspace, agent_id=worker_id)
    assert worker_memory.memory_dir == mock_workspace / "workspace" / "memory" / "workers" / worker_id
    
    # Verify directories created
    assert (mock_workspace / "workspace" / "memory").exists()
    assert (mock_workspace / "workspace" / "memory" / "workers" / worker_id).exists()

def test_context_builder_identity_isolation(mock_workspace):
    """Test that ContextBuilder generates strict identity for Posts."""
    builder = ContextBuilder(mock_workspace)
    
    # specific_post_id
    post_id = "Post_Tester"
    
    # Mock company loader
    builder.company_loader = MagicMock()
    builder.company_loader.posts = {
        post_id: Post(
            title="Tester",
            description="A tester agent",
            skills=[],
            tools=[],
            context_prompt="You test things."
        )
    }
    
    identity = builder.get_agent_identity(post_id)
    
    # Assertions for STRICT isolation
    assert "# Agent Identity: Tester" in identity
    assert "You test things." in identity
    # Should NOT contain the generic base identity
    assert "You are nanobot, a helpful AI assistant" not in identity
    assert "# nanobot 🐈" not in identity

def test_context_builder_memory_link(mock_workspace):
    """Test that ContextBuilder uses the correct isolated memory store."""
    worker_id = "worker_456"
    builder = ContextBuilder(mock_workspace, agent_id=worker_id)
    
    # Verify internal memory store path
    assert builder.memory.memory_dir == mock_workspace / "workspace" / "memory" / "workers" / worker_id

@pytest.mark.asyncio
async def test_subagent_manager_uses_isolation(mock_workspace):
    """Test that SubagentManager spawns workers with isolated components."""
    # We need to mock _run_subagent to inspect how it sets up items, 
    # but that's an internal method. Instead, we can verify the side effects
    # or mock the classes it instantiates if we patch them.
    
    with patch("nanobot.agent.subagent.ContextBuilder") as MockContextBuilder, \
         patch("nanobot.agent.subagent.SkillsLoader") as MockSkillsLoader, \
         patch("nanobot.agent.subagent.SubagentManager._build_subagent_prompt") as mock_build_prompt:

        # Setup
        provider = MagicMock()
        provider.get_default_model.return_value = "gpt-4"
        
        # Mock chat to be async and return a simple response
        mock_response = MagicMock()
        mock_response.has_tool_calls = False
        mock_response.content = "Task completed"
        # provider.chat must be an AsyncMock because it is awaited
        provider.chat = AsyncMock(return_value=mock_response)
        
        bus = MagicMock()
        # bus.publish_inbound is awaited too if used
        bus.publish_inbound = AsyncMock()
        
        manager = SubagentManager(provider, mock_workspace, bus)
        
        # Mock Post retrieval
        manager.company_loader = MagicMock()
        manager.company_loader.posts = {
            "Post_Test": Post(title="Test", description="D", context_prompt="C")
        }
        
        # Action: Spawn
        # We'll call _run_subagent directly since spawn just schedules it.
        # But spawn generates the ID.
        task_id = "test_task_id"
        
        # We need to mock the tools registry to avoid actual tool loading
        # Create a dedicated MagicMock for the registry instance (container is sync)
        mock_registry_instance = MagicMock()
        mock_registry_instance.execute = AsyncMock(return_value="Tool output")
        mock_registry_instance.get_definitions.return_value = [] # Synchronous method
        
        with patch("nanobot.agent.subagent.ToolRegistry", return_value=mock_registry_instance):
            await manager._run_subagent(
                task_id=task_id, 
                task="Do task", 
                label="Label", 
                origin={"channel": "test", "chat_id": "direct"}, 
                post_id="Post_Test"
            )
        
        # Verification:
        # Check if ContextBuilder was instantiated with agent_id=task_id
        MockContextBuilder.assert_called_with(
            manager.workspace,
            agent_id=task_id,
            company_name=None,
            company_path=None,
        )
        
        # Check if get_agent_identity was called on the ISOLATED builder instance
        # MockContextBuilder.return_value is the instance
        isolated_builder = MockContextBuilder.return_value
        isolated_builder.get_agent_identity.assert_called_with("Post_Test")
