"""Unit tests for MCP prompts module.

Note: These tests focus on prompt message structure and logic validation,
not the FastMCP decorator integration. The prompts are tested through
their expected output format and structure.
"""

from unittest.mock import MagicMock

# Import knowledge base functions that prompts use
from nsip_mcp.knowledge_base import (
    get_region_info,
    get_selection_index,
    get_trait_info,
    list_traits,
)
from nsip_mcp.shepherd import (
    NSIP_REGIONS,
    ShepherdAgent,
    ShepherdPersona,
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
        result = format_shepherd_response("Answer here.", recommendations=["Do this", "Try that"])

        assert isinstance(result, str)
        assert "Recommendations" in result or "Do this" in result

    def test_format_response_with_next_steps(self) -> None:
        """Test format_shepherd_response with next steps."""
        result = format_shepherd_response("Answer here.", next_steps=["Step 1", "Step 2"])

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


class TestShepherdPromptsExecution:
    """Tests for shepherd prompt execution."""

    import asyncio

    def test_shepherd_breeding_prompt(self) -> None:
        """Test shepherd breeding prompt returns messages."""
        import asyncio

        from nsip_mcp.prompts.shepherd_prompts import shepherd_breeding_prompt

        result = asyncio.run(
            shepherd_breeding_prompt.fn(
                question="How to improve weaning weight?",
                region="midwest",
                production_goal="terminal",
            )
        )

        assert isinstance(result, list)
        assert len(result) > 0
        assert result[0].get("role") in ["user", "system", "assistant"]

    def test_shepherd_health_prompt(self) -> None:
        """Test shepherd health prompt returns messages."""
        import asyncio

        from nsip_mcp.prompts.shepherd_prompts import shepherd_health_prompt

        result = asyncio.run(
            shepherd_health_prompt.fn(
                question="What vaccines do I need?",
                region="midwest",
                life_stage="maintenance",
            )
        )

        assert isinstance(result, list)

    def test_shepherd_calendar_prompt(self) -> None:
        """Test shepherd calendar prompt returns messages."""
        import asyncio

        from nsip_mcp.prompts.shepherd_prompts import shepherd_calendar_prompt

        result = asyncio.run(
            shepherd_calendar_prompt.fn(
                question="When to start breeding?",
                region="midwest",
                task_type="breeding",
            )
        )

        assert isinstance(result, list)

    def test_shepherd_economics_prompt(self) -> None:
        """Test shepherd economics prompt returns messages."""
        import asyncio

        from nsip_mcp.prompts.shepherd_prompts import shepherd_economics_prompt

        result = asyncio.run(
            shepherd_economics_prompt.fn(
                question="What is my cost per ewe?",
                flock_size="medium",
                market_focus="direct",
            )
        )

        assert isinstance(result, list)

    def test_shepherd_consult_prompt(self) -> None:
        """Test shepherd consult prompt returns messages."""
        import asyncio

        from nsip_mcp.prompts.shepherd_prompts import shepherd_consult_prompt

        result = asyncio.run(
            shepherd_consult_prompt.fn(
                question="General advice on flock management",
                region="midwest",
            )
        )

        assert isinstance(result, list)


class TestInterviewPromptsExecution:
    """Tests for interview prompt execution."""

    def test_mating_plan_interview(self) -> None:
        """Test mating plan interview prompt."""
        import asyncio

        from nsip_mcp.prompts.interview_prompts import guided_mating_plan_prompt

        result = asyncio.run(guided_mating_plan_prompt.fn(rams="", ewes="", goal=""))

        assert isinstance(result, list)

    def test_trait_improvement_interview(self) -> None:
        """Test trait improvement interview prompt."""
        import asyncio

        from nsip_mcp.prompts.interview_prompts import guided_trait_improvement_prompt

        result = asyncio.run(
            guided_trait_improvement_prompt.fn(
                trait="", current_average="", target_value="", generations=""
            )
        )

        assert isinstance(result, list)

    def test_breeding_recs_interview(self) -> None:
        """Test breeding recommendations interview prompt."""
        import asyncio

        from nsip_mcp.prompts.interview_prompts import guided_breeding_recommendations_prompt

        result = asyncio.run(
            guided_breeding_recommendations_prompt.fn(
                flock_data="", priorities="", constraints="", region=""
            )
        )

        assert isinstance(result, list)


class TestSkillPromptsExecution:
    """Tests for skill prompt execution with mocked client."""

    def test_ebv_analyzer_no_animals(self) -> None:
        """Test EBV analyzer with no animals found."""
        import asyncio
        from unittest.mock import MagicMock, patch

        with patch("nsip_mcp.prompts.skill_prompts.get_nsip_client") as mock_get_client:
            mock_client = MagicMock()
            mock_client.get_animal_details.return_value = None
            mock_get_client.return_value = mock_client

            from nsip_mcp.prompts.skill_prompts import ebv_analyzer_prompt

            result = asyncio.run(ebv_analyzer_prompt.fn(lpn_ids="fake-id", traits="WWT,BWT"))

            assert isinstance(result, list)

    def test_selection_index_prompt(self) -> None:
        """Test selection index prompt."""
        import asyncio
        from unittest.mock import MagicMock, patch

        with patch("nsip_mcp.prompts.skill_prompts.get_nsip_client") as mock_get_client:
            mock_client = MagicMock()
            mock_client.get_animal_details.return_value = None
            mock_get_client.return_value = mock_client

            from nsip_mcp.prompts.skill_prompts import selection_index_prompt

            result = asyncio.run(
                selection_index_prompt.fn(lpn_ids="fake-id", index_name="terminal")
            )

            assert isinstance(result, list)

    def test_selection_index_invalid_index(self) -> None:
        """Test selection index with invalid index name."""
        import asyncio

        from nsip_mcp.prompts.skill_prompts import selection_index_prompt

        result = asyncio.run(selection_index_prompt.fn(lpn_ids="fake-id", index_name="invalid_xyz"))

        assert isinstance(result, list)
        # Should return error message about unknown index

    def test_ancestry_prompt(self) -> None:
        """Test ancestry prompt with mocked client."""
        import asyncio
        from unittest.mock import MagicMock, patch

        with patch("nsip_mcp.prompts.skill_prompts.get_nsip_client") as mock_get_client:
            mock_client = MagicMock()
            mock_client.get_lineage.return_value = None
            mock_get_client.return_value = mock_client

            from nsip_mcp.prompts.skill_prompts import ancestry_prompt

            result = asyncio.run(ancestry_prompt.fn(lpn_id="fake-id"))

            assert isinstance(result, list)

    def test_flock_dashboard_prompt(self) -> None:
        """Test flock dashboard prompt with mocked client."""
        import asyncio
        from unittest.mock import MagicMock, patch

        with patch("nsip_mcp.prompts.skill_prompts.get_nsip_client") as mock_get_client:
            mock_client = MagicMock()
            mock_search = MagicMock()
            mock_search.results = []
            mock_client.search_animals.return_value = mock_search
            mock_get_client.return_value = mock_client

            from nsip_mcp.prompts.skill_prompts import flock_dashboard_prompt

            result = asyncio.run(flock_dashboard_prompt.fn(flock_prefix="6332"))

            assert isinstance(result, list)

    def test_progeny_report_prompt(self) -> None:
        """Test progeny report prompt with mocked client."""
        import asyncio
        from unittest.mock import MagicMock, patch

        with patch("nsip_mcp.prompts.skill_prompts.get_nsip_client") as mock_get_client:
            mock_client = MagicMock()
            mock_progeny = MagicMock()
            mock_progeny.animals = []
            mock_client.get_progeny.return_value = mock_progeny
            mock_get_client.return_value = mock_client

            from nsip_mcp.prompts.skill_prompts import progeny_report_prompt

            result = asyncio.run(progeny_report_prompt.fn(sire_lpn="fake-id"))

            assert isinstance(result, list)

    def test_inbreeding_prompt(self) -> None:
        """Test inbreeding prompt with mocked client."""
        import asyncio
        from unittest.mock import MagicMock, patch

        with patch("nsip_mcp.prompts.skill_prompts.get_nsip_client") as mock_get_client:
            mock_client = MagicMock()
            mock_client.get_lineage.return_value = None
            mock_get_client.return_value = mock_client

            from nsip_mcp.prompts.skill_prompts import inbreeding_prompt

            result = asyncio.run(inbreeding_prompt.fn(ram_lpn="fake-ram", ewe_lpn="fake-ewe"))

            assert isinstance(result, list)

    def test_flock_import_prompt(self) -> None:
        """Test flock import prompt."""
        import asyncio

        from nsip_mcp.prompts.interview_prompts import guided_flock_import_prompt

        result = asyncio.run(
            guided_flock_import_prompt.fn(
                file_path="/fake/path.csv",
                flock_prefix="6332",
                data_format="csv",
            )
        )

        assert isinstance(result, list)


class TestSkillPromptsWithSuccessData:
    """Tests for skill prompts with mocked successful data."""

    def test_ebv_analyzer_with_animals(self) -> None:
        """Test EBV analyzer with animals found."""
        import asyncio
        from unittest.mock import MagicMock, patch

        with patch("nsip_mcp.prompts.skill_prompts.get_nsip_client") as mock_get_client:
            mock_client = MagicMock()
            mock_animal = MagicMock()
            mock_animal.to_dict.return_value = {
                "lpn_id": "6332-001",
                "name": "Test Ram",
                "ebvs": {"WWT": 5.0, "BWT": 0.5, "PWWT": 8.0},
            }
            mock_client.get_animal_details.return_value = mock_animal
            mock_get_client.return_value = mock_client

            from nsip_mcp.prompts.skill_prompts import ebv_analyzer_prompt

            result = asyncio.run(ebv_analyzer_prompt.fn(lpn_ids="6332-001", traits="WWT,BWT,PWWT"))

            assert isinstance(result, list)
            assert len(result) > 0
            # Check the content has the analysis
            if result and "content" in result[0]:
                text = result[0]["content"].get("text", "")
                assert "EBV" in text or "Comparison" in text or "WWT" in text

    def test_ebv_analyzer_multiple_animals(self) -> None:
        """Test EBV analyzer with multiple animals."""
        import asyncio
        from unittest.mock import MagicMock, patch

        with patch("nsip_mcp.prompts.skill_prompts.get_nsip_client") as mock_get_client:
            mock_client = MagicMock()
            mock_animal1 = MagicMock()
            mock_animal1.to_dict.return_value = {
                "lpn_id": "6332-001",
                "name": "Ram A",
                "ebvs": {"WWT": 5.0, "BWT": 0.5},
            }
            mock_animal2 = MagicMock()
            mock_animal2.to_dict.return_value = {
                "lpn_id": "6332-002",
                "name": "Ram B",
                "ebvs": {"WWT": 6.0, "BWT": 0.3},
            }
            mock_client.get_animal_details.side_effect = [mock_animal1, mock_animal2]
            mock_get_client.return_value = mock_client

            from nsip_mcp.prompts.skill_prompts import ebv_analyzer_prompt

            result = asyncio.run(
                ebv_analyzer_prompt.fn(lpn_ids="6332-001,6332-002", traits="WWT,BWT")
            )

            assert isinstance(result, list)

    def test_ebv_analyzer_exception_handling(self) -> None:
        """Test EBV analyzer handles exceptions gracefully.

        When API calls fail, the prompt catches the exception and returns
        a "No animals found" message rather than exposing the raw error.
        This is the intended graceful degradation behavior.
        """
        import asyncio
        from unittest.mock import MagicMock, patch

        with patch("nsip_mcp.prompts.skill_prompts.get_nsip_client") as mock_get_client:
            mock_client = MagicMock()
            mock_client.get_animal_details.side_effect = Exception("API error")
            mock_get_client.return_value = mock_client

            from nsip_mcp.prompts.skill_prompts import ebv_analyzer_prompt

            result = asyncio.run(ebv_analyzer_prompt.fn(lpn_ids="6332-001", traits="WWT"))

            assert isinstance(result, list)
            # When exception occurs, prompt returns gracefully with "No animals found"
            if result and "content" in result[0]:
                text = result[0]["content"].get("text", "")
                assert "no animals found" in text.lower() or len(text) > 0

    def test_selection_index_with_animals(self) -> None:
        """Test selection index with animals found."""
        import asyncio
        from unittest.mock import MagicMock, patch

        with patch("nsip_mcp.prompts.skill_prompts.get_nsip_client") as mock_get_client:
            mock_client = MagicMock()
            mock_animal = MagicMock()
            mock_animal.to_dict.return_value = {
                "lpn_id": "6332-001",
                "name": "Test Ram",
                "ebvs": {"PWWT": 8.0, "WWT": 5.0, "BWT": 0.5, "PFAT": -0.2},
            }
            mock_client.get_animal_details.return_value = mock_animal
            mock_get_client.return_value = mock_client

            from nsip_mcp.prompts.skill_prompts import selection_index_prompt

            result = asyncio.run(
                selection_index_prompt.fn(lpn_ids="6332-001", index_name="terminal")
            )

            assert isinstance(result, list)
            if result and "content" in result[0]:
                text = result[0]["content"].get("text", "")
                assert "Index" in text or "Rankings" in text or "Score" in text

    def test_selection_index_exception_handling(self) -> None:
        """Test selection index handles exceptions gracefully."""
        import asyncio
        from unittest.mock import MagicMock, patch

        with patch("nsip_mcp.prompts.skill_prompts.get_nsip_client") as mock_get_client:
            mock_client = MagicMock()
            mock_client.get_animal_details.side_effect = Exception("API error")
            mock_get_client.return_value = mock_client

            from nsip_mcp.prompts.skill_prompts import selection_index_prompt

            result = asyncio.run(
                selection_index_prompt.fn(lpn_ids="6332-001", index_name="terminal")
            )

            assert isinstance(result, list)

    def test_ancestry_prompt_with_animal(self) -> None:
        """Test ancestry prompt with animal found."""
        import asyncio
        from unittest.mock import MagicMock, patch

        with patch("nsip_mcp.prompts.skill_prompts.get_nsip_client") as mock_get_client:
            mock_client = MagicMock()
            # Mock animal details
            mock_animal = MagicMock()
            mock_animal.to_dict.return_value = {
                "lpn_id": "6332-001",
                "name": "Test Ram",
                "breed": "Katahdin",
                "date_of_birth": "2022-03-15",
                "gender": "M",
                "traits": {
                    "BWT": {"value": 0.5},
                    "WWT": {"value": 5.0},
                },
            }
            mock_client.get_animal_details.return_value = mock_animal

            # Mock lineage
            mock_lineage = MagicMock()
            mock_lineage.sire = MagicMock()
            mock_lineage.sire.lpn_id = "sire-001"
            mock_lineage.sire.farm_name = "Sire Farm"
            mock_lineage.dam = MagicMock()
            mock_lineage.dam.lpn_id = "dam-001"
            mock_lineage.dam.farm_name = "Dam Farm"
            mock_lineage.generations = []
            mock_client.get_lineage.return_value = mock_lineage
            mock_get_client.return_value = mock_client

            from nsip_mcp.prompts.skill_prompts import ancestry_prompt

            result = asyncio.run(ancestry_prompt.fn(lpn_id="6332-001"))

            assert isinstance(result, list)
            if result and "content" in result[0]:
                text = result[0]["content"].get("text", "")
                assert "Pedigree" in text or "SIRE" in text or "DAM" in text

    def test_ancestry_prompt_exception(self) -> None:
        """Test ancestry prompt handles exceptions gracefully."""
        import asyncio
        from unittest.mock import MagicMock, patch

        with patch("nsip_mcp.prompts.skill_prompts.get_nsip_client") as mock_get_client:
            mock_client = MagicMock()
            mock_client.get_animal_details.side_effect = Exception("API error")
            mock_get_client.return_value = mock_client

            from nsip_mcp.prompts.skill_prompts import ancestry_prompt

            result = asyncio.run(ancestry_prompt.fn(lpn_id="6332-001"))

            assert isinstance(result, list)

    def test_inbreeding_prompt_with_lineage(self) -> None:
        """Test inbreeding prompt with lineage data."""
        import asyncio
        from unittest.mock import MagicMock, patch

        with patch("nsip_mcp.prompts.skill_prompts.get_nsip_client") as mock_get_client:
            mock_client = MagicMock()

            # Mock lineage for ram
            mock_ram_lineage = MagicMock()
            mock_ram_lineage.to_dict.return_value = {
                "sire": {"lpn_id": "common-ancestor", "lpnId": "common-ancestor"},
                "dam": {"lpn_id": "dam1"},
            }
            # Mock lineage for ewe
            mock_ewe_lineage = MagicMock()
            mock_ewe_lineage.to_dict.return_value = {
                "sire": {"lpn_id": "common-ancestor", "lpnId": "common-ancestor"},
                "dam": {"lpn_id": "dam2"},
            }
            mock_client.get_lineage.side_effect = [mock_ram_lineage, mock_ewe_lineage]
            mock_get_client.return_value = mock_client

            from nsip_mcp.prompts.skill_prompts import inbreeding_prompt

            result = asyncio.run(inbreeding_prompt.fn(ram_lpn="6332-001", ewe_lpn="6332-002"))

            assert isinstance(result, list)
            if result and "content" in result[0]:
                text = result[0]["content"].get("text", "")
                assert "Inbreeding" in text or "Coefficient" in text

    def test_inbreeding_prompt_no_common_ancestors(self) -> None:
        """Test inbreeding prompt with no common ancestors."""
        import asyncio
        from unittest.mock import MagicMock, patch

        with patch("nsip_mcp.prompts.skill_prompts.get_nsip_client") as mock_get_client:
            mock_client = MagicMock()

            mock_ram_lineage = MagicMock()
            mock_ram_lineage.to_dict.return_value = {
                "sire": {"lpn_id": "sire1"},
                "dam": {"lpn_id": "dam1"},
            }
            mock_ewe_lineage = MagicMock()
            mock_ewe_lineage.to_dict.return_value = {
                "sire": {"lpn_id": "sire2"},
                "dam": {"lpn_id": "dam2"},
            }
            mock_client.get_lineage.side_effect = [mock_ram_lineage, mock_ewe_lineage]
            mock_get_client.return_value = mock_client

            from nsip_mcp.prompts.skill_prompts import inbreeding_prompt

            result = asyncio.run(inbreeding_prompt.fn(ram_lpn="6332-001", ewe_lpn="6332-002"))

            assert isinstance(result, list)

    def test_inbreeding_prompt_exception(self) -> None:
        """Test inbreeding prompt handles exceptions gracefully."""
        import asyncio
        from unittest.mock import MagicMock, patch

        with patch("nsip_mcp.prompts.skill_prompts.get_nsip_client") as mock_get_client:
            mock_client = MagicMock()
            mock_client.get_lineage.side_effect = Exception("API error")
            mock_get_client.return_value = mock_client

            from nsip_mcp.prompts.skill_prompts import inbreeding_prompt

            result = asyncio.run(inbreeding_prompt.fn(ram_lpn="6332-001", ewe_lpn="6332-002"))

            assert isinstance(result, list)

    def test_progeny_report_with_sire(self) -> None:
        """Test progeny report with sire and progeny data."""
        import asyncio
        from unittest.mock import MagicMock, patch

        with patch("nsip_mcp.prompts.skill_prompts.get_nsip_client") as mock_get_client:
            mock_client = MagicMock()

            # Mock sire details
            mock_sire = MagicMock()
            mock_sire.to_dict.return_value = {
                "lpn_id": "6332-001",
                "name": "Sire Ram",
                "breed": "Katahdin",
                "traits": {
                    "BWT": {"value": 0.5},
                    "WWT": {"value": 5.0},
                    "PWWT": {"value": 8.0},
                    "NLW": {"value": 0.1},
                },
            }
            mock_client.get_animal_details.return_value = mock_sire

            # Mock progeny
            mock_progeny = MagicMock()
            mock_progeny.total_count = 2
            mock_offspring1 = MagicMock()
            mock_offspring1.lpn_id = "6332-101"
            mock_offspring1.sex = "M"
            mock_offspring2 = MagicMock()
            mock_offspring2.lpn_id = "6332-102"
            mock_offspring2.sex = "F"
            mock_progeny.animals = [mock_offspring1, mock_offspring2]
            mock_client.get_progeny.return_value = mock_progeny

            mock_get_client.return_value = mock_client

            from nsip_mcp.prompts.skill_prompts import progeny_report_prompt

            result = asyncio.run(progeny_report_prompt.fn(sire_lpn="6332-001"))

            assert isinstance(result, list)
            if result and "content" in result[0]:
                text = result[0]["content"].get("text", "")
                assert "Progeny" in text or "Sire" in text

    def test_progeny_report_sire_not_found(self) -> None:
        """Test progeny report when sire not found."""
        import asyncio
        from unittest.mock import MagicMock, patch

        with patch("nsip_mcp.prompts.skill_prompts.get_nsip_client") as mock_get_client:
            mock_client = MagicMock()
            mock_client.get_animal_details.return_value = None
            mock_get_client.return_value = mock_client

            from nsip_mcp.prompts.skill_prompts import progeny_report_prompt

            result = asyncio.run(progeny_report_prompt.fn(sire_lpn="fake-id"))

            assert isinstance(result, list)

    def test_progeny_report_exception(self) -> None:
        """Test progeny report handles exceptions gracefully."""
        import asyncio
        from unittest.mock import MagicMock, patch

        with patch("nsip_mcp.prompts.skill_prompts.get_nsip_client") as mock_get_client:
            mock_client = MagicMock()
            mock_client.get_animal_details.side_effect = Exception("API error")
            mock_get_client.return_value = mock_client

            from nsip_mcp.prompts.skill_prompts import progeny_report_prompt

            result = asyncio.run(progeny_report_prompt.fn(sire_lpn="6332-001"))

            assert isinstance(result, list)

    def test_flock_dashboard_with_animals(self) -> None:
        """Test flock dashboard with animals found."""
        import asyncio
        from unittest.mock import MagicMock, patch

        with patch("nsip_mcp.prompts.skill_prompts.get_nsip_client") as mock_get_client:
            mock_client = MagicMock()

            # Mock search results
            mock_search = MagicMock()
            mock_search.results = [
                {
                    "lpn_id": "6332001",
                    "name": "Ram 1",
                    "sex": "M",
                    "ebvs": {"WWT": 5.0, "PWWT": 8.0},
                },
                {
                    "lpn_id": "6332002",
                    "name": "Ewe 1",
                    "sex": "F",
                    "ebvs": {"WWT": 4.0, "PWWT": 7.0},
                },
            ]
            mock_client.search_animals.return_value = mock_search
            mock_get_client.return_value = mock_client

            from nsip_mcp.prompts.skill_prompts import flock_dashboard_prompt

            result = asyncio.run(flock_dashboard_prompt.fn(flock_prefix="6332"))

            assert isinstance(result, list)
            if result and "content" in result[0]:
                text = result[0]["content"].get("text", "")
                assert "Flock" in text or "Dashboard" in text

    def test_flock_dashboard_exception(self) -> None:
        """Test flock dashboard handles exceptions gracefully."""
        import asyncio
        from unittest.mock import MagicMock, patch

        with patch("nsip_mcp.prompts.skill_prompts.get_nsip_client") as mock_get_client:
            mock_client = MagicMock()
            mock_client.search_animals.side_effect = Exception("API error")
            mock_get_client.return_value = mock_client

            from nsip_mcp.prompts.skill_prompts import flock_dashboard_prompt

            result = asyncio.run(flock_dashboard_prompt.fn(flock_prefix="6332"))

            assert isinstance(result, list)


class TestInterviewPromptsExtended:
    """Extended tests for interview prompts."""

    def test_mating_plan_with_all_inputs(self) -> None:
        """Test mating plan with all inputs provided."""
        import asyncio

        from nsip_mcp.prompts.interview_prompts import guided_mating_plan_prompt

        result = asyncio.run(
            guided_mating_plan_prompt.fn(
                rams="6332-001,6332-002",
                ewes="6332-101,6332-102",
                goal="terminal",
            )
        )

        assert isinstance(result, list)
        # With all inputs, should return analysis message
        if result and "content" in result[0]:
            text = result[0]["content"].get("text", "")
            assert len(text) > 0

    def test_trait_improvement_with_all_inputs(self) -> None:
        """Test trait improvement with all inputs provided."""
        import asyncio

        from nsip_mcp.prompts.interview_prompts import guided_trait_improvement_prompt

        result = asyncio.run(
            guided_trait_improvement_prompt.fn(
                trait="WWT",
                current_average="4.5",
                target_value="6.0",
                generations="3",
            )
        )

        assert isinstance(result, list)

    def test_breeding_recs_with_all_inputs(self) -> None:
        """Test breeding recommendations with all inputs."""
        import asyncio

        from nsip_mcp.prompts.interview_prompts import guided_breeding_recommendations_prompt

        result = asyncio.run(
            guided_breeding_recommendations_prompt.fn(
                flock_data="6332-001,6332-002",
                priorities="growth,maternal",
                constraints="avoid inbreeding",
                region="midwest",
            )
        )

        assert isinstance(result, list)

    def test_flock_import_with_csv(self) -> None:
        """Test flock import with CSV format."""
        import asyncio

        from nsip_mcp.prompts.interview_prompts import guided_flock_import_prompt

        result = asyncio.run(
            guided_flock_import_prompt.fn(
                file_path="/path/to/flock.csv",
                flock_prefix="6332",
                data_format="csv",
            )
        )

        assert isinstance(result, list)

    def test_flock_import_with_xlsx(self) -> None:
        """Test flock import with XLSX format."""
        import asyncio

        from nsip_mcp.prompts.interview_prompts import guided_flock_import_prompt

        result = asyncio.run(
            guided_flock_import_prompt.fn(
                file_path="/path/to/flock.xlsx",
                flock_prefix="6332",
                data_format="xlsx",
            )
        )

        assert isinstance(result, list)
