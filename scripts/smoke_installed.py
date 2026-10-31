"""Smoke-check an installed aiorainpoint; run it under the target venv's interpreter with -I from outside any checkout."""

from __future__ import annotations

import pathlib
import sys
from importlib.metadata import version

import aiorainpoint
from aiorainpoint.mqtt import MQTT_TLS_CA_CERT
from aiorainpoint.product_catalog import get_catalog_entry, get_catalog_fingerprint


def main(expected_version: str | None) -> int:
    """Print each failed check to stderr and return 1, or print ok and return 0."""
    package_file = aiorainpoint.__file__ or ""
    checks = [
        (package_file.startswith(sys.prefix), "package not imported from the venv"),
        (get_catalog_fingerprint() is not None, "catalog did not load"),
        (bool(get_catalog_entry("HCS702B")), "known model missing from the catalog"),
        (pathlib.Path(MQTT_TLS_CA_CERT).is_file(), "CA cert missing"),
        ((pathlib.Path(package_file).parent / "py.typed").exists(), "py.typed missing"),
    ]
    if expected_version:
        installed = version("aiorainpoint")
        checks.append((installed == expected_version, f"installed version {installed} is not {expected_version}"))
    failures = [message for passed, message in checks if not passed]
    for message in failures:
        print(message, file=sys.stderr)
    if failures:
        return 1
    print("ok")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else None))
