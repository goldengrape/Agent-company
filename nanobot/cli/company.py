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
def company_init():
    """Initialize company structure."""
    workspace = get_workspace_path()
    # verify company dir exists, if not create it (this is partly handled by onboard, but let's be safe)
    company_dir = workspace / "company"
    company_dir.mkdir(parents=True, exist_ok=True)
    console.print(f"[green]✓[/green] Company initialized at {company_dir}")

@company_app.command("run")
def company_run():
    """Run the company manager to process tasks."""
    console.print(f"{__logo__} Starting Nanobot Company Manager...")
    
    config = load_config()
    workspace = config.workspace_path
    manager = CompanyManager(workspace)
    
    try:
        asyncio.run(manager.run())
    except KeyboardInterrupt:
        console.print("\n[yellow]Company Manager stopped.[/yellow]")
    except Exception as e:
        console.print(f"[red]Error running company manager: {e}[/red]")
