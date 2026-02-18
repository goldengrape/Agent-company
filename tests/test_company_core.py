import pytest
from pathlib import Path
from dataclasses import asdict
from nanobot.company.loader import CompanyConfigLoader, Post
from nanobot.agent.context import ContextBuilder

# Mock data based on real POSTS.md structure
MOCK_POSTS_MD = """# 岗位描述文档 (人/岗位)

## 1. 结构
...

## 2. 岗位注册表 (Posts Registry)

### 2.1 初级开发工程师 (Post_Dev_Junior)
- **Description**: 负责根据明确的规范编写代码。
- **Skills**:
  - `code-modification`: 安全编辑文件的能力。
  - `git-operations`: 提交和推送代码更改的能力。
- **Tools**: `read_file`, `write_file`, `edit_file`.
- **Context**:
  > 你是一名初级开发工程师。
  > 必须严格遵守指令。

### 2.2 审计员 (Post_Auditor)
- **Description**: 负责检查工作质量。
- **Skills**:
  - `code-review`: 代码质量分析。
- **Tools**: `read_file`.
- **Context**:
  > 你是一名审计员。
  > 检查合规性。
"""

MOCK_WORKFLOWS_MD = "# 流程管理文档\n\n## 1. 核心 PDCA 循环\n..."
MOCK_DOCS_SCHEMA = "# 公文规范文档\n\n## 1. 任务单\n..."


@pytest.fixture
def mock_workspace_root(tmp_path):
    company_dir = tmp_path / "company"
    company_dir.mkdir()
    (company_dir / "POSTS.md").write_text(MOCK_POSTS_MD, encoding="utf-8")
    (company_dir / "WORKFLOWS.md").write_text(MOCK_WORKFLOWS_MD, encoding="utf-8")
    (company_dir / "DOCS_SCHEMA.md").write_text(MOCK_DOCS_SCHEMA, encoding="utf-8")
    return tmp_path


def test_company_loader_initialization(mock_workspace_root):
    loader = CompanyConfigLoader(mock_workspace_root)
    assert loader.workspace == mock_workspace_root


def test_load_posts(mock_workspace_root):
    loader = CompanyConfigLoader(mock_workspace_root)
    loader.load_all()
    
    assert "Post_Dev_Junior" in loader.posts
    assert "Post_Auditor" in loader.posts
    
    dev_post = loader.posts["Post_Dev_Junior"]
    assert dev_post.title == "Post_Dev_Junior"
    assert "负责根据明确的规范编写代码" in dev_post.description
    assert dev_post.skills == ["code-modification", "git-operations"]
    assert dev_post.tools == ["read_file", "write_file", "edit_file"]
    assert "你是一名初级开发工程师" in dev_post.context_prompt


def test_context_builder_company_identity(mock_workspace_root):
    builder = ContextBuilder(mock_workspace_root)
    # This method is not yet implemented, creating a failure for TDD
    identity = builder.get_agent_identity("Post_Dev_Junior")
    
    assert "Post_Dev_Junior" in identity
    assert "你是一名初级开发工程师" in identity
    assert "必须严格遵守指令" in identity


def test_post_dataclass_structure():
    post = Post(
        title="Test_Post",
        description="A test post",
        skills=["skill1"],
        tools=["tool1"],
        context_prompt="Be a tester"
    )
    assert post.title == "Test_Post"
    assert post.skills[0] == "skill1"


def test_load_schemas(mock_workspace_root):
    # Determine where the doc schema mock content is and ensure it has what we need for testing
    schema_content = """# 公文规范文档 (物/文档)

## 1. 任务单 (`Doc_Task_Order`)
**文件命名**: `TASK_{ID}_{Title}.md`
**位置**: `workspace/tasks/`

```markdown
# TASK ORDER: {标题}
**ID**: {UUID}
```

## 2. 工作报告 (`Doc_Work_Report`)
**文件命名**: `REPORT_{TaskID}.md`
**位置**: `workspace/reports/`

```markdown
# REPORT:
```
"""
    (mock_workspace_root / "company" / "DOCS_SCHEMA.md").write_text(schema_content, encoding="utf-8")

    loader = CompanyConfigLoader(mock_workspace_root)
    loader.load_all()
    
    assert "Doc_Task_Order" in loader.schemas
    assert "Doc_Work_Report" in loader.schemas
    
    task_schema = loader.schemas["Doc_Task_Order"]
    assert task_schema.doc_type_id == "Doc_Task_Order"
    assert task_schema.filename_pattern == "TASK_{ID}_{Title}.md"
    assert task_schema.target_dir == "workspace/tasks/"
    assert "# TASK ORDER: {标题}" in task_schema.template

