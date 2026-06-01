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
