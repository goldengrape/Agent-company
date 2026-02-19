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


# ============================================================
# 新增：文件权限 (allowed_paths) 相关测试
# ============================================================

MOCK_POSTS_WITH_PATHS = """# 岗位描述文档 (人/岗位)

## 2. 岗位注册表 (Posts Registry)

### 2.0 天气分析师 (Post_Weather_Analyst)
- **Description**: 负责查询天气并生成报告。
- **Skills**:
  - `web-search`: 搜索天气数据。
- **Tools**: `web_search`, `write_file`.
- **Allowed Paths**:
  - `workspace/reports/weather/` (读写)
  - `workspace/tasks/` (只读)
- **Context**:
  > 你是一名天气分析师。

### 2.1 审计员 (Post_Auditor)
- **Description**: 负责检查工作质量。
- **Skills**:
  - `code-review`: 代码质量分析。
- **Tools**: `read_file`.
- **Allowed Paths**:
  - `workspace/reports/` (只读)
  - `workspace/audits/` (rw)
- **Context**:
  > 你是一名审计员。
"""


@pytest.fixture
def mock_workspace_with_paths(tmp_path):
    company_dir = tmp_path / "company"
    company_dir.mkdir()
    (company_dir / "POSTS.md").write_text(MOCK_POSTS_WITH_PATHS, encoding="utf-8")
    (company_dir / "WORKFLOWS.md").write_text(MOCK_WORKFLOWS_MD, encoding="utf-8")
    (company_dir / "DOCS_SCHEMA.md").write_text(MOCK_DOCS_SCHEMA, encoding="utf-8")
    return tmp_path


def test_load_posts_with_allowed_paths(mock_workspace_with_paths):
    """验证 allowed_paths 从 POSTS.md 正确解析，支持中文和英文模式标记。"""
    loader = CompanyConfigLoader(mock_workspace_with_paths)
    loader.load_all()
    
    # 天气分析师
    weather = loader.posts["Post_Weather_Analyst"]
    assert len(weather.allowed_paths) == 2
    assert weather.allowed_paths[0] == {"path": "workspace/reports/weather/", "mode": "rw"}
    assert weather.allowed_paths[1] == {"path": "workspace/tasks/", "mode": "r"}
    
    # 审计员 - 混合中英文标记
    auditor = loader.posts["Post_Auditor"]
    assert len(auditor.allowed_paths) == 2
    assert auditor.allowed_paths[0] == {"path": "workspace/reports/", "mode": "r"}
    assert auditor.allowed_paths[1] == {"path": "workspace/audits/", "mode": "rw"}


def test_context_builder_includes_permissions(mock_workspace_with_paths):
    """验证 system prompt 中包含文件权限说明。"""
    from unittest.mock import MagicMock
    
    builder = ContextBuilder(mock_workspace_with_paths)
    # 手动加载 posts (因为 get_agent_identity 内部会调用 load_all)
    identity = builder.get_agent_identity("Post_Weather_Analyst")
    
    # 应包含权限段落
    assert "文件访问权限" in identity
    assert "workspace/reports/weather/" in identity
    assert "读写" in identity
    assert "workspace/tasks/" in identity
    assert "只读" in identity
    # 应包含警告
    assert "违反文件访问权限" in identity


def test_post_without_allowed_paths_backward_compatible(mock_workspace_root):
    """验证无 allowed_paths 的旧格式 POSTS.md 仍可正常工作。"""
    loader = CompanyConfigLoader(mock_workspace_root)
    loader.load_all()
    
    # 旧格式 Post 应有空的 allowed_paths
    dev_post = loader.posts["Post_Dev_Junior"]
    assert dev_post.allowed_paths == []
    
    # System prompt 不应包含权限段落
    builder = ContextBuilder(mock_workspace_root)
    identity = builder.get_agent_identity("Post_Dev_Junior")
    assert "文件访问权限" not in identity


def test_post_dataclass_with_allowed_paths():
    """验证 Post dataclass 正确接受 allowed_paths 参数。"""
    post = Post(
        title="Test_Post",
        description="A test post",
        skills=["skill1"],
        tools=["tool1"],
        context_prompt="Be a tester",
        allowed_paths=[
            {"path": "workspace/data/", "mode": "rw"},
            {"path": "workspace/config/", "mode": "r"},
        ]
    )
    assert len(post.allowed_paths) == 2
    assert post.allowed_paths[0]["mode"] == "rw"
    assert post.allowed_paths[1]["path"] == "workspace/config/"

