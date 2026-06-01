# PyPI Publishing Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make `pip install shopify-atc` work for everyone, with automated, secure releases triggered by GitHub releases.

**Architecture:** No runtime code changes. Add a `LICENSE` file, enrich `pyproject.toml` discovery metadata, add a `.github/workflows/publish.yml` that builds and uploads to PyPI via OIDC trusted publishing (TestPyPI on manual dispatch, production PyPI on release), and document the one-time trusted-publisher setup.

**Tech Stack:** Python packaging (`setuptools>=77`, `build`, `twine`), GitHub Actions, `pypa/gh-action-pypi-publish`, OIDC trusted publishing.

---

## File Structure

- Create: `LICENSE` — MIT license text (prerequisite for `license-files`).
- Modify: `pyproject.toml` — metadata (keywords, classifiers, URLs), SPDX license, setuptools floor, dev deps.
- Create: `.github/workflows/publish.yml` — build + publish workflow (3 jobs, OIDC).
- Modify: `README.md` — installation section leads with `pip install shopify-atc`.
- Create: `RELEASING.md` — one-time trusted-publisher setup + per-release steps.

**Ordering note:** `LICENSE` (Task 1) must exist before `pyproject.toml` references it via `license-files` (Task 2). Build verification (Task 3) must come after Task 2.

---

### Task 1: Add the LICENSE file

**Files:**
- Create: `LICENSE`

- [ ] **Step 1: Write the LICENSE file**

Create `LICENSE` with exactly this content:

```
MIT License

Copyright (c) 2026 Jacob Kanfer

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

- [ ] **Step 2: Verify it exists**

Run: `head -1 LICENSE`
Expected: `MIT License`

- [ ] **Step 3: Commit**

```bash
git add LICENSE
git commit -m "chore: add MIT LICENSE file"
```

---

### Task 2: Enrich pyproject.toml metadata

**Files:**
- Modify: `pyproject.toml`

> **Important:** With the SPDX `license = "MIT"` expression and `setuptools>=77`, you must **NOT** include a `License :: OSI Approved :: MIT License` classifier — setuptools will raise a hard error. License is conveyed solely by the `license` field.

- [ ] **Step 1: Replace pyproject.toml with the enriched version**

Replace the entire file contents with:

```toml
[build-system]
requires = ["setuptools>=77"]
build-backend = "setuptools.build_meta"

[project]
name = "shopify-atc"
description = "Generate Shopify add-to-cart permalinks from a store's public products.json."
readme = "README.md"
requires-python = ">=3.9"
license = "MIT"
license-files = ["LICENSE"]
authors = [{name = "Jacob Kanfer", email = "jacobrk2001@gmail.com"}]
keywords = ["shopify", "cart", "permalink", "ecommerce", "cli", "scraper"]
dynamic = ["version"]
dependencies = ["requests>=2.25"]
classifiers = [
    "Development Status :: 5 - Production/Stable",
    "Environment :: Console",
    "Intended Audience :: Developers",
    "Operating System :: OS Independent",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.9",
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",
    "Programming Language :: Python :: 3.13",
    "Topic :: Internet",
]

[project.optional-dependencies]
dev = ["pytest>=7", "build>=1", "twine>=5"]

[project.urls]
Homepage = "https://github.com/Technical-1/Shopify-ATC"
Repository = "https://github.com/Technical-1/Shopify-ATC"
Issues = "https://github.com/Technical-1/Shopify-ATC/issues"
Documentation = "https://github.com/Technical-1/Shopify-ATC#readme"

[project.scripts]
shopify-atc = "shopify_atc.cli:main"

[tool.setuptools.dynamic]
version = {attr = "shopify_atc.__version__"}

[tool.setuptools.packages.find]
include = ["shopify_atc*"]
```

- [ ] **Step 2: Sanity-check the TOML parses**

Run: `python -c "import tomllib; tomllib.load(open('pyproject.toml','rb')); print('ok')"`
Expected: `ok`

- [ ] **Step 3: Commit**

```bash
git add pyproject.toml
git commit -m "chore: enrich package metadata for PyPI (classifiers, urls, keywords, SPDX license)"
```

---

### Task 3: Verify the package builds and installs cleanly

This is the verification gate for Tasks 1–2. No new files; it proves the metadata is publishable.

**Files:** none (verification only)

- [ ] **Step 1: Clean any stale build artifacts**

Run: `rm -rf dist build shopify_atc.egg-info`
Expected: no output (clean exit)

- [ ] **Step 2: Build the sdist and wheel**

Run: `python -m build`
Expected: ends with `Successfully built shopify_atc-1.0.0.tar.gz and shopify_atc-1.0.0-py3-none-any.whl` (filenames may use `shopify-atc`/`shopify_atc` normalization). No errors about license classifiers or `license-files`.

If `build` is not installed: `pip install build` first.

- [ ] **Step 3: Validate metadata with twine**

Run: `python -m twine check dist/*`
Expected: `Checking dist/...: PASSED` for both files.

If `twine` is not installed: `pip install twine` first.

- [ ] **Step 4: Install the wheel in a throwaway venv and run the CLI**

```bash
python -m venv /tmp/atc-verify
/tmp/atc-verify/bin/pip install --quiet dist/*.whl
/tmp/atc-verify/bin/shopify-atc --version
```
Expected: prints `shopify-atc 1.0.0`

- [ ] **Step 5: Clean up the verification venv and artifacts**

Run: `rm -rf /tmp/atc-verify dist build shopify_atc.egg-info`
Expected: clean exit. (Artifacts are git-ignored; nothing to commit in this task.)

---

### Task 4: Update README installation section

**Files:**
- Modify: `README.md` (the `### Installation` block, currently lines ~39–52)

- [ ] **Step 1: Replace the Installation block**

Find this block:

```markdown
### Installation

\`\`\`bash
# Install the CLI (pipx keeps it isolated)
pipx install .

# …or a plain pip install
pip install .

# …or for development, an editable install with test deps
pip install -e ".[dev]"
\`\`\`

This installs a `shopify-atc` command.
```

Replace it with:

```markdown
### Installation

\`\`\`bash
# From PyPI (recommended)
pip install shopify-atc

# …or isolated with pipx
pipx install shopify-atc
\`\`\`

This installs a `shopify-atc` command.

For local development from a clone:

\`\`\`bash
# Editable install with test deps
pip install -e ".[dev]"
\`\`\`
```

- [ ] **Step 2: Verify the change**

Run: `grep -n "pip install shopify-atc" README.md`
Expected: one match in the Installation section.

- [ ] **Step 3: Commit**

```bash
git add README.md
git commit -m "docs: lead README install with pip install shopify-atc"
```

---

### Task 5: Add the publish workflow

**Files:**
- Create: `.github/workflows/publish.yml`

- [ ] **Step 1: Write the workflow**

Create `.github/workflows/publish.yml` with exactly this content:

```yaml
name: Publish

# Publishes to PyPI via trusted publishing (OIDC) — no API tokens stored.
# - GitHub release  -> production PyPI
# - Manual dispatch -> TestPyPI (dry run)

on:
  release:
    types: [published]
  workflow_dispatch:

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - run: pip install build
      - run: python -m build
      - uses: actions/upload-artifact@v4
        with:
          name: dist
          path: dist/

  testpypi:
    needs: build
    if: github.event_name == 'workflow_dispatch'
    runs-on: ubuntu-latest
    environment: testpypi
    permissions:
      id-token: write
    steps:
      - uses: actions/download-artifact@v4
        with:
          name: dist
          path: dist/
      - uses: pypa/gh-action-pypi-publish@release/v1
        with:
          repository-url: https://test.pypi.org/legacy/

  pypi:
    needs: build
    if: github.event_name == 'release'
    runs-on: ubuntu-latest
    environment: pypi
    permissions:
      id-token: write
      contents: write
    steps:
      - uses: actions/download-artifact@v4
        with:
          name: dist
          path: dist/
      - uses: pypa/gh-action-pypi-publish@release/v1
      - name: Attach distributions to the GitHub release
        uses: softprops/action-gh-release@v2
        with:
          files: dist/*
```

- [ ] **Step 2: Verify the YAML parses**

Run: `python -c "import yaml; yaml.safe_load(open('.github/workflows/publish.yml')); print('ok')"`
Expected: `ok` (if PyYAML missing, `pip install pyyaml` first, or skip — the parse is a convenience check).

- [ ] **Step 3: Commit**

```bash
git add .github/workflows/publish.yml
git commit -m "ci: add PyPI publish workflow (OIDC trusted publishing + TestPyPI dispatch)"
```

---

### Task 6: Document the release process

**Files:**
- Create: `RELEASING.md`

- [ ] **Step 1: Write RELEASING.md**

Create `RELEASING.md` with this content:

```markdown
# Releasing shopify-atc

Releases are published to PyPI automatically by `.github/workflows/publish.yml`
using **trusted publishing (OIDC)** — no API tokens are stored anywhere.

## One-time setup (maintainer, web UI)

1. **PyPI trusted publisher** — on <https://pypi.org/manage/account/publishing/>,
   add a *pending publisher*:
   - PyPI Project Name: `shopify-atc`
   - Owner: `Technical-1`
   - Repository name: `Shopify-ATC`
   - Workflow name: `publish.yml`
   - Environment name: `pypi`
2. **TestPyPI trusted publisher** — repeat on
   <https://test.pypi.org/manage/account/publishing/> with Environment name
   `testpypi`.
3. **GitHub Environments** — in repo *Settings → Environments*, create two
   environments named `pypi` and `testpypi` so the OIDC subject matches.

## Dry run (TestPyPI)

Before the first real release, verify end-to-end:

1. GitHub → *Actions* → *Publish* → *Run workflow* (manual dispatch).
2. Confirms build + OIDC + upload to TestPyPI.
3. Optionally install from TestPyPI to smoke-test:
   `pip install --index-url https://test.pypi.org/simple/ shopify-atc`

## Cutting a release (production PyPI)

1. Bump the version in `shopify_atc/__init__.py` (`__version__`).
2. Commit: `git commit -am "release: vX.Y.Z"` and push.
3. Create a GitHub release with tag `vX.Y.Z` matching that version.
4. The `pypi` job builds, publishes to PyPI, and attaches the wheel + sdist to
   the release.

**Note:** PyPI rejects re-uploading an existing version. The git tag and
`__version__` must match and must be new each release.
```

- [ ] **Step 2: Verify it exists**

Run: `head -1 RELEASING.md`
Expected: `# Releasing shopify-atc`

- [ ] **Step 3: Commit**

```bash
git add RELEASING.md
git commit -m "docs: add RELEASING guide (trusted-publisher setup + release steps)"
```

---

## Post-implementation (maintainer action — not automatable)

These require Jacob's PyPI/GitHub web login and are intentionally outside the code changes:

1. Complete the trusted-publisher setup in `RELEASING.md` (PyPI + TestPyPI + GitHub Environments).
2. Run the TestPyPI dry run via manual workflow dispatch.
3. Cut the `v1.0.0` GitHub release to publish to production PyPI.

---

## Acceptance Criteria (from spec)

1. ✅ `pyproject.toml` includes keywords, classifiers, project URLs; builds cleanly (Task 2 + Task 3).
2. ✅ Root `LICENSE` file exists; PyPI/GitHub detect MIT (Task 1).
3. ✅ `.github/workflows/publish.yml` exists with three OIDC jobs; CI unaffected (Task 5).
4. ✅ README leads with `pip install shopify-atc` (Task 4).
5. ✅ Manual trusted-publisher setup documented (Task 6).
```
