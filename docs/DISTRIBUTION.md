# Distribution Policy

## Important: No PyPI Publishing

**This project is NOT published to PyPI and will NOT be available via `pip install nsip-client`.**

### Why Not PyPI?

This is a reverse-engineered API client for a third-party service (NSIP Search). To respect the service and avoid potential issues:

1. We distribute exclusively through GitHub Releases
2. Users must explicitly choose to install from GitHub
3. This ensures users are aware they're using an unofficial client
4. Gives the NSIP organization control to request takedown if needed

### Distribution Method

**GitHub Releases Only**

- ✅ Source distribution (`.tar.gz`)
- ✅ Wheel distribution (`.whl`)
- ✅ Attached to GitHub Releases
- ✅ Installable via pip from GitHub URLs
- ❌ NOT on PyPI
- ❌ NOT on Test PyPI

## Installation Methods

Users can install the package in several ways:

### 1. From GitHub Release (Recommended)

```bash
# Latest wheel
pip install https://github.com/epicpast/nsip-api-client/releases/latest/download/nsip_client-1.0.0-py3-none-any.whl

# Specific version
pip install https://github.com/epicpast/nsip-api-client/releases/download/v1.0.0/nsip-client-1.0.0.tar.gz
```

### 2. From Git Tag

```bash
# Specific version
pip install git+https://github.com/epicpast/nsip-api-client.git@v1.0.0

# Latest from main
pip install git+https://github.com/epicpast/nsip-api-client.git
```

### 3. From Source

```bash
git clone https://github.com/epicpast/nsip-api-client.git
cd nsip-api-client
pip install -e .
```

## Package Validation

We still use standard Python packaging tools to ensure quality:

- ✅ `python -m build` - Build wheel and source distributions
- ✅ `twine check dist/*` - Validate package metadata
- ❌ `twine upload` - **NEVER USED** - Publishing is disabled

### Why We Use Twine Check

`twine check` validates that:
- Package metadata is correct
- README renders properly
- No syntax errors in package files
- Compatible with PyPI standards (even though we don't publish)

**Important:** `twine check` does NOT upload anything. It only validates local files.

## CI/CD Pipeline

Our GitHub Actions workflows:

1. **Tests** - Run on all Python versions
2. **Quality** - Format, lint, type check
3. **Build** - Create wheel and source distributions
4. **Validate** - Run `twine check` to ensure package is well-formed
5. **Release** - Create GitHub Release with distribution files
6. **❌ NO PyPI Upload** - This step is intentionally omitted

## For Maintainers

### Creating a Release

```bash
# Tag a version
git tag -a v1.0.0 -m "Release 1.0.0"
git push origin v1.0.0
```

The GitHub Actions workflow will:
- Run all tests
- Validate code quality
- Build packages
- Create GitHub Release
- Attach `.whl` and `.tar.gz` files

### Manual Release via GitHub UI

1. Go to Actions → Manual Release
2. Enter version number
3. Workflow handles everything

### What Gets Published

- ✅ GitHub Release created
- ✅ Distribution files attached to release
- ✅ Release notes from CHANGELOG
- ✅ Artifacts stored for 90 days
- ❌ Nothing sent to PyPI

## Future Considerations

If NSIP creates an official API or grants permission, we may:
- Publish to PyPI with their blessing
- Use a different package name (e.g., `nsip-search-client`)
- Add official attribution and partnership

Until then: **GitHub Releases Only**.

## For Users

### Finding Releases

Visit: https://github.com/epicpast/nsip-api-client/releases

### Trusting the Source

- All releases are built by GitHub Actions
- Full source code available for review
- Signed commits from maintainers
- Transparent build process

### Support

This is an unofficial, community-maintained client. For official NSIP support, contact NSIP directly at http://nsipsearch.nsip.org
