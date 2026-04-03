import typer

app = typer.Typer(name="pkg", help="Winbridge — cross-distro Linux package manager")

@app.callback(invoke_without_command=True)
def main() -> None:
    """Winbridge — cross-distro Linux package manager"""
    pass

if __name__ == "__main__":
    app()
