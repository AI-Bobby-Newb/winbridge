from __future__ import annotations
import subprocess
from winbridge.adapters.base import Adapter


class DnfAdapter(Adapter):
    def install(self, package: str) -> None:
        subprocess.run(["dnf", "install", "-y", package], check=True)

    def remove(self, package: str) -> None:
        subprocess.run(["dnf", "remove", "-y", package], check=True)

    def update(self, package: str) -> None:
        subprocess.run(["dnf", "upgrade", "-y", package], check=True)

    def upgrade(self) -> None:
        subprocess.run(["dnf", "upgrade", "-y"], check=True)

    def search(self, query: str) -> list[str]:
        result = subprocess.run(
            ["dnf", "search", query], capture_output=True, text=True, check=True
        )
        names = []
        for line in result.stdout.splitlines():
            # dnf search output: "pkg-name.arch : description"
            if " : " in line and "." in line and not line.startswith(" "):
                names.append(line.split(".")[0].strip())
        return names
