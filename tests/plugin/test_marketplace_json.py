"""Test marketplace.json configuration file.

Validates that .claude-plugin/marketplace.json conforms to the marketplace schema
and contains required fields for plugin discovery.
"""

import json
from pathlib import Path

import jsonschema

# Path constants
PROJECT_ROOT = Path(__file__).parent.parent.parent
MARKETPLACE_JSON = PROJECT_ROOT / ".claude-plugin" / "marketplace.json"
MARKETPLACE_SCHEMA = Path(__file__).parent / "marketplace-schema.json"


def test_marketplace_json_exists():
    """Verify marketplace.json exists."""
    assert MARKETPLACE_JSON.exists(), f"marketplace.json not found at {MARKETPLACE_JSON}"


def test_marketplace_json_valid_json():
    """Verify marketplace.json is valid JSON."""
    with open(MARKETPLACE_JSON) as f:
        data = json.load(f)
    assert isinstance(data, dict), "marketplace.json must be a JSON object"


def test_marketplace_json_schema_compliance():
    """Validate marketplace.json against schema."""
    with open(MARKETPLACE_JSON) as f:
        marketplace_data = json.load(f)

    with open(MARKETPLACE_SCHEMA) as f:
        schema = json.load(f)

    # Validate against schema
    jsonschema.validate(instance=marketplace_data, schema=schema)


def test_marketplace_json_required_fields():
    """Verify all required fields are present."""
    with open(MARKETPLACE_JSON) as f:
        data = json.load(f)

    # Top-level required fields
    assert "name" in data, "Missing required field: name"
    assert "version" in data, "Missing required field: version"
    assert "description" in data, "Missing required field: description"
    assert "owner" in data, "Missing required field: owner"
    assert "plugins" in data, "Missing required field: plugins"


def test_marketplace_json_plugin_name():
    """Verify plugin name matches expected value."""
    with open(MARKETPLACE_JSON) as f:
        data = json.load(f)

    assert (
        data["name"] == "nsip-api-client"
    ), f"Expected name 'nsip-api-client', got '{data['name']}'"


def test_marketplace_json_version_format():
    """Verify version follows semver format."""
    with open(MARKETPLACE_JSON) as f:
        data = json.load(f)

    version = data["version"]
    parts = version.split(".")
    assert len(parts) == 3, f"Version must be semver format (X.Y.Z), got '{version}'"
    assert all(part.isdigit() for part in parts), f"Version parts must be numeric, got '{version}'"


def test_marketplace_json_plugins_array():
    """Verify plugins array contains at least one plugin."""
    with open(MARKETPLACE_JSON) as f:
        data = json.load(f)

    plugins = data["plugins"]
    assert isinstance(plugins, list), "plugins must be an array"
    assert len(plugins) >= 1, "plugins array must contain at least one plugin"


def test_marketplace_json_plugin_metadata():
    """Verify first plugin has required metadata."""
    with open(MARKETPLACE_JSON) as f:
        data = json.load(f)

    plugin = data["plugins"][0]

    # Required plugin fields
    assert "name" in plugin, "Plugin missing required field: name"
    assert "description" in plugin, "Plugin missing required field: description"
    assert "version" in plugin, "Plugin missing required field: version"
    assert "author" in plugin, "Plugin missing required field: author"
    assert "source" in plugin, "Plugin missing required field: source"

    # Verify plugin name matches marketplace name
    assert (
        plugin["name"] == "nsip-api-client"
    ), f"Plugin name must match marketplace name, got '{plugin['name']}'"


def test_marketplace_json_plugin_description():
    """Verify plugin description meets minimum length requirement."""
    with open(MARKETPLACE_JSON) as f:
        data = json.load(f)

    plugin = data["plugins"][0]
    description = plugin["description"]

    assert (
        len(description) >= 10
    ), f"Plugin description must be at least 10 characters, got {len(description)}"
    assert (
        len(description) <= 500
    ), f"Plugin description must be at most 500 characters, got {len(description)}"


def test_marketplace_json_plugin_category():
    """Verify plugin category is valid."""
    with open(MARKETPLACE_JSON) as f:
        data = json.load(f)

    plugin = data["plugins"][0]

    if "category" in plugin:
        valid_categories = ["development", "data-access", "productivity", "security", "other"]
        assert (
            plugin["category"] in valid_categories
        ), f"Plugin category must be one of {valid_categories}, got '{plugin['category']}'"
