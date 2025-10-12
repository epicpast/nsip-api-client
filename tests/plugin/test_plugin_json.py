"""Test plugin.json configuration file.

Validates that .claude-plugin/plugin.json conforms to the plugin schema
and contains correct MCP server configuration.
"""

import json
from pathlib import Path

import jsonschema

# Path constants
PROJECT_ROOT = Path(__file__).parent.parent.parent
PLUGIN_JSON = PROJECT_ROOT / ".claude-plugin" / "plugin.json"
PLUGIN_SCHEMA = Path(__file__).parent / "plugin-schema.json"


def test_plugin_json_exists():
    """Verify plugin.json exists."""
    assert PLUGIN_JSON.exists(), f"plugin.json not found at {PLUGIN_JSON}"


def test_plugin_json_valid_json():
    """Verify plugin.json is valid JSON."""
    with open(PLUGIN_JSON) as f:
        data = json.load(f)
    assert isinstance(data, dict), "plugin.json must be a JSON object"


def test_plugin_json_schema_compliance():
    """Validate plugin.json against schema."""
    with open(PLUGIN_JSON) as f:
        plugin_data = json.load(f)

    with open(PLUGIN_SCHEMA) as f:
        schema = json.load(f)

    # Validate against schema
    jsonschema.validate(instance=plugin_data, schema=schema)


def test_plugin_json_name():
    """Verify plugin name is present and correct."""
    with open(PLUGIN_JSON) as f:
        data = json.load(f)

    assert "name" in data, "Missing required field: name"
    assert (
        data["name"] == "nsip-api-client"
    ), f"Expected name 'nsip-api-client', got '{data['name']}'"


def test_plugin_json_mcp_servers():
    """Verify mcpServers configuration exists."""
    with open(PLUGIN_JSON) as f:
        data = json.load(f)

    assert "mcpServers" in data, "Missing mcpServers configuration"
    assert isinstance(data["mcpServers"], dict), "mcpServers must be an object"


def test_plugin_json_mcp_server_config():
    """Verify MCP server configuration has required fields."""
    with open(PLUGIN_JSON) as f:
        data = json.load(f)

    mcp_servers = data["mcpServers"]
    assert "nsip-api-client" in mcp_servers, "Missing 'nsip-api-client' MCP server configuration"

    server_config = mcp_servers["nsip-api-client"]
    assert "command" in server_config, "MCP server config missing required field: command"


def test_plugin_json_command_uses_plugin_root():
    """Verify command uses ${CLAUDE_PLUGIN_ROOT} variable."""
    with open(PLUGIN_JSON) as f:
        data = json.load(f)

    server_config = data["mcpServers"]["nsip-api-client"]
    command = server_config["command"]

    assert "${CLAUDE_PLUGIN_ROOT}" in command, (
        f"Command must use ${{CLAUDE_PLUGIN_ROOT}} variable "
        f"for plugin-relative path, got '{command}'"
    )


def test_plugin_json_args_array():
    """Verify args array contains correct module invocation."""
    with open(PLUGIN_JSON) as f:
        data = json.load(f)

    server_config = data["mcpServers"]["nsip-api-client"]
    assert "args" in server_config, "MCP server config missing args"

    args = server_config["args"]
    assert isinstance(args, list), "args must be an array"
    assert "-m" in args, "args must contain '-m' flag for module invocation"
    assert "nsip_mcp.server" in args, "args must contain 'nsip_mcp.server' module"


def test_plugin_json_env_variables():
    """Verify environment variables are defined."""
    with open(PLUGIN_JSON) as f:
        data = json.load(f)

    server_config = data["mcpServers"]["nsip-api-client"]
    assert "env" in server_config, "MCP server config missing env"

    env = server_config["env"]
    assert isinstance(env, dict), "env must be an object"
    assert "NSIP_BASE_URL" in env, "env missing NSIP_BASE_URL variable"
    # Note: NSIP API is public and requires no authentication


def test_plugin_json_env_variable_expansion():
    """Verify environment variables use expansion syntax."""
    with open(PLUGIN_JSON) as f:
        data = json.load(f)

    server_config = data["mcpServers"]["nsip-api-client"]
    env = server_config["env"]

    # Check NSIP_BASE_URL uses expansion
    base_url = env["NSIP_BASE_URL"]
    assert base_url.startswith("${") and base_url.endswith(
        "}"
    ), f"NSIP_BASE_URL must use variable expansion syntax ${{VAR}}, got '{base_url}'"
    # Note: Only NSIP_BASE_URL needed (API is public, no authentication required)
