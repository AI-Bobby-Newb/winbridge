from __future__ import annotations

import subprocess
from winbridge.adapters.base import Adapter


class AptAdapter(Adapter):
    def install(self, package: str) -> None:
        subprocess.run(["apt", "install", "-y", package], check=True)

    def remove(self, package: str) -> None:
        subprocess.run(["apt", "remove", "-y", package], check=True)

    def update(self, package: str) -> None:
        subprocess.run(["apt", "install", "--only-upgrade", "-y", package], check=True)

    def upgrade(self) -> None:
        subprocess.run(["apt", "update"], check=True)
        subprocess.run(["apt", "upgrade", "-y"], check=True)

    def search(self, query: str) -> list[str]:
        result = subprocess.run(
            ["apt-cache", "search", query],
            capture_output=True, text=True, check=True,
        )
        return [
            line.split(" - ")[0]
            for line in result.stdout.splitlines()
            if " - " in line
        ]
