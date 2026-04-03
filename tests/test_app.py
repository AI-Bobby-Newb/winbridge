import pytest
from pathlib import Path
from unittest.mock import MagicMock, patch
from winbridge.app import WinbridgeApp
from winbridge.resolver import ParsedPackage


@pytest.fixture
def app():
    return WinbridgeApp(
        db=MagicMock(),
        adapter=MagicMock(),
        github=MagicMock(),
        runtime=MagicMock(),
    )


def test_install_native(app):
    with patch("winbridge.app.resolve", return_value=ParsedPackage("native", "nginx", None, None)):
        app.install("nginx")
    app._adapter.install.assert_called_once_with("nginx")
    app._db.record_install.assert_called_once()
    assert app._db.record_install.call_args.kwargs["source"] == "native"


def test_install_github(app):
    pkg = ParsedPackage("github", "helix", "helix-editor/helix", None)
    app._github.fetch_release.return_value = {"tag_name": "25.01", "assets": []}
    app._github.select_asset.return_value = {
        "name": "helix.tar.xz", "browser_download_url": "https://x.com/helix.tar.xz"
    }
    app._github.parse_manifest.return_value = {
        "package": {"name": "helix", "binary": "hx", "version": "25.01"},
        "container": {"ports": [], "mounts": [], "env": [], "network": False},
    }
    app._runtime.build_image.return_value = "winbridge-helix:latest"

    with patch("winbridge.app.resolve", return_value=pkg), \
         patch.object(app, "_download_and_extract", return_value=Path("/tmp/hx")), \
         patch.object(app, "_hash_manifest", return_value="abc123"):
        app.install("gh:helix-editor/helix")

    app._runtime.build_image.assert_called_once()
    assert app._db.record_install.call_args.kwargs["source"] == "github"
    assert app._db.record_install.call_args.kwargs["container_id"] == "winbridge-helix:latest"


def test_remove_native(app):
    app._db.get.return_value = {"name": "nginx", "source": "native", "container_id": None}
    with patch("winbridge.app.resolve", return_value=ParsedPackage("native", "nginx", None, None)):
        app.remove("nginx")
    app._adapter.remove.assert_called_once_with("nginx")
    app._db.record_remove.assert_called_once_with("nginx")


def test_remove_github(app):
    app._db.get.return_value = {
        "name": "helix", "source": "github", "container_id": "winbridge-helix:latest"
    }
    with patch("winbridge.app.resolve", return_value=ParsedPackage("github", "helix", None, None)):
        app.remove("helix")
    app._runtime.remove_image.assert_called_once_with("winbridge-helix:latest")
    app._db.record_remove.assert_called_once_with("helix")


def test_remove_not_installed_exits(app):
    app._db.get.return_value = None
    with patch("winbridge.app.resolve", return_value=ParsedPackage("native", "nginx", None, None)):
        with pytest.raises(SystemExit):
            app.remove("nginx")


def test_list_packages(app):
    app._db.list_all.return_value = [
        {"name": "nginx", "version": "1.24", "source": "native", "repo": None},
        {"name": "helix", "version": "25.01", "source": "github", "repo": "helix-editor/helix"},
    ]
    result = app.list_packages()
    assert len(result) == 2


def test_info_installed(app):
    app._db.get.return_value = {"name": "nginx", "version": "1.24", "source": "native"}
    result = app.info("nginx")
    assert result["name"] == "nginx"


def test_info_not_installed(app):
    app._db.get.return_value = None
    assert app.info("nginx") is None


def test_run_github_package(app):
    app._db.get.return_value = {
        "name": "helix", "source": "github",
        "container_id": "winbridge-helix:latest", "version": "25.01",
    }
    fake_manifest = {
        "package": {"name": "helix", "binary": "hx", "version": "25.01"},
        "container": {"ports": [], "mounts": [], "env": [], "network": False},
    }
    app._github.parse_manifest.return_value = fake_manifest
    app.run("helix", ["myfile.txt"])
    app._runtime.run.assert_called_once_with(
        "helix", "winbridge-helix:latest", fake_manifest, ["myfile.txt"]
    )


def test_run_native_package_exits(app):
    app._db.get.return_value = {"name": "nginx", "source": "native", "container_id": None}
    with pytest.raises(SystemExit):
        app.run("nginx", [])


def test_run_not_installed_exits(app):
    app._db.get.return_value = None
    with pytest.raises(SystemExit):
        app.run("helix", [])
