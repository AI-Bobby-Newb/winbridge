from __future__ import annotations

import re
import shutil
import subprocess
import tempfile
from pathlib import Path


class NoRuntimeError(Exception):
    pass


class ContainerRuntime:
    def __init__(self, runtime_bin: str, packages_dir: Path | None = None) -> None:
        self._runtime_bin = runtime_bin
        self._packages_dir = packages_dir or (
            Path.home() / ".local" / "share" / "winbridge" / "packages"
        )

    @classmethod
    def detect(cls) -> ContainerRuntime:
        for candidate in ("podman", "docker"):
            if shutil.which(candidate):
                return cls(runtime_bin=candidate)
        raise NoRuntimeError(
            "No container runtime found. Install podman (recommended) or docker.\n"
            "  Debian/Ubuntu: apt install podman\n"
            "  Fedora:        dnf install podman\n"
            "  Arch:          pacman -S podman"
        )

    def build_image(self, name: str, binary_path: Path, manifest: dict) -> str:
        image_name = f"winbridge-{name}:latest"
        binary_name = manifest["package"].get("binary") or binary_path.name

        # Validate binary_name is a safe plain filename
        if not re.match(r'^[a-zA-Z0-9._-]+$', binary_name):
            raise ValueError(
                f"Invalid binary name in manifest: {binary_name!r}. "
                "Must contain only letters, digits, dots, hyphens, underscores."
            )

        with tempfile.TemporaryDirectory() as build_dir:
            ctx = Path(build_dir)
            shutil.copy2(binary_path, ctx / binary_name)
            (ctx / "Containerfile").write_text(
                f"FROM alpine:latest\n"
                f"COPY {binary_name} /usr/local/bin/{binary_name}\n"
                f"RUN chmod +x /usr/local/bin/{binary_name}\n"
                f'CMD ["/usr/local/bin/{binary_name}"]\n'
            )
            subprocess.run(
                [self._runtime_bin, "build", "-t", image_name, str(ctx)],
                check=True,
            )
        return image_name

    def run(self, name: str, image_name: str, manifest: dict, args: list[str]) -> None:
        c = manifest.get("container", {})
        binary_name = manifest["package"].get("binary") or name

        cmd = [self._runtime_bin, "run", "--rm", "-it"]

        if not c.get("network", False):
            cmd.append("--network=none")

        for mount in c.get("mounts", []):
            cmd.extend(["-v", mount.replace("$HOME", str(Path.home()))])

        for env_var in c.get("env", []):
            cmd.extend(["-e", env_var])

        for port in c.get("ports", []):
            cmd.extend(["-p", str(port)])

        cmd += [image_name, f"/usr/local/bin/{binary_name}"] + args
        subprocess.run(cmd, check=True)

    def remove_image(self, image_name: str) -> None:
        subprocess.run([self._runtime_bin, "rmi", "-f", image_name], check=True)
