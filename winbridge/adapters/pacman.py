from __future__ import annotations
import subprocess
from winbridge.adapters.base import Adapter


class PacmanAdapter(Adapter):
    def install(self, package: str) -> None:
        subprocess.run(["pacman", "-S", "--noconfirm", package], check=True)

    def remove(self, package: str) -> None:
        subprocess.run(["pacman", "-R", "--noconfirm", package], check=True)

    def update(self, package: str) -> None:
        subprocess.run(["pacman", "-S", "--noconfirm", package], check=True)

    def upgrade(self) -> None:
        subprocess.run(["pacman", "-Syu", "--noconfirm"], check=True)

    def search(self, query: str) -> list[str]:
        result = subprocess.run(
            ["pacman", "-Ss", query], capture_output=True, text=True, check=True
        )
        return [
            line.split("/")[1].split(" ")[0]
            for line in result.stdout.splitlines()
            if "/" in line and " " in line
        ]
