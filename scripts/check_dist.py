"""Check that the built sdist and wheel carry the package data and the pinned CA."""

from __future__ import annotations

import hashlib
import json
import sys
import tarfile
import zipfile
from pathlib import Path

CA_MD5 = "c7a6afb466713832af778a7bcb6d1aef"
_MEMBERS = ("data/product_catalog.json", "certs/ali_iot_ca.crt", "py.typed")


def _check(label: str, files: dict[str, bytes]) -> list[str]:
    """Return one problem string per failed expectation for a name-to-bytes archive view."""
    problems = []
    for rel in _MEMBERS:
        if rel not in files:
            problems.append(f"{label}: missing {rel}")
    ca = files.get("certs/ali_iot_ca.crt")
    if ca is not None and hashlib.md5(ca, usedforsecurity=False).hexdigest() != CA_MD5:
        problems.append(f"{label}: certs/ali_iot_ca.crt md5 is not {CA_MD5}")
    catalog = files.get("data/product_catalog.json")
    if catalog is not None:
        try:
            if not json.loads(catalog):
                problems.append(f"{label}: data/product_catalog.json is empty")
        except ValueError:
            problems.append(f"{label}: data/product_catalog.json is not valid JSON")
    return problems


def _wheel_files(path: Path) -> dict[str, bytes]:
    prefix = "aiorainpoint/"
    with zipfile.ZipFile(path) as zf:
        return {n[len(prefix) :]: zf.read(n) for n in zf.namelist() if n.startswith(prefix)}


def _sdist_files(path: Path) -> dict[str, bytes]:
    with tarfile.open(path) as tf:
        tops = {m.name.split("/", 1)[0] for m in tf.getmembers()}
        if len(tops) != 1:
            raise ValueError(f"expected one top-level directory, found {sorted(tops)}")
        prefix = f"{tops.pop()}/src/aiorainpoint/"
        out = {}
        for m in tf.getmembers():
            if m.isfile() and m.name.startswith(prefix):
                f = tf.extractfile(m)
                if f is not None:
                    out[m.name[len(prefix) :]] = f.read()
        return out


def main(argv: list[str] | None = None) -> int:
    args = sys.argv[1:] if argv is None else argv
    if len(args) != 1:
        print("usage: check_dist.py DIST_DIR", file=sys.stderr)
        return 2
    dist = Path(args[0])
    wheels = sorted(dist.glob("*.whl"))
    sdists = sorted(dist.glob("*.tar.gz"))
    if len(wheels) != 1 or len(sdists) != 1:
        print(f"check_dist: need exactly one wheel and one sdist in {dist}", file=sys.stderr)
        return 1
    failed = False
    for path, reader in ((sdists[0], _sdist_files), (wheels[0], _wheel_files)):
        try:
            problems = _check(path.name, reader(path))
        except (OSError, ValueError, tarfile.TarError, zipfile.BadZipFile) as err:
            problems = [f"{path.name}: unreadable ({err})"]
        for p in problems:
            print(f"check_dist: {p}", file=sys.stderr)
        if problems:
            failed = True
        else:
            print(f"ok: {path.name}")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
