from __future__ import annotations
import subprocess
from winbridge.adapters.base import Adapter


class ApkAdapter(Adapter):
    def install(self, package: str) -> None:
        subprocess.run(["apk", "add", package], check=True)

    def remove(self, package: str) -> None:
        subprocess.run(["apk", "del", package], check=True)

    def update(self, package: str) -> None:
        subprocess.run(["apk", "upgrade", package], check=True)

    def upgrade(self) -> None:
        subprocess.run(["apk", "update"], check=True)
        subprocess.run(["apk", "upgrade"], check=True)

    def search(self, query: str) -> list[str]:
        result = subprocess.run(
            ["apk", "search", query], capture_output=True, text=True, check=True
        )
        return [line.strip() for line in result.stdout.splitlines() if line.strip()]
