import pytest
from pathlib import Path
from unittest.mock import patch
from winbridge.resolver import resolve, ParsedPackage


def test_resolve_native():
    pkg = resolve("nginx")
    assert pkg == ParsedPackage(backend="native", name="nginx", repo=None, tag=None)


def test_resolve_github():
    pkg = resolve("gh:helix-editor/helix")
    assert pkg.backend == "github"
    assert pkg.name == "helix"
    assert pkg.repo == "helix-editor/helix"
    assert pkg.tag is None


def test_resolve_github_with_tag():
    pkg = resolve("gh:helix-editor/helix@25.01")
    assert pkg.repo == "helix-editor/helix"
    assert pkg.tag == "25.01"


def test_resolve_alias(tmp_path: Path):
    aliases_toml = tmp_path / "aliases.toml"
    aliases_toml.write_text('[aliases]\nhelix = "gh:helix-editor/helix"\n')
    with patch("winbridge.resolver.ALIASES_PATH", aliases_toml):
        pkg = resolve("helix")
        assert pkg.backend == "github"
        assert pkg.repo == "helix-editor/helix"
        assert pkg.tag is None


def test_resolve_alias_with_inline_tag(tmp_path: Path):
    aliases_toml = tmp_path / "aliases.toml"
    aliases_toml.write_text('[aliases]\nhelix = "gh:helix-editor/helix"\n')
    with patch("winbridge.resolver.ALIASES_PATH", aliases_toml):
        pkg = resolve("helix@25.01")
        assert pkg.tag == "25.01"


def test_resolve_no_alias_file():
    with patch("winbridge.resolver.ALIASES_PATH", Path("/nonexistent/aliases.toml")):
        pkg = resolve("nginx")
        assert pkg.backend == "native"
