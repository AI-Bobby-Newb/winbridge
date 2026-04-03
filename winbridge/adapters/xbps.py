from __future__ import annotations
import subprocess
from winbridge.adapters.base import Adapter


class XbpsAdapter(Adapter):
    def install(self, package: str) -> None:
        subprocess.run(["xbps-install", "-y", package], check=True)

    def remove(self, package: str) -> None:
        subprocess.run(["xbps-remove", "-y", package], check=True)

    def update(self, package: str) -> None:
        subprocess.run(["xbps-install", "-u", package], check=True)

    def upgrade(self) -> None:
        subprocess.run(["xbps-install", "-Su"], check=True)

    def search(self, query: str) -> list[str]:
        result = subprocess.run(
            ["xbps-query", "-Rs", query], capture_output=True, text=True, check=True
        )
        names = []
        for line in result.stdout.splitlines():
            parts = line.strip().split()
            if len(parts) >= 2:
                pkg_ver = parts[1]
                name = pkg_ver.rsplit("-", 1)[0] if "-" in pkg_ver else pkg_ver
                names.append(name)
        return names
