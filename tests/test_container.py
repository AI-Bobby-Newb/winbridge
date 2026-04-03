import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock
from winbridge.container import ContainerRuntime, NoRuntimeError

MANIFEST = {
    "package": {"name": "helix", "binary": "hx", "version": "25.01"},
    "container": {"ports": [], "mounts": ["$HOME/.config/helix:/root/.config/helix"], "env": [], "network": False},
}


@pytest.fixture
def runtime(tmp_path: Path):
    return ContainerRuntime(runtime_bin="podman", packages_dir=tmp_path)


def test_detect_podman():
    with patch("shutil.which", side_effect=lambda x: "/usr/bin/podman" if x == "podman" else None):
        rt = ContainerRuntime.detect()
        assert rt._runtime_bin == "podman"


def test_detect_docker_fallback():
    with patch("shutil.which", side_effect=lambda x: "/usr/bin/docker" if x == "docker" else None):
        rt = ContainerRuntime.detect()
        assert rt._runtime_bin == "docker"


def test_detect_none_raises():
    with patch("shutil.which", return_value=None):
        with pytest.raises(NoRuntimeError):
            ContainerRuntime.detect()


def test_build_image(runtime, tmp_path: Path):
    binary = tmp_path / "hx"
    binary.write_bytes(b"fake")
    with patch("subprocess.run") as mock_run:
        image_name = runtime.build_image("helix", binary, MANIFEST)
    assert image_name == "winbridge-helix:latest"
    cmd = mock_run.call_args.args[0]
    assert cmd[0] == "podman"
    assert "build" in cmd
    assert "winbridge-helix:latest" in cmd


def test_run_with_network_disabled(runtime):
    with patch("subprocess.run") as mock_run:
        runtime.run("helix", "winbridge-helix:latest", MANIFEST, args=[])
    cmd = mock_run.call_args.args[0]
    assert "--network=none" in cmd
    assert "winbridge-helix:latest" in cmd


def test_run_passes_args(runtime):
    with patch("subprocess.run") as mock_run:
        runtime.run("helix", "winbridge-helix:latest", MANIFEST, args=["myfile.txt"])
    cmd = mock_run.call_args.args[0]
    assert "myfile.txt" in cmd


def test_remove_image(runtime):
    with patch("subprocess.run") as mock_run:
        runtime.remove_image("winbridge-helix:latest")
    cmd = mock_run.call_args.args[0]
    assert cmd[0] == "podman"
    assert "rmi" in cmd
    assert "winbridge-helix:latest" in cmd
