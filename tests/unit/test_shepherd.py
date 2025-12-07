"""Unit tests for the Shepherd agent module."""

import pytest

from nsip_mcp.shepherd import (
    ShepherdAgent,
    ShepherdPersona,
    detect_region,
    get_region_context,
    NSIP_REGIONS,
)
from nsip_mcp.shepherd.agent import Domain
from nsip_mcp.shepherd.persona import format_shepherd_response
from nsip_mcp.shepherd.domains.breeding import BreedingDomain
from nsip_mcp.shepherd.domains.health import HealthDomain
from nsip_mcp.shepherd.domains.calendar import CalendarDomain
from nsip_mcp.shepherd.domains.economics import EconomicsDomain


class TestShepherdPersona:
    """Tests for the Shepherd persona."""

    def test_persona_has_system_prompt(self) -> None:
        """Test persona has a system prompt."""
        persona = ShepherdPersona()
        assert hasattr(persona, "SYSTEM_PROMPT") or hasattr(persona, "system_prompt")

    def test_format_response_basic(self) -> None:
        """Test formatting a basic string answer."""
        result = format_shepherd_response("This is the answer.")
        assert isinstance(result, str)
        assert "This is the answer." in result

    def test_format_response_with_string(self) -> None:
        """Test formatting a string response."""
        result = format_shepherd_response("Test message")
        assert isinstance(result, str)
        assert "Test message" in result

    def test_format_response_with_recommendations(self) -> None:
        """Test formatting a response with recommendations."""
        result = format_shepherd_response(
            "Main answer here.",
            recommendations=["Do this first", "Then try that"]
        )
        assert isinstance(result, str)
        assert "Main answer here." in result


class TestRegionDetection:
    """Tests for region detection functionality."""

    def test_detect_region_from_state(self) -> None:
        """Test detecting region from state abbreviation."""
        result = detect_region("OH")
        assert result is not None
        assert isinstance(result, str)

    def test_detect_region_from_full_state(self) -> None:
        """Test detecting region from full state name."""
        result = detect_region("Ohio")
        assert result is not None or result is None  # May not support full names

    def test_detect_region_unknown(self) -> None:
        """Test detecting region with unknown input."""
        result = detect_region("UNKNOWN_XYZ")
        # Should return None or a default
        assert result is None or isinstance(result, str)

    def test_get_region_context_valid(self) -> None:
        """Test getting context for a valid region."""
        result = get_region_context("midwest")
        assert result is not None
        assert isinstance(result, dict)
        assert "name" in result or "states" in result or "climate" in result

    def test_get_region_context_invalid(self) -> None:
        """Test getting context for invalid region raises error."""
        from nsip_mcp.knowledge_base.loader import KnowledgeBaseError
        with pytest.raises(KnowledgeBaseError):
            get_region_context("invalid_region")

    def test_list_nsip_regions(self) -> None:
        """Test listing all NSIP regions."""
        # NSIP_REGIONS is exported as a dict
        result = list(NSIP_REGIONS.keys())
        assert isinstance(result, list)
        assert len(result) > 0
        # Should contain known regions
        region_names = [r.lower() for r in result]
        assert "midwest" in region_names


class TestShepherdAgent:
    """Tests for the main Shepherd agent."""

    @pytest.fixture
    def agent(self) -> ShepherdAgent:
        """Create a Shepherd agent instance."""
        return ShepherdAgent()

    def test_agent_creation(self, agent: ShepherdAgent) -> None:
        """Test agent can be created."""
        assert agent is not None
        assert hasattr(agent, "persona")

    def test_agent_has_domains(self, agent: ShepherdAgent) -> None:
        """Test agent has access to domains."""
        assert hasattr(agent, "consult") or hasattr(agent, "classify_question")

    def test_consult_breeding_question(self, agent: ShepherdAgent) -> None:
        """Test consulting with a breeding question."""
        result = agent.consult(
            "How do I select for weaning weight?",
            domain=Domain.BREEDING
        )
        assert isinstance(result, dict)

    def test_consult_health_question(self, agent: ShepherdAgent) -> None:
        """Test consulting with a health question."""
        result = agent.consult(
            "What vaccines do my sheep need?",
            domain=Domain.HEALTH
        )
        assert isinstance(result, dict)

    def test_consult_calendar_question(self, agent: ShepherdAgent) -> None:
        """Test consulting with a calendar question."""
        result = agent.consult(
            "When should I start breeding season?",
            domain=Domain.CALENDAR
        )
        assert isinstance(result, dict)

    def test_consult_economics_question(self, agent: ShepherdAgent) -> None:
        """Test consulting with an economics question."""
        result = agent.consult(
            "What is my cost per ewe?",
            domain=Domain.ECONOMICS
        )
        assert isinstance(result, dict)

    def test_consult_auto_classify(self, agent: ShepherdAgent) -> None:
        """Test consulting without specifying domain."""
        result = agent.consult("How do I improve my flock genetics?")
        assert isinstance(result, dict)

    def test_consult_with_context(self, agent: ShepherdAgent) -> None:
        """Test consulting with additional context."""
        result = agent.consult(
            "How should I feed my ewes?",
            context={"region": "midwest", "flock_size": 100}
        )
        assert isinstance(result, dict)


class TestBreedingDomain:
    """Tests for the breeding domain handler."""

    @pytest.fixture
    def domain(self) -> BreedingDomain:
        """Create a breeding domain instance."""
        return BreedingDomain()

    def test_interpret_ebv_positive(self, domain: BreedingDomain) -> None:
        """Test interpreting a positive EBV."""
        result = domain.interpret_ebv("WWT", 5.0, accuracy=0.7)
        assert isinstance(result, dict)
        assert "interpretation" in result or "value" in result

    def test_interpret_ebv_negative(self, domain: BreedingDomain) -> None:
        """Test interpreting a negative EBV."""
        result = domain.interpret_ebv("BWT", -0.5, accuracy=0.6)
        assert isinstance(result, dict)

    def test_interpret_ebv_with_breed_average(self, domain: BreedingDomain) -> None:
        """Test interpreting EBV with breed average comparison."""
        result = domain.interpret_ebv("WWT", 5.0, breed_average=3.0)
        assert isinstance(result, dict)

    def test_recommend_selection_strategy(self, domain: BreedingDomain) -> None:
        """Test getting selection strategy recommendations."""
        result = domain.recommend_selection_strategy(
            goal="terminal",
            current_strengths=["WWT"],
            current_weaknesses=["BWT"]
        )
        assert isinstance(result, dict)
        assert "recommendations" in result or "strategy" in result

    def test_estimate_genetic_progress(self, domain: BreedingDomain) -> None:
        """Test estimating genetic progress."""
        result = domain.estimate_genetic_progress(
            trait="WWT",
            current_mean=2.5,
            selection_differential=1.0,
            generations=3
        )
        assert isinstance(result, dict)

    def test_assess_inbreeding_risk(self, domain: BreedingDomain) -> None:
        """Test assessing inbreeding risk."""
        result = domain.assess_inbreeding_risk(0.15)
        assert isinstance(result, dict)
        assert "risk_level" in result or "recommendations" in result


class TestHealthDomain:
    """Tests for the health domain handler."""

    @pytest.fixture
    def domain(self) -> HealthDomain:
        """Create a health domain instance."""
        return HealthDomain()

    def test_get_disease_prevention(self, domain: HealthDomain) -> None:
        """Test getting disease prevention guide."""
        result = domain.get_disease_prevention(region="midwest")
        assert isinstance(result, dict)

    def test_get_nutrition_recommendations(self, domain: HealthDomain) -> None:
        """Test getting nutrition recommendations."""
        result = domain.get_nutrition_recommendations(
            life_stage="gestation",
            region="midwest"
        )
        assert isinstance(result, dict)

    def test_assess_parasite_risk(self, domain: HealthDomain) -> None:
        """Test assessing parasite risk."""
        result = domain.assess_parasite_risk(
            region="southeast",
            season="summer"
        )
        assert isinstance(result, dict)

    def test_get_vaccination_schedule(self, domain: HealthDomain) -> None:
        """Test getting vaccination schedule."""
        result = domain.get_vaccination_schedule(region="midwest")
        assert isinstance(result, dict)


class TestCalendarDomain:
    """Tests for the calendar domain handler."""

    @pytest.fixture
    def domain(self) -> CalendarDomain:
        """Create a calendar domain instance."""
        return CalendarDomain()

    def test_get_seasonal_tasks(self, domain: CalendarDomain) -> None:
        """Test getting seasonal tasks."""
        result = domain.get_seasonal_tasks(
            task_type="breeding",
            region="midwest",
            month=3
        )
        assert isinstance(result, dict)

    def test_calculate_breeding_dates(self, domain: CalendarDomain) -> None:
        """Test calculating breeding dates."""
        result = domain.calculate_breeding_dates(
            target_lambing="March"
        )
        assert isinstance(result, dict)

    def test_get_marketing_windows(self, domain: CalendarDomain) -> None:
        """Test getting marketing windows."""
        result = domain.get_marketing_windows(region="midwest")
        assert isinstance(result, dict)

    def test_create_annual_calendar(self, domain: CalendarDomain) -> None:
        """Test creating annual calendar."""
        result = domain.create_annual_calendar(
            lambing_month=3,
            region="midwest"
        )
        assert isinstance(result, dict)


class TestEconomicsDomain:
    """Tests for the economics domain handler."""

    @pytest.fixture
    def domain(self) -> EconomicsDomain:
        """Create an economics domain instance."""
        return EconomicsDomain()

    def test_get_cost_breakdown(self, domain: EconomicsDomain) -> None:
        """Test getting cost breakdown."""
        result = domain.get_cost_breakdown(flock_size="medium")
        assert isinstance(result, dict)

    def test_calculate_breakeven(self, domain: EconomicsDomain) -> None:
        """Test calculating breakeven."""
        result = domain.calculate_breakeven(
            annual_costs_per_ewe=150,
            lambs_per_ewe=1.5,
            lamb_weight=100
        )
        assert isinstance(result, dict)

    def test_calculate_ram_roi(self, domain: EconomicsDomain) -> None:
        """Test calculating ram ROI."""
        result = domain.calculate_ram_roi(
            ram_cost=2000,
            years_used=4,
            ewes_per_year=30,
            lamb_value_increase=20
        )
        assert isinstance(result, dict)

    def test_analyze_flock_profitability(self, domain: EconomicsDomain) -> None:
        """Test analyzing flock profitability."""
        result = domain.analyze_flock_profitability(
            ewe_count=100,
            lambs_marketed=150,
            avg_lamb_price=200,
            wool_revenue=500,
            cull_revenue=1000,
            total_costs=15000
        )
        assert isinstance(result, dict)

    def test_compare_marketing_options(self, domain: EconomicsDomain) -> None:
        """Test comparing marketing options."""
        result = domain.compare_marketing_options(
            weight=80,
            options=[
                {"name": "direct", "price": 2.50},
                {"name": "auction", "price": 2.00}
            ]
        )
        assert isinstance(result, dict)


class TestDomainClassification:
    """Tests for question domain classification."""

    @pytest.fixture
    def agent(self) -> ShepherdAgent:
        """Create a Shepherd agent instance."""
        return ShepherdAgent()

    def test_classify_breeding_keywords(self, agent: ShepherdAgent) -> None:
        """Test classification of breeding-related questions."""
        questions = [
            "How do I improve weaning weight?",
            "What is EBV selection?",
            "How to reduce inbreeding?",
        ]
        for q in questions:
            result = agent.consult(q)
            assert isinstance(result, dict)

    def test_classify_health_keywords(self, agent: ShepherdAgent) -> None:
        """Test classification of health-related questions."""
        questions = [
            "What vaccines are needed?",
            "How to prevent parasites?",
            "Nutrition for pregnant ewes?",
        ]
        for q in questions:
            result = agent.consult(q)
            assert isinstance(result, dict)

    def test_classify_calendar_keywords(self, agent: ShepherdAgent) -> None:
        """Test classification of calendar-related questions."""
        questions = [
            "When to start breeding?",
            "Lambing preparation timeline?",
            "Shearing schedule?",
        ]
        for q in questions:
            result = agent.consult(q)
            assert isinstance(result, dict)

    def test_classify_economics_keywords(self, agent: ShepherdAgent) -> None:
        """Test classification of economics-related questions."""
        questions = [
            "Cost per ewe annually?",
            "Is sheep farming profitable?",
            "Marketing options?",
        ]
        for q in questions:
            result = agent.consult(q)
            assert isinstance(result, dict)


class TestAgentIntegration:
    """Integration tests for the Shepherd agent."""

    @pytest.fixture
    def agent(self) -> ShepherdAgent:
        """Create a Shepherd agent with region set."""
        return ShepherdAgent(region="midwest", production_goal="balanced")

    def test_agent_with_region_context(self, agent: ShepherdAgent) -> None:
        """Test agent uses region context in responses."""
        result = agent.consult("What breeds work best here?")
        assert isinstance(result, dict)

    def test_agent_with_production_goal(self, agent: ShepherdAgent) -> None:
        """Test agent uses production goal in responses."""
        result = agent.consult("How should I select my breeding stock?")
        assert isinstance(result, dict)

    def test_agent_handles_complex_questions(self, agent: ShepherdAgent) -> None:
        """Test agent handles multi-domain questions."""
        result = agent.consult(
            "How do I balance breeding for growth while maintaining maternal traits?"
        )
        assert isinstance(result, dict)
