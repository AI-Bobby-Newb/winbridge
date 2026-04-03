# Winbridge

Cross-distro Linux package manager (Python). Wraps native package managers and installs containerized apps from GitHub releases.

## How to run

```bash
uv run pkg --help
uv run pkg install nginx
uv run pkg install gh:helix-editor/helix
uv run pkg run helix myfile.txt
```

## How to test

```bash
uv run pytest -v
```

## Key files

- `winbridge/cli.py` — Typer CLI entrypoint
- `winbridge/app.py` — Orchestration (install/remove/run/list/info)
- `winbridge/_factory.py` — Wires real dependencies at startup
- `winbridge/resolver.py` — Routes `gh:user/repo` vs native package names
- `winbridge/github.py` — GitHub API, asset selection, manifest parsing
- `winbridge/container.py` — Podman/Docker wrapper
- `winbridge/db.py` — SQLite package database
- `winbridge/distro.py` — Detects distro family from `/etc/os-release`
- `winbridge/adapters/` — One adapter per distro family (apt/dnf/pacman/zypper/apk/xbps)

## Gotchas

- Requires `podman` or `docker` at runtime for GitHub-sourced packages
- `WINBRIDGE_GITHUB_TOKEN` env var raises GitHub API rate limits
- Package aliases live in `~/.config/winbridge/aliases.toml`
- DB lives at `~/.local/share/winbridge/winbridge.db`
- Tests run on macOS fine (all subprocess/network calls are mocked)
