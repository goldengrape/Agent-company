import pytest
import json
import time
from pathlib import Path
from unittest.mock import MagicMock

from nanobot.agent.tools.document_flow import DocumentFlowTool
from nanobot.agent.memory import MemoryStore

@pytest.fixture
def workspace(tmp_path):
    (tmp_path / "workspace" / "tasks").mkdir(parents=True)
    (tmp_path / "company").mkdir()
    # Create a dummy schema for testing
    (tmp_path / "company" / "DOCS_SCHEMA.md").write_text("""
## 1. Test Doc (`Doc_Test`)
**文件命名**: `TEST_{ID}.md`
**位置**: `workspace/tasks/`
    """, encoding="utf-8")
    
    # Create POSTS.md to avoid loader error if it reads it
    (tmp_path / "company" / "POSTS.md").write_text("# Posts", encoding="utf-8")
    (tmp_path / "company" / "WORKFLOWS.md").write_text("# Workflows", encoding="utf-8")
    
    return tmp_path

def test_memory_log_event(workspace):
    memory = MemoryStore(workspace)
    memory.log_event("test_event", {"foo": "bar"})
    
    events_file = workspace / "memory" / "EVENTS.jsonl"
    assert events_file.exists()
    
    lines = events_file.read_text(encoding="utf-8").strip().split("\n")
    assert len(lines) == 1
    
    event = json.loads(lines[0])
    assert event["type"] == "test_event"
    assert event["details"]["foo"] == "bar"
    assert "timestamp" in event

@pytest.mark.asyncio
async def test_document_flow_logs_creation(workspace):
    tool = DocumentFlowTool(workspace)
    
    # Create a document
    result = await tool.execute(
        action="create",
        doc_type="Doc_Test",
        title="My Test Doc",
        content="Some content"
    )
    
    assert "Document created successfully" in result
    
    # Check log
    events_file = workspace / "memory" / "EVENTS.jsonl"
    assert events_file.exists()
    
    lines = events_file.read_text(encoding="utf-8").strip().split("\n")
    # Depending on implementation, might be multiple logs if tested in sequence, but here new workspace
    assert len(lines) >= 1
    last_event = json.loads(lines[-1])
    
    assert last_event["type"] == "task_created"
    assert last_event["details"]["title"] == "My Test Doc"
    assert "TEST_" in last_event["details"]["file_path"]

@pytest.mark.asyncio
async def test_document_flow_logs_submission(workspace):
    tool = DocumentFlowTool(workspace)
    
    # Create a dummy file to submit
    doc_path = workspace / "workspace" / "tasks" / "TEST_123.md"
    doc_path.write_text("content")
    
    await tool.execute(action="submit", file_path=str(doc_path))
    
    events_file = workspace / "memory" / "EVENTS.jsonl"
    assert events_file.exists()
    
    lines = events_file.read_text(encoding="utf-8").strip().split("\n")
    last_event = json.loads(lines[-1])
    
    assert last_event["type"] == "task_submitted"
    assert str(doc_path) in last_event["details"]["file_path"]
