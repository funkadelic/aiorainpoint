# Contributing

Thanks for your interest in improving `aiorainpoint`. Bug reports and PRs are welcome. To request support for a new device, open a new device issue on [ha-rainpoint](https://github.com/funkadelic/ha-rainpoint/issues/new/choose) and attach its diagnostics file.

## Development setup

The library supports Python 3.13 and later, and CI runs on both 3.13 and 3.14.

The tests run against the installed package, never the checkout. Install it non-editable into a venv outside the repo. An editable install, or a `PYTHONPATH` pointing at `src/`, hides packaging mistakes that only show up in the wheel.

Install [uv](https://docs.astral.sh/uv/) if you don't have it, then from the repo root:

```bash
uv venv --python 3.14 ~/venvs/aiorainpoint
source ~/venvs/aiorainpoint/bin/activate
uv pip install . -r requirements-test.txt ruff
```

With pip instead:

```bash
python3.14 -m venv ~/venvs/aiorainpoint
source ~/venvs/aiorainpoint/bin/activate
pip install . -r requirements-test.txt ruff
```

## Running checks

Reinstall after every source change, or the tests run against your previous code:

```bash
uv pip install --reinstall --no-deps .   # with pip: pip install --force-reinstall --no-deps .
```

Then:

```bash
python -m pytest    # test suite with coverage
ruff check .        # lint
ruff format .       # format
mypy                # type-check
```

`pytest` fails below 100% branch coverage.

To run the same hooks on every commit, install [pre-commit](https://pre-commit.com/) and run `pre-commit install`. The hooks include the test suite, so commit with the venv active and the package reinstalled.

CI runs `ruff`, `mypy` and the suite on every PR. The suite runs on Python 3.14, at the oldest supported versions of `aiohttp` and `paho-mqtt`, and against the built wheel. A separate job checks that the dependencies still resolve against Home Assistant's constraints. pre-commit.ci runs the hygiene hooks and pushes any fixes to the branch. Coverage goes to Codecov, and SonarCloud scans PRs that change source or test files.

Every action in `.github/workflows/` is pinned to a full commit SHA with the version in a trailing comment, e.g. `uses: actions/checkout@3d3c42e... # v7.0.1`. A tag can be repointed at new code without review, so a new `uses:` line needs a SHA rather than `@v4`. Dependabot reads the trailing comment and bumps both parts together.

## Mutation testing (optional)

```bash
uv pip install --group mutation                         # or: pip install --group mutation
mutmut run --max-children 4 'aiorainpoint.utils.*'      # one module
mutmut results                                          # what survived
mutmut show MUTANT_NAME                                 # one of those names, and its exact change
```

Scope a run to the module you're working on. `mutants/` is the working copy mutmut builds; it is gitignored and safe to delete.

Pass `--max-children` with a number below your core count, because the default of one worker per core can saturate the machine. Some mutants also break a loop so it never ends, and that worker grows until mutmut's timeout stops it. On Linux or WSL with systemd, this keeps a runaway worker from taking the session down with it:

```bash
systemd-run --user --scope -p MemoryMax=10G -p MemorySwapMax=0 -p OOMPolicy=continue nice -n 19 mutmut run --max-children 4 'aiorainpoint.utils.*'
```

A surviving mutant names a change to the source that no test objects to. Sometimes that means a missing assertion, and sometimes the line doesn't matter.

Configuration lives in `pyproject.toml` under `[tool.mutmut]`, with comments explaining why some tests are deselected for those runs.

## Changing the public API

The public surface is `aiorainpoint.__all__`, and `tests/test_public_api.py` pins it. To add or remove a name, change `__init__.py` and `EXPECTED_PUBLIC_NAMES` in the same commit. Everything exported needs a docstring, and so does every public method of an exported class.

Underscore names stay private to their modules and are never re-exported. Removing or renaming a public name is a breaking change, so mark it with `!` in the PR title and list what changed in a `BREAKING CHANGE` footer.

## Logging cloud data

Debug logs get pasted into public issues, so log lines on cloud-record paths carry only keys, integer counts, and the hardware model and model code. Never log `deviceName`, `productKey`, `iotId`, a MAC, a home or device name, the account email, or any other text from the cloud.

Log anything else from a cloud record through `utils.summarize_record`, which shows its shape and field names but no values. In a log call, wrap the record in `utils._RecordSummary`, which does that work only when a handler formats the line.

## Adding a new device model

Model constants and decoders live here, so a new model starts in this repo and finishes in ha-rainpoint.

1. Add `MODEL_XXX = "XXX"` to `models.py`, and add the model to `HAND_WRITTEN_MODELS`.
2. Write `decode_xxx(raw: str) -> dict` in `decoders.py`, with a docstring. Return at least `type`, `rssi_dbm` and `raw_bytes`, plus any device-specific fields. Use `_parse_rainpoint_payload` and `_parse_tlv_payload` from `utils.py`.
3. Add tests to `tests/test_decoders.py` that cover every branch of the decoder, with sample payloads in `tests/payload_samples.py`.
4. Export it: add `decode_xxx` to `__init__.py` and to `EXPECTED_PUBLIC_NAMES`.
5. Update `_DECODERS_PY_SHA256` in `tests/test_generic_decoder.py` to the output of `sha256sum src/aiorainpoint/decoders.py`. The pin catches the generic decoder reaching into this file, so a deliberate decoder change moves it in the same commit.

After the release, the integration side is in ha-rainpoint's [CONTRIBUTING.md](https://github.com/funkadelic/ha-rainpoint/blob/main/CONTRIBUTING.md).

## Scripts

`scripts/` holds maintainer tools that talk to the real cloud. They read credentials from the environment (`RAINPOINT_EMAIL`, `RAINPOINT_PASSWORD`), never from a committed file. Use a second account, because the cloud keeps one session per account.

## Versioning

Releases are automated by `release-please`, so don't bump the version or edit `CHANGELOG.md` by hand. See [RELEASING.md](RELEASING.md).

## Commit and PR style

PR titles follow Conventional Commits (`feat`, `fix`, `perf`, `refactor`, `docs`, `test`, `ci`, `build`, `chore`). PRs squash-merge into `main`, so the title becomes the commit subject that release-please parses, and a non-conventional title silently skips the release.

Keep PRs focused; large multi-concern diffs are harder to review.
