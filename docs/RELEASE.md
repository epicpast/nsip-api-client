# Release Process

This document describes how to create a new release of the NSIP API Client.

## Automated Release Workflow

Releases are automated via GitHub Actions. When you push a version tag, the workflow will:

1. ✅ Run all tests on Python 3.10, 3.11, 3.12, 3.13
2. ✅ Run quality checks (black, isort, flake8, mypy)
3. 📦 Build distribution packages (wheel and source)
4. ✅ Validate package with twine
5. 🚀 Create GitHub Release with release notes
6. 📎 Attach distribution files to the release

**Note:** Packages are NOT published to PyPI - they are only available as GitHub Release assets.

## Creating a New Release

### 1. Update Version and Changelog

Edit the version in `pyproject.toml`:

```toml
[project]
name = "nsip-client"
version = "1.1.0"  # Update this
```

Update `CHANGELOG.md` with changes for the new version:

```markdown
## [1.1.0] - 2025-10-15

### Added
- New feature X
- Support for Y

### Fixed
- Bug with Z

### Changed
- Improved performance of A
```

Update `src/nsip_client/__init__.py`:

```python
__version__ = "1.1.0"  # Update this
```

### 2. Commit Changes

```bash
git add pyproject.toml CHANGELOG.md src/nsip_client/__init__.py
git commit -m "Bump version to 1.1.0"
git push origin main
```

### 3. Create and Push Tag

```bash
# Create annotated tag
git tag -a v1.1.0 -m "Release version 1.1.0"

# Push tag to trigger release workflow
git push origin v1.1.0
```

### 4. Monitor Release

1. Go to https://github.com/epicpast/nsip-api-client/actions
2. Watch the "Release" workflow run
3. Verify all checks pass
4. Check that the release is created at https://github.com/epicpast/nsip-api-client/releases

### 5. Verify Release Assets

The release should include:
- `nsip-client-1.1.0.tar.gz` (source distribution)
- `nsip_client-1.1.0-py3-none-any.whl` (wheel distribution)
- Automatically generated release notes
- Changelog excerpt for this version

## Installing from GitHub Release

Users can install directly from the release:

```bash
# Install from latest release
pip install https://github.com/epicpast/nsip-api-client/releases/latest/download/nsip_client-1.1.0-py3-none-any.whl

# Or from source distribution
pip install https://github.com/epicpast/nsip-api-client/releases/download/v1.1.0/nsip-client-1.1.0.tar.gz
```

Or from Git tag:

```bash
pip install git+https://github.com/epicpast/nsip-api-client.git@v1.1.0
```

## Pre-release Versions

For beta or release candidate versions:

```bash
# Update version to 1.1.0rc1
git tag -a v1.1.0rc1 -m "Release candidate 1.1.0rc1"
git push origin v1.1.0rc1
```

The workflow will mark it as a pre-release automatically if the tag contains `rc`, `alpha`, `beta`, etc.

## Rolling Back a Release

If you need to delete a release:

```bash
# Delete the tag locally
git tag -d v1.1.0

# Delete the tag remotely
git push origin :refs/tags/v1.1.0

# Manually delete the GitHub Release from the web UI
```

## Troubleshooting

### Workflow Failed

If the release workflow fails:

1. Check the Actions tab for error details
2. Fix the issue
3. Delete the tag: `git push origin :refs/tags/v1.1.0`
4. Recreate and push the tag after fixing

### Missing Release Notes

If changelog extraction fails, the workflow will use auto-generated notes from commits.

To fix:
1. Ensure CHANGELOG.md has proper formatting
2. Section headers should match: `## [version]`

### Tests Failing

The release will NOT be created if tests fail. Fix tests first:

```bash
make test
make quality
```

Then recreate the tag.

## Versioning

We follow [Semantic Versioning](https://semver.org/):

- **MAJOR** version (1.x.x): Incompatible API changes
- **MINOR** version (x.1.x): New functionality, backward compatible
- **PATCH** version (x.x.1): Backward compatible bug fixes

Examples:
- `1.0.0` → `1.0.1`: Bug fix
- `1.0.1` → `1.1.0`: New feature
- `1.1.0` → `2.0.0`: Breaking change

## Release Checklist

Before creating a release:

- [ ] All tests pass locally (`make test`)
- [ ] All quality checks pass (`make quality`)
- [ ] Version updated in `pyproject.toml`
- [ ] Version updated in `src/nsip_client/__init__.py`
- [ ] CHANGELOG.md updated with changes
- [ ] Documentation updated if needed
- [ ] Examples tested with new version
- [ ] README.md reviewed for accuracy
- [ ] All PRs merged to main
- [ ] No known critical bugs

## Post-Release

After release:

1. Announce the release (if applicable)
2. Update documentation site (if exists)
3. Close milestone (if using)
4. Create next milestone for future version
