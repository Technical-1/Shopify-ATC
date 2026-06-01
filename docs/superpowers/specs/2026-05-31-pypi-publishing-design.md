# Design: Publish `shopify-atc` to PyPI

**Date:** 2026-05-31
**Author:** Jacob Kanfer
**Status:** Approved — ready for implementation plan

## Goal

Make `pip install shopify-atc` work for anyone, and automate secure releases
triggered by GitHub releases. The release pipeline mirrors the established
`pythonforge`/`quickforge` pattern: trusted publishing via OIDC (no stored
secrets), with a manual TestPyPI dry-run path before production releases.

## Background / Current State

The project is already structured as an installable package:

- `pyproject.toml` declares the build backend (`setuptools`), a console entry
  point (`shopify-atc = "shopify_atc.cli:main"`), and a dynamic version sourced
  from `shopify_atc.__init__.__version__` (currently `1.0.0`).
- CI (`.github/workflows/ci.yml`) runs the test suite across Python 3.9–3.13.
- The package name `shopify-atc` is **available** on PyPI (verified: `GET
  https://pypi.org/pypi/shopify-atc/json` → 404).

No code changes are required. The gaps are: discovery metadata, a `LICENSE`
file, and the publishing workflow.

## Non-Goals (YAGNI)

- No changes to runtime code (`client.py`, `formatters.py`, `cli.py`).
- No new runtime dependencies.
- No automated version-bump tooling — the version stays edited by hand in
  `shopify_atc/__init__.py`.
- No documentation site beyond the existing `README.md`.

## Design

### Unit 1 — Enrich `pyproject.toml` metadata

The build configuration is already correct. Add only the metadata PyPI surfaces
on the project page and uses for search/filtering:

- `keywords = ["shopify", "cart", "permalink", "ecommerce", "cli", "scraper"]`
- `classifiers` — at minimum:
  - `Development Status :: 5 - Production/Stable`
  - `Environment :: Console`
  - `Intended Audience :: Developers`
  - `License :: OSI Approved :: MIT License`
  - `Operating System :: OS Independent`
  - `Programming Language :: Python :: 3` and `:: 3.9` through `:: 3.13`
  - `Topic :: Internet`
- `[project.urls]` — `Homepage`, `Repository`, `Issues`, `Documentation`, all
  pointing at `https://github.com/Technical-1/Shopify-ATC`.
- Modern SPDX license declaration: replace `license = {text = "MIT"}` with
  `license = "MIT"` and add `license-files = ["LICENSE"]`. (Requires
  `setuptools>=77`; bump the `build-system.requires` floor accordingly.)
- Add the author email `jacobrk2001@gmail.com` to the existing `authors` entry.

**Depends on:** Unit 2 (the `LICENSE` file must exist for `license-files`).

Also update the README installation section to lead with `pip install
shopify-atc` (keeping the existing local `pipx install .` / editable-install
instructions below it for contributors).

### Unit 2 — Add a `LICENSE` file

Add a standard MIT `LICENSE` file at the repo root, copyright `2026 Jacob
Kanfer`. The project already declares MIT; this makes it concrete for both PyPI
and GitHub's license detection.

### Unit 3 — Add `.github/workflows/publish.yml`

A single workflow with three jobs. Triggers:

- `release: [published]` → production PyPI path
- `workflow_dispatch` → manual TestPyPI dry-run path

Jobs:

1. **build** — checkout, set up Python 3.12, `pip install build`, run
   `python -m build`, upload `dist/` as a workflow artifact. Runs on every
   trigger.
2. **testpypi** — needs `build`; `if: github.event_name == 'workflow_dispatch'`.
   Download the artifact, publish via `pypa/gh-action-pypi-publish@release/v1`
   with `repository-url: https://test.pypi.org/legacy/`. Uses
   `environment: testpypi` and `permissions: id-token: write`.
3. **pypi** — needs `build`; `if: github.event_name == 'release'`. Download the
   artifact, publish via `pypa/gh-action-pypi-publish@release/v1` to production
   PyPI. Uses `environment: pypi` and `permissions: id-token: write`. After a
   successful publish, attach the built `dist/*` (wheel + sdist) to the GitHub
   release, which requires `permissions: contents: write` on that step/job.

No API tokens are stored anywhere; authentication is OIDC trusted publishing.

### Unit 4 — Document the one-time manual setup

These steps require the maintainer's PyPI web login and cannot be automated.
They will be captured in the implementation plan and surfaced to the user as
release instructions:

1. On **pypi.org** → *Publishing* → add a **pending trusted publisher**:
   - PyPI project name: `shopify-atc`
   - Owner: `Technical-1`
   - Repository: `Shopify-ATC`
   - Workflow filename: `publish.yml`
   - Environment name: `pypi`
2. Repeat on **test.pypi.org** with environment name `testpypi`.
3. (Optional but recommended) Create GitHub Environments named `pypi` and
   `testpypi` in repo settings for the OIDC subject to match.
4. First release flow: bump `__version__` in `shopify_atc/__init__.py` → commit
   → create a GitHub release (tag e.g. `v1.0.0`) → the `pypi` job publishes
   automatically.

## Data Flow

```
Developer                GitHub                         PyPI
─────────                ──────                         ────
edit __version__ ─┐
git tag + release ─┼──▶ release:published
                   │      └─▶ build job ──▶ dist/ artifact
                   │            └─▶ pypi job (OIDC) ──────────▶ PyPI
                   │                  └─▶ attach dist to release
                   │
"Run workflow" ────┴──▶ workflow_dispatch
                          └─▶ build job ──▶ dist/ artifact
                                └─▶ testpypi job (OIDC) ─────▶ TestPyPI
```

## Error Handling / Failure Modes

- **Name collision on first publish** — mitigated: name verified available.
- **Trusted publisher not configured** — the `gh-action-pypi-publish` step fails
  with a clear OIDC error; resolved by completing Unit 4 step 1/2. Documented.
- **Re-publishing an existing version** — PyPI rejects duplicate versions; the
  fix is bumping `__version__`. The version is dynamic, so the tag and the
  package version must be kept in sync manually (called out in release docs).
- **`license-files` unsupported** — guarded by bumping the setuptools floor to
  `>=77`.

## Testing / Verification

- Local: `python -m build` produces a valid wheel + sdist; `twine check dist/*`
  passes (run locally as part of implementation verification).
- `pip install dist/*.whl` in a clean venv exposes a working `shopify-atc`
  command (`shopify-atc --version` prints `1.0.0`).
- Existing `pytest` suite continues to pass (no code changed).
- End-to-end OIDC publish is verified via the TestPyPI manual-dispatch path
  before the first production release.

## Acceptance Criteria

1. `pyproject.toml` includes keywords, classifiers, and project URLs; builds
   cleanly with `python -m build`.
2. A root `LICENSE` file exists and PyPI/GitHub detect MIT.
3. `.github/workflows/publish.yml` exists with the three jobs and OIDC config
   described above; CI workflow is unaffected.
4. The README installation section reflects `pip install shopify-atc` once
   published (alongside the existing local-install instructions).
5. Manual trusted-publisher setup steps are documented for the maintainer.
