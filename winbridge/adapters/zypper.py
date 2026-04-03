from __future__ import annotations
import subprocess
from winbridge.adapters.base import Adapter


class ZypperAdapter(Adapter):
    def install(self, package: str) -> None:
        subprocess.run(["zypper", "install", "-y", package], check=True)

    def remove(self, package: str) -> None:
        subprocess.run(["zypper", "remove", "-y", package], check=True)

    def update(self, package: str) -> None:
        subprocess.run(["zypper", "update", "-y", package], check=True)

    def upgrade(self) -> None:
        subprocess.run(["zypper", "update", "-y"], check=True)

    def search(self, query: str) -> list[str]:
        result = subprocess.run(
            ["zypper", "search", query], capture_output=True, text=True, check=True
        )
        return [
            parts[1]
            for line in result.stdout.splitlines()
            if "|" in line
            for parts in [[p.strip() for p in line.split("|")]]
            if len(parts) >= 2 and parts[1] and parts[1] != "Name"
        ]
