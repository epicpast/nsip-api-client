"""Test slash command definitions.

Validates that all required slash commands exist in .claude-plugin/commands/
and have the correct structure with required sections.
"""

import re
from pathlib import Path

import pytest

# Path constants
PROJECT_ROOT = Path(__file__).parent.parent.parent
COMMANDS_DIR = PROJECT_ROOT / ".claude-plugin" / "commands"


# Required commands (US2 + US3 + US4 = 9 commands, exceeds FR-007 minimum of 5)
REQUIRED_COMMANDS = [
    "discover.md",
    "lookup.md",
    "profile.md",
    "health.md",
    "test-api.md",  # US3
    "search.md",  # US4
    "traits.md",  # US4
    "lineage.md",  # US4
    "progeny.md",  # US4
]


def test_commands_directory_exists():
    """Verify commands directory exists."""
    assert COMMANDS_DIR.exists(), f"commands directory not found at {COMMANDS_DIR}"
    assert COMMANDS_DIR.is_dir(), f"{COMMANDS_DIR} is not a directory"


@pytest.mark.parametrize("command_file", REQUIRED_COMMANDS)
def test_command_file_exists(command_file):
    """Verify required command files exist."""
    command_path = COMMANDS_DIR / command_file
    assert command_path.exists(), f"Command file {command_file} not found at {command_path}"


@pytest.mark.parametrize("command_file", REQUIRED_COMMANDS)
def test_command_file_has_heading(command_file):
    """Verify command file has proper heading format: # /nsip/[command] - [Description]"""
    command_path = COMMANDS_DIR / command_file
    with open(command_path) as f:
        content = f.read()

    # Extract command name from filename
    command_name = command_file.replace(".md", "")

    # Check for heading pattern
    heading_pattern = rf"^#\s+/nsip/{command_name}\s+-\s+.+"
    assert re.search(
        heading_pattern, content, re.MULTILINE
    ), f"Command file {command_file} missing heading: # /nsip/{command_name} - [Description]"


@pytest.mark.parametrize("command_file", REQUIRED_COMMANDS)
def test_command_file_has_instructions(command_file):
    """Verify command file has Instructions section."""
    command_path = COMMANDS_DIR / command_file
    with open(command_path) as f:
        content = f.read()

    assert (
        "## Instructions" in content
    ), f"Command file {command_file} missing '## Instructions' section"


@pytest.mark.parametrize("command_file", REQUIRED_COMMANDS)
def test_command_file_has_error_handling(command_file):
    """Verify command file has Error Handling section."""
    command_path = COMMANDS_DIR / command_file
    with open(command_path) as f:
        content = f.read()

    assert (
        "## Error Handling" in content
    ), f"Command file {command_file} missing '## Error Handling' section"


def test_minimum_commands_count():
    """Verify at least 9 commands exist (exceeds FR-007 minimum of 5)."""
    if not COMMANDS_DIR.exists():
        pytest.skip("Commands directory does not exist")

    command_files = list(COMMANDS_DIR.glob("*.md"))
    assert len(command_files) >= 9, f"Expected at least 9 command files, found {len(command_files)}"


def test_command_file_names():
    """Verify command file names follow pattern: [a-z0-9-]+.md"""
    if not COMMANDS_DIR.exists():
        pytest.skip("Commands directory does not exist")

    command_files = list(COMMANDS_DIR.glob("*.md"))
    pattern = re.compile(r"^[a-z0-9-]+\.md$")

    for command_file in command_files:
        assert pattern.match(
            command_file.name
        ), f"Command file {command_file.name} does not follow naming pattern [a-z0-9-]+.md"
