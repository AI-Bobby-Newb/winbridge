from __future__ import annotations

import hashlib
import sys
import tarfile
import zipfile
from pathlib import Path

import httpx
from rich.console import Console

from winbridge.adapters.base import Adapter
from winbridge.container import ContainerRuntime
from winbridge.db import PackageDB
from winbridge.github import GitHubBackend
from winbridge.resolver import ParsedPackage, resolve

console = Console()


class WinbridgeApp:
    def __init__(
        self,
        db: PackageDB,
        adapter: Adapter,
        github: GitHubBackend,
        runtime: ContainerRuntime,
    ) -> None:
        self._db = db
        self._adapter = adapter
        self._github = github
        self._runtime = runtime

    # ------------------------------------------------------------------ install

    def install(self, spec: str) -> None:
        pkg = resolve(spec)
        if pkg.backend == "native":
            self._install_native(pkg)
        else:
            self._install_github(pkg)

    def _install_native(self, pkg: ParsedPackage) -> None:
        console.print(f"[bold]Installing[/bold] {pkg.name} via native package manager...")
        self._adapter.install(pkg.name)
        self._db.record_install(name=pkg.name, version="", source="native")
        console.print(f"[green]✓[/green] {pkg.name} installed.")

    def _install_github(self, pkg: ParsedPackage) -> None:
        console.print(f"[bold]Fetching[/bold] {pkg.repo} from GitHub...")
        release = self._github.fetch_release(pkg.repo, pkg.tag)
        version = release["tag_name"]
        asset = self._github.select_asset(release["assets"])

        console.print(f"[bold]Downloading[/bold] {asset['name']}...")
        binary_path = self._download_and_extract(asset, pkg.name, version)

        manifest_path = binary_path.parent / "winbridge.toml"
        manifest = self._github.parse_manifest(manifest_path)
        if manifest["package"]["binary"] is None:
            manifest["package"]["binary"] = pkg.name

        manifest_hash = self._hash_manifest(manifest_path)

        console.print("[bold]Building[/bold] container image...")
        image_name = self._runtime.build_image(pkg.name, binary_path, manifest)

        self._db.record_install(
            name=pkg.name,
            version=version,
            source="github",
            repo=pkg.repo,
            container_id=image_name,
            manifest_hash=manifest_hash,
        )
        console.print(
            f"[green]✓[/green] {pkg.name} {version} installed. "
            f"Run with: [bold]pkg run {pkg.name}[/bold]"
        )

    # ------------------------------------------------------------------ remove

    def remove(self, spec: str) -> None:
        pkg = resolve(spec)
        record = self._db.get(pkg.name)
        if record is None:
            console.print(f"[red]Error:[/red] {pkg.name} is not installed.")
            sys.exit(1)

        if record["source"] == "github" and record["container_id"]:
            console.print(f"[bold]Removing[/bold] container image {record['container_id']}...")
            self._runtime.remove_image(record["container_id"])
        else:
            console.print(f"[bold]Removing[/bold] {pkg.name}...")
            self._adapter.remove(pkg.name)

        self._db.record_remove(pkg.name)
        console.print(f"[green]✓[/green] {pkg.name} removed.")

    # ------------------------------------------------------------------ query

    def list_packages(self, source: str | None = None) -> list[dict]:
        return self._db.list_all(source=source)

    def info(self, name: str) -> dict | None:
        return self._db.get(name)

    # ------------------------------------------------------------------ run

    def run(self, name: str, args: list[str]) -> None:
        record = self._db.get(name)
        if record is None:
            console.print(f"[red]Error:[/red] {name} is not installed.")
            sys.exit(1)
        if record["source"] != "github":
            console.print(
                f"[red]Error:[/red] {name} is a native package — run it directly, not via 'pkg run'."
            )
            sys.exit(1)

        manifest_path = (
            Path.home() / ".local" / "share" / "winbridge" / "packages"
            / name / record["version"] / "winbridge.toml"
        )
        manifest = self._github.parse_manifest(manifest_path)
        self._runtime.run(name, record["container_id"], manifest, args)

    # ------------------------------------------------------------------ helpers

    def _download_and_extract(self, asset: dict, name: str, version: str) -> Path:
        dest_dir = (
            Path.home() / ".local" / "share" / "winbridge" / "packages"
            / name / version
        )
        dest_dir.mkdir(parents=True, exist_ok=True)

        archive_path = dest_dir / asset["name"]
        with httpx.stream("GET", asset["browser_download_url"], follow_redirects=True) as r:
            r.raise_for_status()
            with open(archive_path, "wb") as f:
                for chunk in r.iter_bytes():
                    f.write(chunk)

        self._extract_archive(archive_path, dest_dir)
        archive_path.unlink(missing_ok=True)
        return self._find_binary(dest_dir, name)

    def _extract_archive(self, archive: Path, dest: Path) -> None:
        n = archive.name
        if n.endswith((".tar.xz", ".tar.gz", ".tar.bz2", ".tar.zst")):
            with tarfile.open(archive) as tf:
                tf.extractall(dest, filter="data")
        elif n.endswith(".zip"):
            with zipfile.ZipFile(archive) as zf:
                zf.extractall(dest)
        # Raw binary: leave as-is

    def _find_binary(self, directory: Path, name: str) -> Path:
        executables = [
            f for f in directory.rglob("*")
            if f.is_file() and (f.stat().st_mode & 0o111)
        ]
        named = [f for f in executables if f.name == name]
        if named:
            return named[0]
        if executables:
            return max(executables, key=lambda f: f.stat().st_size)
        raise FileNotFoundError(f"No executable binary found in {directory}")

    def _hash_manifest(self, path: Path) -> str | None:
        if not path.exists():
            return None
        return hashlib.sha256(path.read_bytes()).hexdigest()
