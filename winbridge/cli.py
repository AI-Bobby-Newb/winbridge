from __future__ import annotations

from typing import Optional

import typer
from rich.console import Console
from rich.table import Table

app = typer.Typer(name="pkg", help="Winbridge — cross-distro Linux package manager")
console = Console()


def _app():
    from winbridge._factory import build_app
    return build_app()


@app.command()
def install(package: str = typer.Argument(..., help="Package name or gh:user/repo[@tag]")):
    """Install a package."""
    _app().install(package)


@app.command()
def remove(package: str = typer.Argument(..., help="Package name to remove")):
    """Remove an installed package."""
    _app().remove(package)


@app.command()
def update(package: str = typer.Argument(..., help="Package to update")):
    """Update a single package to its latest version."""
    wa = _app()
    record = wa._db.get(package)
    if record and record["source"] == "native":
        wa._adapter.update(package)
        console.print(f"[green]✓[/green] {package} updated.")
    else:
        wa.install(package)  # Re-install to latest for GitHub packages


@app.command()
def upgrade():
    """Upgrade all native packages."""
    _app()._adapter.upgrade()
    console.print("[green]✓[/green] System packages upgraded.")


@app.command("list")
def list_packages(
    native: bool = typer.Option(False, "--native", help="Show only native packages"),
    gh: bool = typer.Option(False, "--gh", help="Show only GitHub packages"),
):
    """List installed packages."""
    source = "native" if native else ("github" if gh else None)
    packages = _app().list_packages(source=source)

    if not packages:
        console.print("No packages installed.")
        return

    table = Table(title="Installed Packages")
    table.add_column("Name", style="bold")
    table.add_column("Version")
    table.add_column("Source")
    table.add_column("Repo / Notes")

    for pkg in packages:
        table.add_row(
            pkg["name"],
            pkg["version"] or "—",
            pkg["source"],
            pkg.get("repo") or "—",
        )
    console.print(table)


@app.command()
def search(query: str = typer.Argument(..., help="Search query")):
    """Search for native packages."""
    results = _app()._adapter.search(query)
    if not results:
        console.print("No results found.")
        return
    for name in results:
        console.print(name)


@app.command()
def info(package: str = typer.Argument(..., help="Package name")):
    """Show details about an installed package."""
    record = _app().info(package)
    if record is None:
        console.print(f"[red]{package} is not installed.[/red]")
        raise typer.Exit(1)
    for key, value in record.items():
        console.print(f"[bold]{key}:[/bold] {value or '—'}")


@app.command("run")
def run_package(
    package: str = typer.Argument(..., help="Package name"),
    args: Optional[list[str]] = typer.Argument(None, help="Arguments to pass to the app"),
):
    """Run a GitHub-installed containerized package."""
    _app().run(package, args or [])


if __name__ == "__main__":
    app()
