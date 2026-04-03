# winbridge

A cross-distro Linux package manager. One command to install from your native package manager or directly from GitHub releases — containerized and isolated.

```bash
pkg install nginx                        # uses apt / dnf / pacman / etc.
pkg install gh:helix-editor/helix        # downloads release, runs in a container
pkg install gh:zellij-org/zellij@0.40.1  # pin a specific version
pkg run helix myfile.txt                 # run the containerized app
```

## What it does

**Native wrapper** — translates `pkg install <name>` into the correct command for the running distro. Supports Debian/Ubuntu (apt), Fedora/RHEL (dnf), Arch (pacman), openSUSE (zypper), Alpine (apk), and Void (xbps).

**GitHub package manager** — installs binaries directly from GitHub releases. Each app runs in its own OCI container (podman or docker), isolated from the host system. A unified SQLite database tracks everything installed regardless of source.

## Requirements

- Python 3.11+
- [uv](https://docs.astral.sh/uv/)
- `podman` (recommended) or `docker` — required for `gh:` packages only

## Installation

```bash
git clone https://github.com/AI-Bobby-Newb/winbridge
cd winbridge
uv tool install .
```

This installs the `pkg` command into your PATH.

## Usage

### Install packages

```bash
# Native package manager
pkg install nginx
pkg install git

# From GitHub releases (containerized)
pkg install gh:helix-editor/helix
pkg install gh:zellij-org/zellij
pkg install gh:burntsushi/ripgrep@14.1.0   # pin a tag
```

### Manage packages

```bash
pkg list                  # all installed packages
pkg list --native         # only native packages
pkg list --gh             # only GitHub packages
pkg info helix            # details about an installed package
pkg update nginx          # update a single package
pkg upgrade               # upgrade all native packages
pkg remove helix          # uninstall
```

### Search and run

```bash
pkg search ripgrep        # search native package index
pkg run helix             # run a GitHub-installed containerized app
pkg run helix myfile.txt  # pass args to the app
```

## Aliases

Map short names to GitHub repos in `~/.config/winbridge/aliases.toml`:

```toml
[aliases]
helix   = "gh:helix-editor/helix"
zellij  = "gh:zellij-org/zellij"
rg      = "gh:burntsushi/ripgrep"
```

Then use `pkg install helix` instead of `pkg install gh:helix-editor/helix`.

## Package manifests

GitHub packages can ship a `winbridge.toml` in their release assets to control how the container is built and run:

```toml
[package]
name   = "helix"
binary = "hx"
version = "25.01"

[container]
ports   = []
mounts  = ["$HOME/.config/helix:/root/.config/helix"]
env     = []
network = false
```

If no `winbridge.toml` is found, winbridge auto-detects the binary from the release archive and uses safe defaults (no network, no extra mounts).

## GitHub API rate limits

Unauthenticated requests are limited to 60/hour. Set a token to raise it:

```bash
export WINBRIDGE_GITHUB_TOKEN=ghp_yourtoken
```

## File locations

| Path | Purpose |
|------|---------|
| `~/.local/share/winbridge/winbridge.db` | Package database |
| `~/.local/share/winbridge/packages/` | Downloaded binaries |
| `~/.config/winbridge/aliases.toml` | Package name aliases |

## Supported distros

| Family | Distros |
|--------|---------|
| debian | Ubuntu, Debian, Mint, Pop!_OS |
| rhel | Fedora, CentOS, RHEL, AlmaLinux, Rocky |
| arch | Arch, Manjaro, EndeavourOS |
| suse | openSUSE Tumbleweed, Leap |
| alpine | Alpine Linux |
| void | Void Linux |

## Development

```bash
git clone https://github.com/AI-Bobby-Newb/winbridge
cd winbridge
uv sync
uv run pytest -v
```

## License

MIT
