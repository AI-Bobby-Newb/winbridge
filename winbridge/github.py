from __future__ import annotations

import os
import platform
import tomllib
from pathlib import Path

import httpx

GITHUB_API = "https://api.github.com"

_ARCH_ALIASES: dict[str, list[str]] = {
    "x86_64":  ["x86_64", "amd64"],
    "aarch64": ["aarch64", "arm64"],
    "armv7l":  ["armv7", "arm"],
}


class AssetNotFoundError(Exception):
    pass


class RateLimitError(Exception):
    pass


class GitHubBackend:
    def __init__(self, packages_dir: Path | None = None) -> None:
        self._packages_dir = packages_dir or (
            Path.home() / ".local" / "share" / "winbridge" / "packages"
        )

    def fetch_release(self, repo: str, tag: str | None) -> dict:
        url = (
            f"{GITHUB_API}/repos/{repo}/releases/tags/{tag}"
            if tag
            else f"{GITHUB_API}/repos/{repo}/releases/latest"
        )
        headers = {"Accept": "application/vnd.github+json"}
        token = os.environ.get("WINBRIDGE_GITHUB_TOKEN")
        if token:
            headers["Authorization"] = f"Bearer {token}"

        response = httpx.get(url, headers=headers)
        if response.status_code in (403, 429):
            raise RateLimitError(
                "GitHub API rate limit reached. "
                "Set WINBRIDGE_GITHUB_TOKEN to increase limits."
            )
        response.raise_for_status()
        return response.json()

    def select_asset(self, assets: list[dict], arch: str | None = None) -> dict:
        if arch is None:
            arch = platform.machine()
        aliases = _ARCH_ALIASES.get(arch, [arch])

        candidates = [
            a for a in assets
            if "linux" in a["name"].lower()
            and not a["name"].endswith(".sha256")
            and not a["name"].endswith(".sig")
            and not a["name"].endswith(".asc")
        ]

        for alias in aliases:
            for asset in candidates:
                if alias.lower() in asset["name"].lower():
                    return asset

        available = [a["name"] for a in assets]
        raise AssetNotFoundError(
            f"No asset found for arch={arch!r}. Available assets: {available}"
        )

    def parse_manifest(self, path: Path) -> dict:
        if not path.exists():
            return {
                "package": {"name": None, "binary": None, "version": None},
                "container": {"ports": [], "mounts": [], "env": [], "network": False},
            }
        with open(path, "rb") as f:
            return tomllib.load(f)
