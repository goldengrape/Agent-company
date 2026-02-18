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
    console.print(f"[green]✓[/green] Company '{name}' initialized at {companies_dir}")

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
