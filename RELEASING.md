# Releasing

## How a release happens

Commits to `main` follow Conventional Commits. release-please keeps a release pull request open that collects them into a version bump and a changelog entry. Merging that pull request tags `vX.Y.Z` and creates the GitHub release.

The `build` job then builds the sdist and the wheel, checks them, and runs the whole suite against the installed wheel. The `publish` job waits for approval in the `pypi` environment, then uploads through trusted publishing, with no token stored anywhere.

After the upload, the `bump` job opens a draft pull request on `funkadelic/ha-rainpoint` titled `fix(deps): bump aiorainpoint to X.Y.Z`, from the branch `automated/aiorainpoint-bump`. It changes only the `aiorainpoint` pin in the integration's `manifest.json`. Merging it ships the new client in the integration's next release. The job waits until PyPI serves the version before it pushes, so the integration's checks never install a pin that is not there yet.

## When the bump job does nothing

The job exits green without pushing when the version is already pinned on the integration's `main`, when an open bump pull request already pins that version or a newer one, or when the version is a pre-release. Re-running it never churns the branch or opens a second pull request, and two releases finishing out of order never move the pin backwards.

A failed bump job is re-run alone from the release run. It never publishes again. If the job cannot be used at all, open a pull request on the integration with the same title that changes only the pin.

## TestPyPI rehearsal

Dispatching the workflow with a ref uploads that ref to TestPyPI only. A rehearsal never creates a release, so it never opens a bump pull request.

## Pre-releases

A pre-release must never outlive the stable release of its own version.

Delete it with `gh release delete <tag> --yes --cleanup-tag` as soon as its purpose ends. If someone still needs it after the stable release ships, freeze releases until they are done, or set `last-release-sha` in `release-please-config.json` to the stable release's commit as a temporary bound.

The reason: release-please reads a pre-release tag as the release of its version. One that outranks the stable tag while pointing at a commit off `main` leaves release-please no stopping point, so it rebuilds the changelog from the first commit.

A version uploaded to PyPI can never be uploaded again, so a pre-release tag costs a version number for good. The integration's release check also refuses a stable release that pins a pre-release.
