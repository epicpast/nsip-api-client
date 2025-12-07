"""MCP Prompts for NSIP breeding decisions.

This module provides prompt templates that guide users through breeding
decisions and flock management tasks. Prompts are divided into:

1. Skill Prompts (skill_prompts.py):
   - 10 prompts matching existing slash commands
   - Single-shot execution with direct results

2. Shepherd Prompts (shepherd_prompts.py):
   - Guided consultation prompts for complex decisions
   - Uses LLM sampling for contextualized advice

3. Interview Prompts (interview_prompts.py):
   - Multi-turn guided interviews for complex workflows
   - Uses ctx.sample() for progressive data gathering
"""

# Import prompt modules to register them with the MCP server
# These are imported after server.py imports this module
from nsip_mcp.prompts import interview_prompts  # noqa: F401
from nsip_mcp.prompts import shepherd_prompts  # noqa: F401
from nsip_mcp.prompts import skill_prompts  # noqa: F401

__all__ = [
    "skill_prompts",
    "shepherd_prompts",
    "interview_prompts",
]
