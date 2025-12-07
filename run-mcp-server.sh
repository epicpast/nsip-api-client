#!/bin/bash
cd /Users/AllenR1_1/Projects/nsip-mcp-extend
exec /opt/homebrew/bin/uv run python -c "from nsip_mcp.cli import main; main()"
