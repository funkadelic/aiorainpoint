#!/usr/bin/env python3
"""Regenerate the committed, trimmed RainPoint product catalog.

The integration ships a committed snapshot of RainPoint's product-model
catalog at src/aiorainpoint/data/product_catalog.json and
never fetches it from RainPoint at runtime. This script is the maintainer
tool that keeps that snapshot up to date: it pulls the live catalog, which
needs no login, trims it down to the fields the client actually uses, and
either writes the result to the committed file or diffs it against what is
already committed.

Usage:
    python scripts/refresh_product_catalog.py
    python scripts/refresh_product_catalog.py --check

Write mode (the default) overwrites the committed catalog file with a fresh,
trimmed pull. --check mode never writes; it prints a drift summary and exits
nonzero when the committed file no longer matches a live pull, so it is safe
to run on a schedule in CI.

Exit codes: 0 clean, 1 drift, a failed fetch or a refused write.
"""

from __future__ import annotations

import argparse
import asyncio
import json
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parent.parent
_CATALOG_PATH = _REPO_ROOT / "src" / "aiorainpoint" / "data" / "product_catalog.json"

# Per dp entry, keep only the fields the loader/enrichment needs. Drop
# UI/provisioning metadata the RainPoint catalog also carries.
#
# dpLen is RainPoint's own byte count and is what the enrichment compares a
# decoded field's width against; dpDataType ("U8", "S16", ...) is kept for its
# signedness letter. portNumber is deliberately absent: it is a per-model
# property, not a per-dp one, and is written once on the variant record.
_KEPT_DP_FIELDS = ("dpCode", "identity", "dpPort", "dpDataType", "dpLen")

# Identity namespaces kept in the committed snapshot.
#
# STA_ entries are the status datapoints the generic decoder actually sees in a
# payload. CTL_ entries are the control datapoints the generic-control
# allowlist is built from. The RainPoint catalog also carries P_/C_/S_/ATTR_/MAX_/
# RD_ provisioning, config, and UI metadata that no code path in this
# integration reads, so it is dropped rather than shipped to every user.
_KEPT_IDENTITY_PREFIXES = ("STA_", "CTL_")

# Per-variant provenance flags copied straight from the RainPoint entry. No code
# path decodes with them; they exist so a maintainer triaging an unfamiliar
# model can tell what kind of catalog record it is without re-fetching the raw
# RainPoint response.
#
# hasDistribution marks a record the app can actually pair, which is the
# closest thing the catalog has to "this product exists." HCS003FRF is the
# worked example: false here, absent from RainPoint's manual index and from the
# app's add-device list, yet it carried a hand-written decoder claiming
# moisture support for a device with no moisture datapoint.
#
# Read them as triage signals, not verdicts. false does not mean discontinued:
# accessory and sub-device records (accessoryFlag true) are false too, and so
# are several models this integration genuinely supports.
_KEPT_PROVENANCE_FIELDS = ("hasDistribution", "isMainDevice", "accessoryFlag")

# Seconds allowed for the catalog fetch. Far below aiohttp's five-minute
# default, which is long enough that a stalled run looks wedged.
_DEFAULT_TIMEOUT_SECONDS = 90.0

# Bucket key for RainPoint entries carrying no modelCode. Duplicated from
# src/aiorainpoint/_product_catalog.py rather than imported, so
# trim_catalog stays importable without the package. A test asserts the two
# stay in step.
UNCODED_VARIANT = "*"


def trim_catalog(raw: list[dict]) -> dict:
    """Trim a raw RainPoint productModel catalog to the committed snapshot shape.

    raw is the list returned by RainPointClient.get_product_catalog(): one
    entry per RainPoint model, each carrying a "model" name, an optional
    "modelCode", a model-level "portNumber", and a "dp" list of per-datapoint
    metadata dicts. Returns an object keyed by model string then by modelCode,
    whose values are {"portNumber": ..., "dp": [...]} records carrying whichever
    of _KEPT_PROVENANCE_FIELDS RainPoint supplied as booleans. Every named
    model is kept, with only its STA_/CTL_ dp entries, trimmed to
    _KEPT_DP_FIELDS; an entry without a string name and every other identity
    namespace are dropped.

    The model string alone is not a unique key: RainPoint maps some models to
    several modelCodes whose port counts genuinely differ (HIC801W is 0 ports
    under code 278 and 8 under 279), so a flat model-keyed object would silently
    keep whichever variant happened to come last. Entries with no modelCode land
    in the UNCODED_VARIANT bucket. Pure function: no I/O, no network.
    """
    trimmed: dict[str, dict[str, dict]] = {}
    for entry in raw:
        model = entry.get("model")
        if not isinstance(model, str) or not model:
            continue
        model_code = entry.get("modelCode")
        variant = UNCODED_VARIANT if model_code is None else str(model_code)
        dp_entries = [dp for dp in (entry.get("dp") or []) if str(dp.get("identity") or "").startswith(_KEPT_IDENTITY_PREFIXES)]
        port_number = entry.get("portNumber")
        trimmed.setdefault(model, {})[variant] = {
            "portNumber": port_number if isinstance(port_number, int) and not isinstance(port_number, bool) else None,
            **{field: entry[field] for field in _KEPT_PROVENANCE_FIELDS if isinstance(entry.get(field), bool)},
            # Sort by dpCode so re-running against an unchanged RainPoint catalog
            # is deterministic, even if the RainPoint API does not guarantee a
            # stable dp array order across calls. Entries missing dpCode sort
            # last.
            "dp": sorted(
                ({field: dp.get(field) for field in _KEPT_DP_FIELDS} for dp in dp_entries),
                key=lambda d: (d.get("dpCode") is None, d.get("dpCode")),
            ),
        }
    return trimmed


def _write_catalog(trimmed: dict, path: Path) -> None:
    """Write the trimmed catalog with stable key ordering and a trailing newline.

    Writes to a temp file in the same directory first and atomically replaces
    the destination, so an interrupted write (Ctrl-C, disk full, OOM kill)
    cannot leave the previously-committed file truncated or corrupted.
    """
    tmp = path.with_suffix(path.suffix + ".tmp")
    with tmp.open("w", encoding="utf-8") as handle:
        json.dump(trimmed, handle, indent=2, sort_keys=True)
        handle.write("\n")
    tmp.replace(path)


def _load_committed_catalog(path: Path) -> dict:
    """Return the committed snapshot, or {} when the file does not exist yet.

    Unlike the component-side loader this one is deliberately strict: a
    corrupt committed file should stop a maintainer run loudly rather than
    silently compare a fresh pull against an empty catalog and report every
    model as newly added.
    """
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def _changed_fields(committed_variants: dict, fresh_variants: dict) -> set[str]:
    """Return the record keys that differ between two models' variant maps.

    Variants present on only one side count as a difference in every key that
    side declares, so an added or dropped modelCode is never reported as an
    empty change.
    """
    fields: set[str] = set()
    for variant in set(committed_variants) | set(fresh_variants):
        before = committed_variants.get(variant) or {}
        after = fresh_variants.get(variant) or {}
        fields |= {key for key in set(before) | set(after) if before.get(key) != after.get(key)}
    return fields


def _print_drift(committed: dict, fresh: dict) -> bool:
    """Print a human-readable drift summary. Returns True if any drift was found.

    Changed models are split by what actually moved. A snapshot regenerated
    after the trim starts keeping a new record key would otherwise report every
    model as changed with no way to tell that from real catalog drift, which is
    the difference between "commit this" and "read this carefully."
    """
    committed_models = set(committed)
    fresh_models = set(fresh)

    added = sorted(fresh_models - committed_models)
    removed = sorted(committed_models - fresh_models)
    changed = {
        model: _changed_fields(committed[model], fresh[model])
        for model in sorted(committed_models & fresh_models)
        if committed[model] != fresh[model]
    }

    if not added and not removed and not changed:
        print("No drift: the committed catalog matches a fresh pull.")
        return False

    if added:
        print(f"Models added upstream ({len(added)}): {', '.join(added)}")
    if removed:
        print(f"Models removed upstream ({len(removed)}): {', '.join(removed)}")

    substantive = sorted(model for model, fields in changed.items() if fields - set(_KEPT_PROVENANCE_FIELDS))
    metadata_only = sorted(model for model, fields in changed.items() if not fields - set(_KEPT_PROVENANCE_FIELDS))
    if substantive:
        detail = ", ".join(f"{model} ({', '.join(sorted(changed[model]))})" for model in substantive)
        print(f"Models with changed datapoints or ports ({len(substantive)}): {detail}")
    if metadata_only:
        print(f"Models changed only in RainPoint metadata ({len(metadata_only)}): {', '.join(metadata_only)}")
    return True


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    """Build the CLI parser and parse argv (defaults to sys.argv)."""
    parser = argparse.ArgumentParser(
        description="Regenerate the committed RainPoint product catalog from a live RainPoint pull.",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Diff the committed catalog against a fresh live pull and exit nonzero on drift, without writing.",
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=_DEFAULT_TIMEOUT_SECONDS,
        help=f"Seconds to wait for the catalog fetch before giving up (default {_DEFAULT_TIMEOUT_SECONDS:g})",
    )
    return parser.parse_args(argv)


async def _fetch_trimmed_catalog(timeout_seconds: float) -> dict:
    """Pull the live catalog without logging in and return it trimmed.

    aiohttp and the client are imported here so trim_catalog stays importable
    without them. Progress goes to stderr so --check output stays pipeable.
    """
    import aiohttp

    from aiorainpoint._client import fetch_product_catalog

    print(f"Fetching the RainPoint catalog (timeout {timeout_seconds:g}s)...", file=sys.stderr)
    timeout = aiohttp.ClientTimeout(total=timeout_seconds)
    async with aiohttp.ClientSession(timeout=timeout) as session:
        try:
            raw = await fetch_product_catalog(session)
        except TimeoutError:
            print(
                f"Timed out after {timeout_seconds:g}s. Retry, or raise the limit with --timeout.",
                file=sys.stderr,
            )
            raise
    print(f"Fetched {len(raw)} RainPoint model entries.", file=sys.stderr)
    return trim_catalog(raw)


def main(argv: list[str] | None = None) -> int:
    """Run the refresh, returning a process exit code: 0 on a write or a clean --check, else 1."""
    args = _parse_args(argv)
    trimmed = asyncio.run(_fetch_trimmed_catalog(args.timeout))

    if args.check:
        # An empty pull means the fetch failed, not that RainPoint dropped
        # every model. Without this guard the drift report would list the whole
        # committed catalog as "removed upstream" and bury the real cause.
        if not trimmed:
            print(
                "Live pull produced 0 kept models; treating as a fetch failure, not drift.",
                file=sys.stderr,
            )
            return 1
        committed = _load_committed_catalog(_CATALOG_PATH)
        drifted = _print_drift(committed, trimmed)
        return 1 if drifted else 0

    committed = _load_committed_catalog(_CATALOG_PATH)
    if not trimmed:
        print(
            "Refusing to write an empty catalog (live pull produced 0 kept models); "
            "check the RainPoint response before retrying.",
            file=sys.stderr,
        )
        return 1
    if committed and len(trimmed) < len(committed) // 2:
        print(
            f"Refusing to write: model count dropped from {len(committed)} to {len(trimmed)}; "
            "investigate before overwriting the committed catalog.",
            file=sys.stderr,
        )
        return 1

    _write_catalog(trimmed, _CATALOG_PATH)
    print(f"Wrote {len(trimmed)} models to {_CATALOG_PATH}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
