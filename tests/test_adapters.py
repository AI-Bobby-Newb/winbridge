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
    with patch("winbridge.adapters.apt.subprocess.run") as mock_run:
        apt.install("nginx")
        mock_run.assert_called_once_with(["apt", "install", "-y", "nginx"], check=True)


def test_apt_remove(apt):
    with patch("winbridge.adapters.apt.subprocess.run") as mock_run:
        apt.remove("nginx")
        mock_run.assert_called_once_with(["apt", "remove", "-y", "nginx"], check=True)


def test_apt_update(apt):
    with patch("winbridge.adapters.apt.subprocess.run") as mock_run:
        apt.update("nginx")
        mock_run.assert_called_once_with(
            ["apt", "install", "--only-upgrade", "-y", "nginx"], check=True
        )


def test_apt_upgrade(apt):
    with patch("winbridge.adapters.apt.subprocess.run") as mock_run:
        apt.upgrade()
        calls = [c.args[0] for c in mock_run.call_args_list]
        assert calls == [["apt", "update"], ["apt", "upgrade", "-y"]]


def test_apt_search(apt):
    mock_result = MagicMock()
    mock_result.stdout = "nginx - high performance web server\ncurl - command line tool\n"
    with patch("winbridge.adapters.apt.subprocess.run", return_value=mock_result):
        results = apt.search("nginx")
        assert results == ["nginx", "curl"]


from winbridge.adapters.dnf import DnfAdapter
from winbridge.adapters.pacman import PacmanAdapter
from winbridge.adapters.zypper import ZypperAdapter
from winbridge.adapters.apk import ApkAdapter
from winbridge.adapters.xbps import XbpsAdapter


@pytest.fixture
def dnf(): return DnfAdapter()

def test_dnf_install(dnf):
    with patch("winbridge.adapters.dnf.subprocess.run") as m:
        dnf.install("nginx")
        m.assert_called_once_with(["dnf", "install", "-y", "nginx"], check=True)

def test_dnf_remove(dnf):
    with patch("winbridge.adapters.dnf.subprocess.run") as m:
        dnf.remove("nginx")
        m.assert_called_once_with(["dnf", "remove", "-y", "nginx"], check=True)

def test_dnf_update(dnf):
    with patch("winbridge.adapters.dnf.subprocess.run") as m:
        dnf.update("nginx")
        m.assert_called_once_with(["dnf", "upgrade", "-y", "nginx"], check=True)

def test_dnf_upgrade(dnf):
    with patch("winbridge.adapters.dnf.subprocess.run") as m:
        dnf.upgrade()
        m.assert_called_once_with(["dnf", "upgrade", "-y"], check=True)

def test_dnf_search(dnf):
    mock_result = MagicMock()
    mock_result.stdout = "nginx.x86_64 : A web server\ncurl.x86_64 : A URL tool\n"
    with patch("winbridge.adapters.dnf.subprocess.run", return_value=mock_result):
        results = dnf.search("nginx")
        assert "nginx" in results


@pytest.fixture
def pacman(): return PacmanAdapter()

def test_pacman_install(pacman):
    with patch("winbridge.adapters.pacman.subprocess.run") as m:
        pacman.install("nginx")
        m.assert_called_once_with(["pacman", "-S", "--noconfirm", "nginx"], check=True)

def test_pacman_remove(pacman):
    with patch("winbridge.adapters.pacman.subprocess.run") as m:
        pacman.remove("nginx")
        m.assert_called_once_with(["pacman", "-R", "--noconfirm", "nginx"], check=True)

def test_pacman_update(pacman):
    with patch("winbridge.adapters.pacman.subprocess.run") as m:
        pacman.update("nginx")
        m.assert_called_once_with(["pacman", "-S", "--noconfirm", "nginx"], check=True)

def test_pacman_upgrade(pacman):
    with patch("winbridge.adapters.pacman.subprocess.run") as m:
        pacman.upgrade()
        m.assert_called_once_with(["pacman", "-Syu", "--noconfirm"], check=True)

def test_pacman_search(pacman):
    mock_result = MagicMock()
    mock_result.stdout = "community/nginx 1.24.0-1\nextra/curl 8.0-1\n"
    with patch("winbridge.adapters.pacman.subprocess.run", return_value=mock_result):
        results = pacman.search("nginx")
        assert "nginx" in results


@pytest.fixture
def zypper(): return ZypperAdapter()

def test_zypper_install(zypper):
    with patch("winbridge.adapters.zypper.subprocess.run") as m:
        zypper.install("nginx")
        m.assert_called_once_with(["zypper", "install", "-y", "nginx"], check=True)

def test_zypper_remove(zypper):
    with patch("winbridge.adapters.zypper.subprocess.run") as m:
        zypper.remove("nginx")
        m.assert_called_once_with(["zypper", "remove", "-y", "nginx"], check=True)

def test_zypper_update(zypper):
    with patch("winbridge.adapters.zypper.subprocess.run") as m:
        zypper.update("nginx")
        m.assert_called_once_with(["zypper", "update", "-y", "nginx"], check=True)

def test_zypper_upgrade(zypper):
    with patch("winbridge.adapters.zypper.subprocess.run") as m:
        zypper.upgrade()
        m.assert_called_once_with(["zypper", "update", "-y"], check=True)

def test_zypper_search(zypper):
    mock_result = MagicMock()
    mock_result.stdout = "| nginx | An HTTP server | package\n| curl | URL tool | package\n"
    with patch("winbridge.adapters.zypper.subprocess.run", return_value=mock_result):
        results = zypper.search("nginx")
        assert "nginx" in results


@pytest.fixture
def apk(): return ApkAdapter()

def test_apk_install(apk):
    with patch("winbridge.adapters.apk.subprocess.run") as m:
        apk.install("nginx")
        m.assert_called_once_with(["apk", "add", "nginx"], check=True)

def test_apk_remove(apk):
    with patch("winbridge.adapters.apk.subprocess.run") as m:
        apk.remove("nginx")
        m.assert_called_once_with(["apk", "del", "nginx"], check=True)

def test_apk_update(apk):
    with patch("winbridge.adapters.apk.subprocess.run") as m:
        apk.update("nginx")
        m.assert_called_once_with(["apk", "upgrade", "nginx"], check=True)

def test_apk_upgrade(apk):
    with patch("winbridge.adapters.apk.subprocess.run") as m:
        apk.upgrade()
        calls = [c.args[0] for c in m.call_args_list]
        assert calls == [["apk", "update"], ["apk", "upgrade"]]

def test_apk_search(apk):
    mock_result = MagicMock()
    mock_result.stdout = "nginx-1.24.0-r0\ncurl-8.0-r0\n"
    with patch("winbridge.adapters.apk.subprocess.run", return_value=mock_result):
        results = apk.search("nginx")
        assert any("nginx" in r for r in results)


@pytest.fixture
def xbps(): return XbpsAdapter()

def test_xbps_install(xbps):
    with patch("winbridge.adapters.xbps.subprocess.run") as m:
        xbps.install("nginx")
        m.assert_called_once_with(["xbps-install", "-y", "nginx"], check=True)

def test_xbps_remove(xbps):
    with patch("winbridge.adapters.xbps.subprocess.run") as m:
        xbps.remove("nginx")
        m.assert_called_once_with(["xbps-remove", "-y", "nginx"], check=True)

def test_xbps_update(xbps):
    with patch("winbridge.adapters.xbps.subprocess.run") as m:
        xbps.update("nginx")
        m.assert_called_once_with(["xbps-install", "-u", "nginx"], check=True)

def test_xbps_upgrade(xbps):
    with patch("winbridge.adapters.xbps.subprocess.run") as m:
        xbps.upgrade()
        m.assert_called_once_with(["xbps-install", "-Su"], check=True)

def test_xbps_search(xbps):
    mock_result = MagicMock()
    mock_result.stdout = "[*] nginx-1.24.0_1 A high performance HTTP server\n[*] python3-pip-23.0_1 Python package installer\n"
    with patch("winbridge.adapters.xbps.subprocess.run", return_value=mock_result):
        results = xbps.search("nginx")
        assert "nginx" in results
        assert "python3-pip" in results
        assert "python3-pip-23.0" not in results  # wrong strip would produce this
