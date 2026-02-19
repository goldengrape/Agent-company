import asyncio
import typer
from rich.console import Console

from nanobot import __logo__
from nanobot.config.loader import load_config
from nanobot.utils.helpers import get_workspace_path
from nanobot.company.manager import CompanyManager

company_app = typer.Typer(help="Manage the AI Company")
console = Console()

@company_app.command("init")
def company_init(
    name: str = typer.Option("default", "--name", "-n", help="Name of the company to initialize"),
):
    """Initialize company structure."""
    workspace = get_workspace_path()
    # Create companies directory
    companies_dir = workspace / "companies" / name
    companies_dir.mkdir(parents=True, exist_ok=True)
    
    # 1. Create SKILL.md
    skill_content = f"""---
name: {name}
# default_post: Post_Analyst  # Uncomment to enable auto-routing
# default_task_template: |
#   Process this task:
#   File: {{filename}}
#   {{content}}

components:
  posts: "./POSTS.md"
  workflows: "./WORKFLOWS.md"
  docs_schema: "./DOCS_SCHEMA.md"
---
"""
    (companies_dir / "SKILL.md").write_text(skill_content, encoding="utf-8")

    # 2. Create POSTS.md
    posts_content = """# Company Posts

### 2.1 Analyst (Post_Analyst)
- **Description**: A generic analyst role.
- **Skills**:
  - `web_search`
- **Tools**: `read_file`, `write_file`
- **Context**:
  > You are an analyst. Your job is to process tasks.
"""
    (companies_dir / "POSTS.md").write_text(posts_content, encoding="utf-8")

    # 3. Create WORKFLOWS.md
    workflows_content = """# Company Workflows
"""
    (companies_dir / "WORKFLOWS.md").write_text(workflows_content, encoding="utf-8")

    # 4. Create DOCS_SCHEMA.md
    schema_content = """# Document Schemas
"""
    (companies_dir / "DOCS_SCHEMA.md").write_text(schema_content, encoding="utf-8")

    console.print(f"[green]✓[/green] Company '{name}' initialized at {companies_dir}")
    console.print(f"  - Created SKILL.md")
    console.print(f"  - Created POSTS.md")
    console.print(f"  - Created WORKFLOWS.md")
    console.print(f"  - Created DOCS_SCHEMA.md")

@company_app.command("run")
def company_run(
    name: str = typer.Option(None, "--name", "-n", help="Name of the company to run"),
):
    """Run the company manager to process tasks."""
    console.print(f"{__logo__} Starting Nanobot Company Manager ({name or 'default'})...")
    
    config = load_config()
    workspace = config.workspace_path
    manager = CompanyManager(workspace, company_name=name)
    
    try:
        asyncio.run(manager.run())
    except KeyboardInterrupt:
        console.print("\n[yellow]Company Manager stopped.[/yellow]")
    except Exception as e:
        console.print(f"[red]Error running company manager: {e}[/red]")
