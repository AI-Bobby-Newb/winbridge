from __future__ import annotations
import subprocess
from winbridge.adapters.base import Adapter


class XbpsAdapter(Adapter):
    def install(self, package: str) -> None:
        subprocess.run(["xbps-install", "-y", package], check=True)

    def remove(self, package: str) -> None:
        subprocess.run(["xbps-remove", "-y", package], check=True)

    def update(self, package: str) -> None:
        subprocess.run(["xbps-install", "-yu", package], check=True)

    def upgrade(self) -> None:
        subprocess.run(["xbps-install", "-Syu"], check=True)

    def search(self, query: str) -> list[str]:
        result = subprocess.run(
            ["xbps-query", "-Rs", query], capture_output=True, text=True, check=True
        )
        names = []
        for line in result.stdout.splitlines():
            parts = line.strip().split()
            if len(parts) >= 2:
                pkg_ver = parts[1]
                # xbps format: name-version_revision, find where version starts (digit after -)
                for i, segment in enumerate(pkg_ver.split("-")):
                    if segment and segment[0].isdigit():
                        # Found version, everything before this is the name
                        name = "-".join(pkg_ver.split("-")[:i])
                        break
                else:
                    # No version found, use the whole thing
                    name = pkg_ver
                names.append(name)
        return names
