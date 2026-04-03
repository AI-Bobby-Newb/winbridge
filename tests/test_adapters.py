import pytest
from unittest.mock import patch, MagicMock
from winbridge.adapters.base import Adapter
from winbridge.adapters.apt import AptAdapter


def test_adapter_is_abstract():
    with pytest.raises(TypeError):
        Adapter()


@pytest.fixture
def apt():
    return AptAdapter()


def test_apt_install(apt):
    with patch("subprocess.run") as mock_run:
        apt.install("nginx")
        mock_run.assert_called_once_with(["apt", "install", "-y", "nginx"], check=True)


def test_apt_remove(apt):
    with patch("subprocess.run") as mock_run:
        apt.remove("nginx")
        mock_run.assert_called_once_with(["apt", "remove", "-y", "nginx"], check=True)


def test_apt_update(apt):
    with patch("subprocess.run") as mock_run:
        apt.update("nginx")
        mock_run.assert_called_once_with(
            ["apt", "install", "--only-upgrade", "-y", "nginx"], check=True
        )


def test_apt_upgrade(apt):
    with patch("subprocess.run") as mock_run:
        apt.upgrade()
        calls = [c.args[0] for c in mock_run.call_args_list]
        assert ["apt", "update"] in calls
        assert ["apt", "upgrade", "-y"] in calls


def test_apt_search(apt):
    mock_result = MagicMock()
    mock_result.stdout = "nginx - high performance web server\ncurl - command line tool\n"
    with patch("subprocess.run", return_value=mock_result):
        results = apt.search("nginx")
        assert results == ["nginx", "curl"]
