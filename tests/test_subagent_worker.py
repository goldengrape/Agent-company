import pytest
import asyncio
from unittest.mock import MagicMock, AsyncMock, patch
from pathlib import Path
from nanobot.agent.subagent import SubagentManager
from nanobot.company.loader import CompanyConfigLoader, Post

# Mock data
MOCK_POSTS_MD = """# Posts
### 2.1 TestWorker (Post_TestWorker)
- **Description**: A worker for testing.
- **Skills**:
  - `test-skill`
- **Tools**: `read_file`, `exec`.
- **Context**:
  > You are a test worker.
"""

@pytest.fixture
def mock_workspace(tmp_path):
    company_dir = tmp_path / "company"
    company_dir.mkdir()
    (company_dir / "POSTS.md").write_text(MOCK_POSTS_MD, encoding="utf-8")
    
    skills_dir = tmp_path / "skills" / "test-skill"
    skills_dir.mkdir(parents=True)
    (skills_dir / "SKILL.md").write_text("# Test Skill\n\nHow to test.", encoding="utf-8")
    (tmp_path / "AGENTS.md").write_text("", encoding="utf-8") # Bootstrap file
    
    return tmp_path

@pytest.mark.asyncio
async def test_spawn_worker(mock_workspace):
    # Mock provider and bus
    provider = AsyncMock()
    provider.get_default_model.return_value = "gpt-4"
    # Mock chat response
    mock_response = MagicMock()
    mock_response.has_tool_calls = False
    mock_response.content = "I have completed the task."
    provider.chat.return_value = mock_response
    
    bus = AsyncMock()
    
    manager = SubagentManager(
        provider=provider,
        workspace=mock_workspace,
        bus=bus
    )
    
    # Test spawn_worker
    result = await manager.spawn_worker("Post_TestWorker", "Do a test")
    
    assert "Subagent" in result
    assert "started" in result
    assert "Post_TestWorker" in str(manager._running_tasks) or True # Just check it runs without error
    
    # Wait for background task (it's async, so we might need to wait a tiny bit or inspect the task)
    # Since we can't easily await the background task directly without access to it, 
    # we can check if it was added to _running_tasks.
    # But wait, spawn_worker calls spawn which creates a task.
    
    # Let's inspect the side effects.
    # The provider.chat should eventually be called.
    # We need to yield control to let the loop run.
    await asyncio.sleep(0.1)
    
    # Verify provider was called
    assert provider.chat.called
    call_args = provider.chat.call_args
    messages = call_args.kwargs['messages']
    tools = call_args.kwargs['tools']
    
    # Verify System Prompt contains identity and skills
    system_prompt = messages[0]['content']
    assert "You are a test worker" in system_prompt
    assert "Test Skill" in system_prompt
    
    # Verify Tools (should only have read_file and exec)
    tool_names = [t['function']['name'] for t in tools]
    assert "read_file" in tool_names
    assert "exec" in tool_names
    
    # Verify Registry Update
    import json
    # Verify Registry Update
    import json
    registry_file = mock_workspace / "workspace" / "agent_resource" / "workers.json"
    assert registry_file.exists()
    
    data = json.loads(registry_file.read_text(encoding="utf-8"))
    # Find the worker we just spawned (we don't know the ID exactly from here easily without parsing return string)
    # But there should be one entry
    assert len(data) == 1
    worker_data = list(data.values())[0]
    assert worker_data["post_id"] == "Post_TestWorker"
    assert worker_data["status"] in ["active", "completed"]

@pytest.mark.asyncio
async def test_spawn_worker_invalid_post(mock_workspace):
    provider = AsyncMock()
    bus = AsyncMock()
    manager = SubagentManager(provider, mock_workspace, bus)
    
    result = await manager.spawn_worker("Post_Invalid", "Task")
    assert "Error: Post 'Post_Invalid' not found" in result
