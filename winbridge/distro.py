from __future__ import annotations


class DistroNotSupportedError(Exception):
    pass


_DISTRO_MAP: dict[str, str] = {
    "ubuntu": "debian",
    "debian": "debian",
    "linuxmint": "debian",
    "pop": "debian",
    "fedora": "rhel",
    "centos": "rhel",
    "rhel": "rhel",
    "almalinux": "rhel",
    "rocky": "rhel",
    "arch": "arch",
    "manjaro": "arch",
    "endeavouros": "arch",
    "opensuse-tumbleweed": "suse",
    "opensuse-leap": "suse",
    "alpine": "alpine",
    "void": "void",
}

_ID_LIKE_MAP: dict[str, str] = {
    "debian": "debian",
    "rhel": "rhel",
    "fedora": "rhel",
    "suse": "suse",
    "opensuse": "suse",
}


def detect_distro() -> str:
    """Read /etc/os-release and return a distro family string.

    Returns one of: debian, rhel, arch, suse, alpine, void.
    Raises DistroNotSupportedError for unknown distros.
    """
    fields: dict[str, str] = {}
    with open("/etc/os-release") as f:
        for line in f:
            line = line.strip()
            if "=" not in line or line.startswith("#"):
                continue
            key, _, value = line.partition("=")
            fields[key] = value.strip('"').strip("'")

    distro_id = fields.get("ID", "").lower()
    id_like = fields.get("ID_LIKE", "").lower()

    if distro_id in _DISTRO_MAP:
        return _DISTRO_MAP[distro_id]

    for token in id_like.split():
        if token in _ID_LIKE_MAP:
            return _ID_LIKE_MAP[token]

    raise DistroNotSupportedError(
        f"Unsupported distro: {distro_id!r}. "
        "Supported families: debian, rhel, arch, suse, alpine, void."
    )
