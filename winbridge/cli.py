import typer

app = typer.Typer(name="pkg", help="Winbridge — cross-distro Linux package manager")

@app.command()
def hello() -> None:
    """Say hello."""
    typer.echo("Hello from Winbridge!")

if __name__ == "__main__":
    app()
