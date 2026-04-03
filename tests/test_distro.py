from unittest.mock import mock_open, patch
import pytest
from winbridge.distro import detect_distro, DistroNotSupportedError

DEBIAN_OS_RELEASE = 'ID=ubuntu\nID_LIKE=debian\nVERSION_ID="22.04"'
RHEL_OS_RELEASE = "ID=fedora\nID_LIKE=rhel"
ARCH_OS_RELEASE = "ID=arch"
SUSE_OS_RELEASE = 'ID=opensuse-tumbleweed\nID_LIKE="suse opensuse"'
ALPINE_OS_RELEASE = "ID=alpine"
VOID_OS_RELEASE = "ID=void"
UNKNOWN_OS_RELEASE = "ID=gentoo"


def _mock_release(content: str):
    return patch("builtins.open", mock_open(read_data=content))


def test_detect_debian():
    with _mock_release(DEBIAN_OS_RELEASE):
        assert detect_distro() == "debian"


def test_detect_rhel():
    with _mock_release(RHEL_OS_RELEASE):
        assert detect_distro() == "rhel"


def test_detect_arch():
    with _mock_release(ARCH_OS_RELEASE):
        assert detect_distro() == "arch"


def test_detect_suse():
    with _mock_release(SUSE_OS_RELEASE):
        assert detect_distro() == "suse"


def test_detect_alpine():
    with _mock_release(ALPINE_OS_RELEASE):
        assert detect_distro() == "alpine"


def test_detect_void():
    with _mock_release(VOID_OS_RELEASE):
        assert detect_distro() == "void"


def test_unsupported_distro():
    with _mock_release(UNKNOWN_OS_RELEASE):
        with pytest.raises(DistroNotSupportedError, match="gentoo"):
            detect_distro()
