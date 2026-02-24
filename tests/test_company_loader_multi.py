
import pytest
from pathlib import Path
from nanobot.company.loader import CompanyConfigLoader

@pytest.fixture
def workspace(tmp_path):
    """Create a temporary workspace with company structures."""
    ws = tmp_path / "workspace_root"
    ws.mkdir()
    return ws

def test_load_explicit_company(workspace):
    """Test loading a specific company by name."""
    # Setup: Create companies/alpha/POSTS.md
    alpha_dir = workspace / "companies" / "alpha"
    alpha_dir.mkdir(parents=True)
    (alpha_dir / "POSTS.md").write_text("""
### 2.1 Alpha Agent (Post_Alpha)
- **Description**: Alpha agent.
    """)
    
    loader = CompanyConfigLoader(workspace, company_name="alpha")
    loader.load_all()
    
    assert loader.base_path == alpha_dir
    assert "Post_Alpha" in loader.posts

def test_load_default_company(workspace):
    """Test loading default company when no name provided."""
    # Setup: Create companies/default/POSTS.md
    default_dir = workspace / "companies" / "default"
    default_dir.mkdir(parents=True)
    (default_dir / "POSTS.md").write_text("""
### 2.1 Default Agent (Post_Default)
- **Description**: Default agent.
    """)
    
    loader = CompanyConfigLoader(workspace, company_name=None)
    loader.load_all()
    
    assert loader.base_path == default_dir
    assert "Post_Default" in loader.posts

def test_load_legacy_fallback(workspace):
    """Test fallback to legacy 'company/' directory if specific/default missing."""
    # Setup: Create company/POSTS.md (Legacy)
    legacy_dir = workspace / "company"
    legacy_dir.mkdir(parents=True)
    (legacy_dir / "POSTS.md").write_text("""
### 2.1 Legacy Agent (Post_Legacy)
- **Description**: Legacy agent.
    """)
    
    # Ensure no companies/default exists
    
    loader = CompanyConfigLoader(workspace, company_name=None)
    loader.load_all()
    
    assert loader.base_path == legacy_dir
    assert "Post_Legacy" in loader.posts

def test_load_non_existent_company(workspace):
    """Test loading a company that does not exist."""
    loader = CompanyConfigLoader(workspace, company_name="non_existent")
    loader.load_all()
    
    # Base path should still be set to the expected path
    expected_path = workspace / "companies" / "non_existent"
    assert loader.base_path == expected_path
    
    # But nothing loaded
    assert len(loader.posts) == 0
    assert len(loader.schemas) == 0

def test_skill_md_priority(workspace):
    """Test that SKILL.md paths take precedence if file exists."""
    # Setup: companies/beta/SKILL.md pointing to a custom file
    beta_dir = workspace / "companies" / "beta"
    beta_dir.mkdir(parents=True)
    
    (beta_dir / "SKILL.md").write_text("""---
components:
  posts: "./CUSTOM_POSTS.md"
---""")
    
    (beta_dir / "CUSTOM_POSTS.md").write_text("""
### 2.1 Custom Agent (Post_Custom)
- **Description**: Custom agent.
    """)
    
    # Create standard POSTS.md too, to ensure it's NOT loaded if SKILL.md guides elsewhere
    # Actually logic in loader.py: 
    # if _load_from_skill_def returns True, we don't call _load_posts() (which loads standard POSTS.md)
    # But _load_from_skill_def only loads what is in components.
    
    (beta_dir / "POSTS.md").write_text("""
### 2.1 Standard Agent (Post_Standard)
- **Description**: Standard agent.
    """)

    loader = CompanyConfigLoader(workspace, company_name="beta")
    loader.load_all()
    
    # Should contain Custom but NOT Standard (unless logic changed to merge, but currently it's one or other)
    assert "Post_Custom" in loader.posts
    assert "Post_Standard" not in loader.posts


def test_skill_md_loads_skills_dir_and_workflows(workspace):
    """Test SKILL.md-based skills_dir/workflows loading."""
    gamma_dir = workspace / "companies" / "gamma"
    gamma_dir.mkdir(parents=True)

    (gamma_dir / "SKILL.md").write_text(
        """---
components:
  posts: "./POSTS.md"
  workflows: "./WORKFLOWS.md"
  skills_dir: "./company_skills"
---""",
        encoding="utf-8",
    )
    (gamma_dir / "POSTS.md").write_text(
        """
### 2.1 Gamma Agent (Post_Gamma)
- **Description**: Gamma agent.
        """,
        encoding="utf-8",
    )
    (gamma_dir / "WORKFLOWS.md").write_text(
        "# Workflows\n\nPlan -> Do -> Check -> Act",
        encoding="utf-8",
    )
    (gamma_dir / "company_skills").mkdir(parents=True)

    loader = CompanyConfigLoader(workspace, company_name="gamma")
    loader.load_all()

    assert loader.skills_dir == (gamma_dir / "company_skills").resolve()
    assert loader.workflows_path == (gamma_dir / "WORKFLOWS.md").resolve()
    assert "Plan -> Do -> Check -> Act" in loader.workflows_content
