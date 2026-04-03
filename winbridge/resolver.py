from __future__ import annotations

import tomllib
from dataclasses import dataclass
from pathlib import Path

ALIASES_PATH = Path.home() / ".config" / "winbridge" / "aliases.toml"


@dataclass
class ParsedPackage:
    backend: str       # "native" or "github"
    name: str          # friendly name, e.g. "helix"
    repo: str | None   # "helix-editor/helix" (github only)
    tag: str | None    # "25.01" or None for latest


def _load_aliases() -> dict[str, str]:
    if not ALIASES_PATH.exists():
        return {}
    with open(ALIASES_PATH, "rb") as f:
        return tomllib.load(f).get("aliases", {})


def _parse_gh(spec: str) -> tuple[str, str | None]:
    """'user/repo' or 'user/repo@tag' → (repo, tag | None)"""
    if "@" in spec:
        repo, tag = spec.rsplit("@", 1)
        return repo, tag
    return spec, None


def resolve(spec: str) -> ParsedPackage:
    if spec.startswith("gh:"):
        repo, tag = _parse_gh(spec[3:])
        return ParsedPackage(backend="github", name=repo.split("/")[-1], repo=repo, tag=tag)

    # Check for inline @tag before alias lookup
    inline_tag: str | None = None
    lookup = spec
    if "@" in spec:
        lookup, inline_tag = spec.rsplit("@", 1)

    aliases = _load_aliases()
    if lookup in aliases:
        repo, alias_tag = _parse_gh(aliases[lookup][3:])  # strip "gh:"
        return ParsedPackage(
            backend="github",
            name=repo.split("/")[-1],
            repo=repo,
            tag=inline_tag or alias_tag,
        )

    return ParsedPackage(backend="native", name=spec, repo=None, tag=None)
