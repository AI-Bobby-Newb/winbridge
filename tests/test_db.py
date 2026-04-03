import pytest
from pathlib import Path
from winbridge.db import PackageDB


@pytest.fixture
def db(tmp_path: Path) -> PackageDB:
    return PackageDB(tmp_path / "test.db")


def test_record_and_get_native_package(db: PackageDB):
    db.record_install(name="nginx", version="1.24.0", source="native")
    pkg = db.get("nginx")
    assert pkg is not None
    assert pkg["name"] == "nginx"
    assert pkg["version"] == "1.24.0"
    assert pkg["source"] == "native"
    assert pkg["repo"] is None
    assert pkg["container_id"] is None
    assert pkg["install_date"]  # must be a non-empty ISO timestamp


def test_record_and_get_github_package(db: PackageDB):
    db.record_install(
        name="helix",
        version="25.01",
        source="github",
        repo="helix-editor/helix",
        container_id="winbridge-helix:latest",
        manifest_hash="abc123",
    )
    pkg = db.get("helix")
    assert pkg["repo"] == "helix-editor/helix"
    assert pkg["container_id"] == "winbridge-helix:latest"
    assert pkg["manifest_hash"] == "abc123"


def test_get_nonexistent_returns_none(db: PackageDB):
    assert db.get("doesnotexist") is None


def test_record_remove(db: PackageDB):
    db.record_install(name="curl", version="8.0", source="native")
    db.record_remove("curl")
    assert db.get("curl") is None


def test_list_all(db: PackageDB):
    db.record_install(name="nginx", version="1.24", source="native")
    db.record_install(name="helix", version="25.01", source="github", repo="helix-editor/helix")
    assert len(db.list_all()) == 2


def test_list_by_source(db: PackageDB):
    db.record_install(name="nginx", version="1.24", source="native")
    db.record_install(name="helix", version="25.01", source="github", repo="helix-editor/helix")
    assert db.list_all(source="native")[0]["name"] == "nginx"
    assert db.list_all(source="github")[0]["name"] == "helix"


def test_record_install_upserts(db: PackageDB):
    db.record_install(name="nginx", version="1.24", source="native")
    db.record_install(name="nginx", version="1.25", source="native")
    assert db.get("nginx")["version"] == "1.25"
