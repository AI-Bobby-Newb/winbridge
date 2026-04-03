import pytest
from pathlib import Path
from unittest.mock import MagicMock, patch
from winbridge.github import GitHubBackend, AssetNotFoundError, RateLimitError

FAKE_ASSETS = [
    {"name": "helix-25.01-x86_64-linux.tar.xz", "browser_download_url": "https://x.com/helix.tar.xz"},
    {"name": "helix-25.01-aarch64-linux.tar.xz", "browser_download_url": "https://x.com/helix-arm.tar.xz"},
    {"name": "helix-25.01-x86_64-windows.zip",   "browser_download_url": "https://x.com/helix-win.zip"},
    {"name": "helix-25.01-x86_64-linux.tar.xz.sha256", "browser_download_url": "https://x.com/sha"},
]

FAKE_RELEASE = {"tag_name": "25.01", "assets": FAKE_ASSETS}


@pytest.fixture
def backend(tmp_path: Path):
    return GitHubBackend(packages_dir=tmp_path)


def test_select_asset_x86_64(backend):
    asset = backend.select_asset(FAKE_ASSETS, arch="x86_64")
    assert "x86_64" in asset["name"]
    assert "linux" in asset["name"]
    assert "windows" not in asset["name"]
    assert not asset["name"].endswith(".sha256")


def test_select_asset_aarch64(backend):
    asset = backend.select_asset(FAKE_ASSETS, arch="aarch64")
    assert "aarch64" in asset["name"]
    assert "linux" in asset["name"]


def test_select_asset_not_found(backend):
    with pytest.raises(AssetNotFoundError):
        backend.select_asset(FAKE_ASSETS, arch="riscv64")


def test_fetch_release_latest(backend):
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = FAKE_RELEASE
    with patch("httpx.get", return_value=mock_resp):
        release = backend.fetch_release("helix-editor/helix", tag=None)
    assert release["tag_name"] == "25.01"


def test_fetch_release_pinned_tag(backend):
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = FAKE_RELEASE
    with patch("httpx.get", return_value=mock_resp) as mock_get:
        backend.fetch_release("helix-editor/helix", tag="25.01")
    assert "25.01" in mock_get.call_args.args[0]
    assert "latest" not in mock_get.call_args.args[0]


def test_fetch_release_rate_limit(backend):
    mock_resp = MagicMock()
    mock_resp.status_code = 403
    mock_resp.headers = {"X-RateLimit-Remaining": "0"}
    with patch("httpx.get", return_value=mock_resp):
        with pytest.raises(RateLimitError):
            backend.fetch_release("helix-editor/helix", tag=None)


def test_parse_manifest(backend, tmp_path: Path):
    (tmp_path / "winbridge.toml").write_bytes(
        b'[package]\nname="helix"\nbinary="hx"\nversion="25.01"\n'
        b'[container]\nports=[]\nmounts=[]\nenv=[]\nnetwork=false\n'
    )
    manifest = backend.parse_manifest(tmp_path / "winbridge.toml")
    assert manifest["package"]["binary"] == "hx"
    assert manifest["container"]["network"] is False


def test_parse_manifest_missing_returns_defaults(backend, tmp_path: Path):
    manifest = backend.parse_manifest(tmp_path / "nonexistent.toml")
    assert manifest["package"]["binary"] is None
    assert manifest["container"]["mounts"] == []
