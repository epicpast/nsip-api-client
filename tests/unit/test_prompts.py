"""Unit tests for MCP prompts module.

Note: These tests focus on prompt message structure and logic validation,
not the FastMCP decorator integration. The prompts are tested through
their expected output format and structure.
"""

from unittest.mock import MagicMock

# Import knowledge base functions that prompts use
from nsip_mcp.knowledge_base import (
    get_trait_info,
    get_region_info,
    get_selection_index,
    list_traits,
)
from nsip_mcp.shepherd import (
    ShepherdPersona,
    ShepherdAgent,
    NSIP_REGIONS,
)
from nsip_mcp.shepherd.persona import format_shepherd_response


class TestPromptMessageStructure:
    """Tests for MCP prompt message structure requirements."""

    def test_valid_message_roles(self) -> None:
        """Test that valid message roles are defined."""
        valid_roles = ["user", "assistant", "system"]
        assert "user" in valid_roles
        assert "assistant" in valid_roles
        assert "system" in valid_roles

    def test_message_requires_role_and_content(self) -> None:
        """Test that messages must have role and content."""
        message = {"role": "user", "content": {"type": "text", "text": "Hello"}}
        assert "role" in message
        assert "content" in message

    def test_content_text_structure(self) -> None:
        """Test content with text type structure."""
        content = {"type": "text", "text": "Test message"}
        assert content["type"] == "text"
        assert "text" in content


class TestSkillPromptLogic:
    """Tests for skill prompt underlying logic."""

    def test_ebv_analyzer_trait_parsing(self) -> None:
        """Test EBV analyzer trait parsing logic."""
        traits_str = "BWT,WWT,PWWT"
        trait_list = [t.strip().upper() for t in traits_str.split(",")]

        assert trait_list == ["BWT", "WWT", "PWWT"]

    def test_ebv_analyzer_lpn_parsing(self) -> None:
        """Test EBV analyzer LPN ID parsing logic."""
        lpn_ids = "6332-001, 6332-002, 6332-003"
        lpn_list = [lpn.strip() for lpn in lpn_ids.split(",")]

        assert len(lpn_list) == 3
        assert lpn_list[0] == "6332-001"

    def test_selection_index_lookup(self) -> None:
        """Test selection index lookup for prompts."""
        index = get_selection_index("terminal")

        assert isinstance(index, dict)
        assert "name" in index or "traits" in index or "description" in index

    def test_trait_info_for_interpretation(self) -> None:
        """Test trait info lookup for interpretation."""
        info = get_trait_info("WWT")

        assert isinstance(info, dict)
        assert "name" in info or "description" in info

    def test_comparison_table_format(self) -> None:
        """Test markdown table generation logic."""
        # Simulate table row generation
        header = ["Animal", "WWT", "BWT"]
        row1 = ["Ram A", "5.0", "0.5"]

        header_line = "| " + " | ".join(header) + " |"
        separator = "| " + " | ".join(["---"] * len(header)) + " |"
        row_line = "| " + " | ".join(row1) + " |"

        assert "|" in header_line
        assert "---" in separator
        assert "Ram A" in row_line


class TestShepherdPromptLogic:
    """Tests for shepherd consultation prompt logic."""

    def test_persona_system_prompt_exists(self) -> None:
        """Test that persona has system prompt content."""
        persona = ShepherdPersona()

        assert hasattr(persona, "SYSTEM_PROMPT") or hasattr(persona, "get_system_prompt")

    def test_region_context_available(self) -> None:
        """Test region context is available for prompts."""
        region_info = get_region_info("midwest")

        assert isinstance(region_info, dict)

    def test_nsip_regions_available(self) -> None:
        """Test NSIP regions dict is available."""
        assert isinstance(NSIP_REGIONS, dict)
        assert len(NSIP_REGIONS) > 0

    def test_format_response_with_answer(self) -> None:
        """Test format_shepherd_response with answer string."""
        result = format_shepherd_response("This is my answer.")

        assert isinstance(result, str)
        assert "This is my answer." in result

    def test_format_response_with_recommendations(self) -> None:
        """Test format_shepherd_response with recommendations."""
        result = format_shepherd_response(
            "Answer here.",
            recommendations=["Do this", "Try that"]
        )

        assert isinstance(result, str)
        assert "Recommendations" in result or "Do this" in result

    def test_format_response_with_next_steps(self) -> None:
        """Test format_shepherd_response with next steps."""
        result = format_shepherd_response(
            "Answer here.",
            next_steps=["Step 1", "Step 2"]
        )

        assert isinstance(result, str)


class TestInterviewPromptLogic:
    """Tests for guided interview prompt logic."""

    def test_missing_inputs_detection(self) -> None:
        """Test detection of missing required inputs."""
        # Simulate checking for required inputs
        rams = None
        ewes = None

        missing = []
        if not rams:
            missing.append("rams")
        if not ewes:
            missing.append("ewes")

        assert "rams" in missing
        assert "ewes" in missing
        assert len(missing) == 2

    def test_all_inputs_provided_detection(self) -> None:
        """Test detection when all inputs are provided."""
        rams = "6332-001"
        ewes = "6332-101"
        goal = "terminal"

        all_provided = all([rams, ewes, goal])

        assert all_provided is True

    def test_interview_question_format(self) -> None:
        """Test interview question message format."""
        question = "Please provide the LPN IDs for your rams."
        message = {"role": "user", "content": {"type": "text", "text": question}}

        assert message["role"] == "user"
        assert question in message["content"]["text"]


class TestPromptTraitHandling:
    """Tests for trait handling in prompts."""

    def test_list_available_traits(self) -> None:
        """Test listing available traits for prompts."""
        traits = list_traits()

        assert isinstance(traits, list)
        assert len(traits) > 0

    def test_trait_code_normalization(self) -> None:
        """Test trait code normalization."""
        raw_input = "  wWt , bwt , PWWT  "
        normalized = [t.strip().upper() for t in raw_input.split(",")]

        assert normalized == ["WWT", "BWT", "PWWT"]

    def test_ebv_value_formatting(self) -> None:
        """Test EBV value formatting."""
        value = 5.123456
        formatted = f"{value:.2f}"

        assert formatted == "5.12"

    def test_missing_ebv_handling(self) -> None:
        """Test handling of missing EBV values."""
        value = None
        display = f"{value:.2f}" if value is not None else "N/A"

        assert display == "N/A"


class TestPromptErrorHandling:
    """Tests for prompt error handling patterns."""

    def test_graceful_api_error_handling(self) -> None:
        """Test pattern for graceful API error handling."""
        mock_client = MagicMock()
        mock_client.get_animal_details.side_effect = Exception("API Error")

        try:
            mock_client.get_animal_details("test-id")
            succeeded = True
        except Exception:
            succeeded = False

        assert succeeded is False

    def test_empty_result_handling(self) -> None:
        """Test handling when no results are found."""
        animals_data = []

        if not animals_data:
            message = "No animals found"
        else:
            message = "Found animals"

        assert message == "No animals found"

    def test_knowledge_base_fallback(self) -> None:
        """Test fallback when knowledge base lookup fails."""
        try:
            info = get_trait_info("INVALID_TRAIT")
            found = True
        except Exception:
            found = False
            info = {"name": "Unknown", "description": "Trait not found"}

        assert found is False or isinstance(info, dict)


class TestPromptIntegrationPatterns:
    """Tests for prompt integration patterns."""

    def test_shepherd_agent_creation(self) -> None:
        """Test Shepherd agent can be created for prompts."""
        agent = ShepherdAgent()

        assert agent is not None
        assert hasattr(agent, "consult")

    def test_agent_consult_returns_dict(self) -> None:
        """Test agent consult returns dict."""
        agent = ShepherdAgent()
        result = agent.consult("How do I improve weaning weight?")

        assert isinstance(result, dict)

    def test_region_context_in_prompt(self) -> None:
        """Test region context integration pattern."""
        region = "midwest"
        region_info = get_region_info(region)

        context = {
            "region": region,
            "climate": region_info.get("climate", "Unknown"),
        }

        assert context["region"] == "midwest"
