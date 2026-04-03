from __future__ import annotations

from pathlib import Path

from winbridge.adapters.apt import AptAdapter
from winbridge.adapters.apk import ApkAdapter
from winbridge.adapters.dnf import DnfAdapter
from winbridge.adapters.pacman import PacmanAdapter
from winbridge.adapters.xbps import XbpsAdapter
from winbridge.adapters.zypper import ZypperAdapter
from winbridge.app import WinbridgeApp
from winbridge.container import ContainerRuntime
from winbridge.db import PackageDB
from winbridge.distro import detect_distro
from winbridge.github import GitHubBackend

_ADAPTER_MAP = {
    "debian": AptAdapter,
    "rhel":   DnfAdapter,
    "arch":   PacmanAdapter,
    "suse":   ZypperAdapter,
    "alpine": ApkAdapter,
    "void":   XbpsAdapter,
}

_DB_PATH = Path.home() / ".local" / "share" / "winbridge" / "winbridge.db"


def build_app() -> WinbridgeApp:
    distro = detect_distro()
    adapter_cls = _ADAPTER_MAP[distro]
    _DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    return WinbridgeApp(
        db=PackageDB(_DB_PATH),
        adapter=adapter_cls(),
        github=GitHubBackend(),
        runtime=ContainerRuntime.detect(),
    )
