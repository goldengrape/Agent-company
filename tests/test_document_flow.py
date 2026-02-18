import pytest
from pathlib import Path
from nanobot.agent.tools.document_flow import DocumentFlowTool
from nanobot.company.loader import CompanyConfigLoader

MOCK_SCHEMA = """# Doc Schema
## 1. Task Order (Doc_Task_Order)
**文件命名**: `TASK_{ID}_{Title}.md`
**位置**: `workspace/tasks/`

```markdown
# TASK ORDER: {Title}
**ID**: {ID}
## Objective
{Objective}
```
"""

@pytest.fixture
def workspace_with_schema(tmp_path):
    company_dir = tmp_path / "company"
    company_dir.mkdir()
    (company_dir / "DOCS_SCHEMA.md").write_text(MOCK_SCHEMA, encoding="utf-8")
    return tmp_path

@pytest.mark.asyncio
async def test_create_document(workspace_with_schema):
    tool = DocumentFlowTool(workspace_with_schema)
    
    result = await tool.execute(
        "create",
        doc_type="Doc_Task_Order",
        title="Fix_Bug",
        metadata={"Objective": "Fix the crash"}
    )
    
    assert "Document created successfully" in result
    
    # Verify file exists
    tasks_dir = workspace_with_schema / "workspace" / "tasks"
    files = list(tasks_dir.glob("TASK_*_Fix_Bug.md"))
    assert len(files) == 1
    
    content = files[0].read_text(encoding="utf-8")
    assert "# TASK ORDER: Fix_Bug" in content
    assert "## Objective" in content
    assert "Fix the crash" in content

@pytest.mark.asyncio
async def test_validate_document(workspace_with_schema):
    tool = DocumentFlowTool(workspace_with_schema)
    # Create valid doc first
    await tool.execute("create", doc_type="Doc_Task_Order", title="Valid_Doc")
    tasks_dir = workspace_with_schema / "workspace" / "tasks"
    doc_path = list(tasks_dir.glob("TASK_*_Valid_Doc.md"))[0]
    
    result = await tool.execute("validate", file_path=str(doc_path), doc_type="Doc_Task_Order")
    assert "Validation Passed" in result

@pytest.mark.asyncio
async def test_list_schemas(workspace_with_schema):
    tool = DocumentFlowTool(workspace_with_schema)
    result = await tool.execute("list_schemas")
    assert "Doc_Task_Order" in result
