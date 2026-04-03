from __future__ import annotations

import sqlite3
from datetime import datetime, timezone
from pathlib import Path


class PackageDB:
    def __init__(self, path: Path) -> None:
        self._conn = sqlite3.connect(path)
        self._conn.row_factory = sqlite3.Row
        self._conn.execute("""
            CREATE TABLE IF NOT EXISTS packages (
                name         TEXT PRIMARY KEY,
                version      TEXT NOT NULL,
                source       TEXT NOT NULL,
                repo         TEXT,
                install_date TEXT NOT NULL,
                container_id TEXT,
                manifest_hash TEXT
            )
        """)
        self._conn.commit()

    def record_install(
        self,
        name: str,
        version: str,
        source: str,
        repo: str | None = None,
        container_id: str | None = None,
        manifest_hash: str | None = None,
    ) -> None:
        self._conn.execute(
            """
            INSERT INTO packages (name, version, source, repo, install_date, container_id, manifest_hash)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(name) DO UPDATE SET
                version=excluded.version,
                source=excluded.source,
                repo=excluded.repo,
                install_date=excluded.install_date,
                container_id=excluded.container_id,
                manifest_hash=excluded.manifest_hash
            """,
            (
                name, version, source, repo,
                datetime.now(timezone.utc).isoformat(),
                container_id, manifest_hash,
            ),
        )
        self._conn.commit()

    def record_remove(self, name: str) -> None:
        self._conn.execute("DELETE FROM packages WHERE name = ?", (name,))
        self._conn.commit()

    def get(self, name: str) -> dict | None:
        row = self._conn.execute(
            "SELECT * FROM packages WHERE name = ?", (name,)
        ).fetchone()
        return dict(row) if row else None

    def list_all(self, source: str | None = None) -> list[dict]:
        if source:
            rows = self._conn.execute(
                "SELECT * FROM packages WHERE source = ? ORDER BY name", (source,)
            ).fetchall()
        else:
            rows = self._conn.execute(
                "SELECT * FROM packages ORDER BY name"
            ).fetchall()
        return [dict(r) for r in rows]
