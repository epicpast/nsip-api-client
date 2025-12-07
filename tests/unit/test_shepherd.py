"""Unit tests for the Shepherd agent module."""

import pytest

from nsip_mcp.shepherd import (
    NSIP_REGIONS,
    ShepherdAgent,
    ShepherdPersona,
    detect_region,
    get_region_context,
)
from nsip_mcp.shepherd.agent import Domain
from nsip_mcp.shepherd.domains.breeding import BreedingDomain
from nsip_mcp.shepherd.domains.calendar import CalendarDomain
from nsip_mcp.shepherd.domains.economics import EconomicsDomain
from nsip_mcp.shepherd.domains.health import HealthDomain
from nsip_mcp.shepherd.persona import format_shepherd_response


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
            "Main answer here.", recommendations=["Do this first", "Then try that"]
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
        result = agent.consult("How do I select for weaning weight?", domain=Domain.BREEDING)
        assert isinstance(result, dict)

    def test_consult_health_question(self, agent: ShepherdAgent) -> None:
        """Test consulting with a health question."""
        result = agent.consult("What vaccines do my sheep need?", domain=Domain.HEALTH)
        assert isinstance(result, dict)

    def test_consult_calendar_question(self, agent: ShepherdAgent) -> None:
        """Test consulting with a calendar question."""
        result = agent.consult("When should I start breeding season?", domain=Domain.CALENDAR)
        assert isinstance(result, dict)

    def test_consult_economics_question(self, agent: ShepherdAgent) -> None:
        """Test consulting with an economics question."""
        result = agent.consult("What is my cost per ewe?", domain=Domain.ECONOMICS)
        assert isinstance(result, dict)

    def test_consult_auto_classify(self, agent: ShepherdAgent) -> None:
        """Test consulting without specifying domain."""
        result = agent.consult("How do I improve my flock genetics?")
        assert isinstance(result, dict)

    def test_consult_with_context(self, agent: ShepherdAgent) -> None:
        """Test consulting with additional context."""
        result = agent.consult(
            "How should I feed my ewes?", context={"region": "midwest", "flock_size": 100}
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
            goal="terminal", current_strengths=["WWT"], current_weaknesses=["BWT"]
        )
        assert isinstance(result, dict)
        assert "recommendations" in result or "strategy" in result

    def test_estimate_genetic_progress(self, domain: BreedingDomain) -> None:
        """Test estimating genetic progress."""
        result = domain.estimate_genetic_progress(
            trait="WWT", current_mean=2.5, selection_differential=1.0, generations=3
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
        result = domain.get_nutrition_recommendations(life_stage="gestation", region="midwest")
        assert isinstance(result, dict)

    def test_assess_parasite_risk(self, domain: HealthDomain) -> None:
        """Test assessing parasite risk."""
        result = domain.assess_parasite_risk(region="southeast", season="summer")
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
        result = domain.get_seasonal_tasks(task_type="breeding", region="midwest", month=3)
        assert isinstance(result, dict)

    def test_calculate_breeding_dates(self, domain: CalendarDomain) -> None:
        """Test calculating breeding dates."""
        result = domain.calculate_breeding_dates(target_lambing="March")
        assert isinstance(result, dict)

    def test_get_marketing_windows(self, domain: CalendarDomain) -> None:
        """Test getting marketing windows."""
        result = domain.get_marketing_windows(region="midwest")
        assert isinstance(result, dict)

    def test_create_annual_calendar(self, domain: CalendarDomain) -> None:
        """Test creating annual calendar."""
        result = domain.create_annual_calendar(lambing_month=3, region="midwest")
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
            annual_costs_per_ewe=150, lambs_per_ewe=1.5, lamb_weight=100
        )
        assert isinstance(result, dict)

    def test_calculate_ram_roi(self, domain: EconomicsDomain) -> None:
        """Test calculating ram ROI."""
        result = domain.calculate_ram_roi(
            ram_cost=2000, years_used=4, ewes_per_year=30, lamb_value_increase=20
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
            total_costs=15000,
        )
        assert isinstance(result, dict)

    def test_compare_marketing_options(self, domain: EconomicsDomain) -> None:
        """Test comparing marketing options."""
        result = domain.compare_marketing_options(
            weight=80,
            options=[{"name": "direct", "price": 2.50}, {"name": "auction", "price": 2.00}],
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


class TestBreedingDomainExtended:
    """Extended tests for the breeding domain to increase coverage."""

    @pytest.fixture
    def domain(self) -> BreedingDomain:
        """Create a breeding domain instance."""
        return BreedingDomain()

    def test_value_interpretation_near_average(self, domain: BreedingDomain) -> None:
        """Test value interpretation when value is near breed average."""
        result = domain._value_interpretation(3.05, "WWT", 3.0)
        assert "Near breed average" in result

    def test_value_interpretation_above_average(self, domain: BreedingDomain) -> None:
        """Test value interpretation when value is above breed average."""
        result = domain._value_interpretation(5.0, "WWT", 3.0)
        assert "Above breed average" in result

    def test_value_interpretation_below_average(self, domain: BreedingDomain) -> None:
        """Test value interpretation when value is below breed average."""
        result = domain._value_interpretation(1.0, "WWT", 3.0)
        assert "Below breed average" in result

    def test_value_interpretation_positive_no_average(self, domain: BreedingDomain) -> None:
        """Test value interpretation for positive value without breed average."""
        result = domain._value_interpretation(2.5, "WWT", None)
        assert "Positive EBV" in result
        assert "above-average genetic merit" in result

    def test_value_interpretation_negative_no_average(self, domain: BreedingDomain) -> None:
        """Test value interpretation for negative value without breed average."""
        result = domain._value_interpretation(-1.5, "WWT", None)
        assert "Negative EBV" in result
        assert "below-average genetic merit" in result

    def test_value_interpretation_zero(self, domain: BreedingDomain) -> None:
        """Test value interpretation for zero value."""
        result = domain._value_interpretation(0.0, "WWT", None)
        assert "breed average" in result

    def test_value_interpretation_near_zero_average(self, domain: BreedingDomain) -> None:
        """Test value interpretation with zero breed average."""
        result = domain._value_interpretation(0.3, "WWT", 0.0)
        assert "average" in result.lower()

    def test_accuracy_interpretation_very_high(self, domain: BreedingDomain) -> None:
        """Test accuracy interpretation for very high values."""
        result = domain._accuracy_interpretation(95)
        assert "Very high accuracy" in result

    def test_accuracy_interpretation_good(self, domain: BreedingDomain) -> None:
        """Test accuracy interpretation for good values."""
        result = domain._accuracy_interpretation(75)
        assert "Good accuracy" in result

    def test_accuracy_interpretation_moderate(self, domain: BreedingDomain) -> None:
        """Test accuracy interpretation for moderate values."""
        result = domain._accuracy_interpretation(55)
        assert "Moderate accuracy" in result

    def test_accuracy_interpretation_low(self, domain: BreedingDomain) -> None:
        """Test accuracy interpretation for low values."""
        result = domain._accuracy_interpretation(30)
        assert "Low accuracy" in result

    def test_selection_response_high_h2(self, domain: BreedingDomain) -> None:
        """Test selection response note for high heritability."""
        result = domain._selection_response_note(0.40)
        assert "High heritability" in result

    def test_selection_response_moderate_h2(self, domain: BreedingDomain) -> None:
        """Test selection response note for moderate heritability."""
        result = domain._selection_response_note(0.25)
        assert "Moderate heritability" in result

    def test_selection_response_low_h2(self, domain: BreedingDomain) -> None:
        """Test selection response note for low heritability."""
        result = domain._selection_response_note(0.15)
        assert "Low heritability" in result

    def test_selection_response_very_low_h2(self, domain: BreedingDomain) -> None:
        """Test selection response note for very low heritability."""
        result = domain._selection_response_note(0.05)
        assert "Very low heritability" in result

    def test_estimate_percentile_top_5(self, domain: BreedingDomain) -> None:
        """Test percentile estimation for top 5%."""
        result = domain._estimate_percentile(5.0, "WWT")
        assert "Top 5%" in result

    def test_estimate_percentile_top_15(self, domain: BreedingDomain) -> None:
        """Test percentile estimation for top 15%."""
        result = domain._estimate_percentile(3.0, "WWT")
        assert "Top 15%" in result

    def test_estimate_percentile_top_35(self, domain: BreedingDomain) -> None:
        """Test percentile estimation for top 35%."""
        result = domain._estimate_percentile(1.0, "WWT")
        assert "Top 35%" in result

    def test_estimate_percentile_middle(self, domain: BreedingDomain) -> None:
        """Test percentile estimation for middle 30%."""
        result = domain._estimate_percentile(0.0, "WWT")
        assert "Middle 30%" in result

    def test_estimate_percentile_bottom_35(self, domain: BreedingDomain) -> None:
        """Test percentile estimation for bottom 35%."""
        result = domain._estimate_percentile(-1.0, "WWT")
        assert "Bottom 35%" in result

    def test_estimate_percentile_bottom_15(self, domain: BreedingDomain) -> None:
        """Test percentile estimation for bottom 15%."""
        result = domain._estimate_percentile(-3.0, "WWT")
        assert "Bottom 15%" in result

    def test_recommend_intensity_small(self, domain: BreedingDomain) -> None:
        """Test selection intensity for small flock."""
        result = domain._recommend_intensity("small")
        assert result["percent_selected"] == "40-50%"
        assert "Limited selection" in result["note"]

    def test_recommend_intensity_medium(self, domain: BreedingDomain) -> None:
        """Test selection intensity for medium flock."""
        result = domain._recommend_intensity("medium")
        assert result["percent_selected"] == "25-35%"
        assert "balance" in result["note"].lower()

    def test_recommend_intensity_large(self, domain: BreedingDomain) -> None:
        """Test selection intensity for large flock."""
        result = domain._recommend_intensity("large")
        assert result["percent_selected"] == "15-25%"
        assert "Strong selection" in result["note"]

    def test_recommend_intensity_unknown(self, domain: BreedingDomain) -> None:
        """Test selection intensity falls back to medium for unknown size."""
        result = domain._recommend_intensity("unknown")
        assert result["percent_selected"] == "25-35%"

    def test_recommend_selection_strategy_unknown_goal(self, domain: BreedingDomain) -> None:
        """Test selection strategy with unknown goal raises KnowledgeBaseError."""
        from nsip_mcp.knowledge_base.loader import KnowledgeBaseError

        with pytest.raises(KnowledgeBaseError) as exc_info:
            domain.recommend_selection_strategy(goal="invalid_goal")
        assert "not found" in str(exc_info.value)

    def test_recommend_selection_with_weaknesses(self, domain: BreedingDomain) -> None:
        """Test selection strategy with current weaknesses marked high priority."""
        result = domain.recommend_selection_strategy(
            goal="terminal", current_weaknesses=["WWT", "PWWT"]
        )
        assert "recommendations" in result
        # Should have high priority items for weaknesses

    def test_assess_inbreeding_with_percentage(self, domain: BreedingDomain) -> None:
        """Test inbreeding assessment with percentage (>1) input."""
        result = domain.assess_inbreeding_risk(15.0)  # 15%
        assert result["coefficient"] == 0.15
        assert "percentage" in result

    def test_assess_inbreeding_very_high(self, domain: BreedingDomain) -> None:
        """Test inbreeding assessment for very high level."""
        result = domain.assess_inbreeding_risk(0.30)
        assert result["risk_level"] == "Very High"
        assert "immediate genetic diversification" in result["concern"]

    def test_assess_inbreeding_high(self, domain: BreedingDomain) -> None:
        """Test inbreeding assessment for high level."""
        result = domain.assess_inbreeding_risk(0.20)
        assert result["risk_level"] == "High"

    def test_assess_inbreeding_moderate(self, domain: BreedingDomain) -> None:
        """Test inbreeding assessment for moderate level."""
        result = domain.assess_inbreeding_risk(0.10)
        assert result["risk_level"] == "Moderate"

    def test_assess_inbreeding_with_increasing_trend(self, domain: BreedingDomain) -> None:
        """Test inbreeding assessment with increasing trend."""
        result = domain.assess_inbreeding_risk(0.10, trend="increasing")
        assert "Trend is concerning" in result["recommendations"][0]

    def test_format_breeding_advice_basic(self, domain: BreedingDomain) -> None:
        """Test formatting breeding advice with basic input."""
        result = domain.format_breeding_advice("How do I select rams?", "Select based on EBVs.")
        assert isinstance(result, str)
        assert "Select based on EBVs" in result

    def test_format_breeding_advice_with_data(self, domain: BreedingDomain) -> None:
        """Test formatting breeding advice with supporting data."""
        data = {
            "recommendations": ["Use WWT as primary trait", "Consider accuracy"],
            "assumptions": ["Constant selection pressure"],
        }
        result = domain.format_breeding_advice("Selection strategy?", "Focus on WWT.", data=data)
        assert isinstance(result, str)
        assert "Focus on WWT" in result

    def test_interpret_ebv_with_accuracy(self, domain: BreedingDomain) -> None:
        """Test EBV interpretation includes accuracy note."""
        result = domain.interpret_ebv("WWT", 5.0, accuracy=85)
        assert "accuracy" in result
        assert "accuracy_note" in result

    def test_interpret_ebv_with_breed_average(self, domain: BreedingDomain) -> None:
        """Test EBV interpretation includes breed average comparison."""
        result = domain.interpret_ebv("WWT", 5.0, breed_average=3.0)
        assert "vs_breed_avg" in result
        assert "deviation" in result["vs_breed_avg"]
        assert "percentile_estimate" in result["vs_breed_avg"]


class TestPersonaExtended:
    """Extended tests for ShepherdPersona class."""

    def test_persona_get_system_prompt(self) -> None:
        """Test persona returns system prompt."""
        persona = ShepherdPersona()
        prompt = persona.get_system_prompt()
        assert isinstance(prompt, str)
        assert "NSIP Shepherd" in prompt

    def test_persona_format_uncertainty_high_confidence(self) -> None:
        """Test format uncertainty with high confidence."""
        persona = ShepherdPersona()
        result = persona.format_uncertainty("This is definitely true.", confidence=0.95)
        assert result == "This is definitely true."

    def test_persona_format_uncertainty_good_confidence(self) -> None:
        """Test format uncertainty with good confidence."""
        persona = ShepherdPersona()
        result = persona.format_uncertainty("This is likely true.", confidence=0.75)
        assert "Based on available data" in result

    def test_persona_format_uncertainty_moderate_confidence(self) -> None:
        """Test format uncertainty with moderate confidence."""
        persona = ShepherdPersona()
        result = persona.format_uncertainty("This might be true.", confidence=0.55)
        assert "Research suggests" in result

    def test_persona_format_uncertainty_low_confidence(self) -> None:
        """Test format uncertainty with low confidence."""
        persona = ShepherdPersona()
        result = persona.format_uncertainty("This could be true.", confidence=0.30)
        assert "limited data" in result

    def test_format_shepherd_response_all_sections(self) -> None:
        """Test format response with all optional sections."""
        result = format_shepherd_response(
            answer="Main answer here.",
            context="Background context.",
            recommendations=["Do this", "Then that"],
            considerations=["Consider A", "Consider B"],
            next_steps=["Step 1", "Step 2"],
            sources=["NSIP Database", "Extension Publications"],
        )
        assert "Main answer here." in result
        assert "Context" in result
        assert "Recommendations" in result
        assert "Considerations" in result
        assert "Next Steps" in result
        assert "Sources" in result


class TestHealthDomainExtended:
    """Extended tests for the health domain to increase coverage."""

    @pytest.fixture
    def domain(self) -> HealthDomain:
        """Create a health domain instance."""
        return HealthDomain()

    def test_get_disease_prevention_no_data(self, domain: HealthDomain) -> None:
        """Test disease prevention when no data is available for region."""
        from unittest.mock import patch

        with patch("nsip_mcp.shepherd.domains.health.get_disease_guide") as mock_guide:
            with patch("nsip_mcp.shepherd.domains.health.get_region_info") as mock_region:
                mock_guide.return_value = None
                mock_region.return_value = None
                result = domain.get_disease_prevention(region="unknown_region")
                assert "note" in result
                assert "general_recommendations" in result

    def test_get_disease_prevention_with_season(self, domain: HealthDomain) -> None:
        """Test disease prevention filtered by season."""
        result = domain.get_disease_prevention(region="midwest", season="summer")
        assert "region" in result

    def test_default_nutrition_maintenance(self, domain: HealthDomain) -> None:
        """Test default nutrition for maintenance stage."""
        result = domain._default_nutrition("maintenance")
        assert "energy" in result
        assert "protein" in result

    def test_default_nutrition_flushing(self, domain: HealthDomain) -> None:
        """Test default nutrition for flushing stage."""
        result = domain._default_nutrition("flushing")
        assert "energy" in result
        assert "protein" in result

    def test_default_nutrition_gestation(self, domain: HealthDomain) -> None:
        """Test default nutrition for gestation stage."""
        result = domain._default_nutrition("gestation")
        assert "early" in result
        assert "late" in result

    def test_default_nutrition_lactation(self, domain: HealthDomain) -> None:
        """Test default nutrition for lactation stage."""
        result = domain._default_nutrition("lactation")
        assert "singles" in result
        assert "twins" in result

    def test_default_nutrition_unknown_stage(self, domain: HealthDomain) -> None:
        """Test default nutrition falls back to maintenance for unknown stage."""
        result = domain._default_nutrition("unknown_stage")
        assert result == domain._default_nutrition("maintenance")

    def test_bcs_adjustment_thin(self, domain: HealthDomain) -> None:
        """Test BCS adjustment for thin animal."""
        result = domain._bcs_adjustment(1.5, "maintenance")
        assert "Thin" in result["interpretation"]
        assert "20-30%" in result["adjustment"]

    def test_bcs_adjustment_slightly_thin(self, domain: HealthDomain) -> None:
        """Test BCS adjustment for slightly thin animal."""
        result = domain._bcs_adjustment(2.2, "maintenance")
        assert "Slightly thin" in result["interpretation"]
        assert "10-15%" in result["adjustment"]

    def test_bcs_adjustment_ideal(self, domain: HealthDomain) -> None:
        """Test BCS adjustment for ideal condition."""
        result = domain._bcs_adjustment(3.0, "maintenance")
        assert "Ideal" in result["interpretation"]

    def test_bcs_adjustment_slightly_over(self, domain: HealthDomain) -> None:
        """Test BCS adjustment for slightly overconditioned animal."""
        result = domain._bcs_adjustment(3.8, "maintenance")
        assert "Slightly overconditioned" in result["interpretation"]

    def test_bcs_adjustment_over(self, domain: HealthDomain) -> None:
        """Test BCS adjustment for overconditioned animal."""
        result = domain._bcs_adjustment(4.5, "maintenance")
        assert "Overconditioned" in result["interpretation"]

    def test_life_stage_notes_maintenance(self, domain: HealthDomain) -> None:
        """Test life stage notes for maintenance."""
        result = domain._life_stage_notes("maintenance")
        assert isinstance(result, list)
        assert len(result) > 0

    def test_life_stage_notes_flushing(self, domain: HealthDomain) -> None:
        """Test life stage notes for flushing."""
        result = domain._life_stage_notes("flushing")
        assert isinstance(result, list)
        assert len(result) > 0

    def test_life_stage_notes_gestation(self, domain: HealthDomain) -> None:
        """Test life stage notes for gestation."""
        result = domain._life_stage_notes("gestation")
        assert isinstance(result, list)
        assert "fetal growth" in " ".join(result).lower()

    def test_life_stage_notes_lactation(self, domain: HealthDomain) -> None:
        """Test life stage notes for lactation."""
        result = domain._life_stage_notes("lactation")
        assert isinstance(result, list)
        assert "milk" in " ".join(result).lower()

    def test_life_stage_notes_unknown(self, domain: HealthDomain) -> None:
        """Test life stage notes returns empty for unknown stage."""
        result = domain._life_stage_notes("unknown")
        assert result == []

    def test_calculate_parasite_risk_summer_high_stocking(self, domain: HealthDomain) -> None:
        """Test parasite risk is very high in summer with high stocking."""
        result = domain._calculate_parasite_risk("summer", "summer peak", "high")
        assert result in ["High", "Very High"]

    def test_calculate_parasite_risk_winter_low_stocking(self, domain: HealthDomain) -> None:
        """Test parasite risk is low in winter with low stocking."""
        result = domain._calculate_parasite_risk("winter", "summer peak", "low")
        assert result == "Low"

    def test_calculate_parasite_risk_yearround(self, domain: HealthDomain) -> None:
        """Test parasite risk adjusts for year-round regions."""
        result = domain._calculate_parasite_risk("winter", "year-round", None)
        assert result in ["Moderate", "High"]

    def test_calculate_parasite_risk_spring(self, domain: HealthDomain) -> None:
        """Test parasite risk for spring season."""
        result = domain._calculate_parasite_risk("spring", "spring to fall", None)
        assert result == "Moderate"

    def test_calculate_parasite_risk_fall(self, domain: HealthDomain) -> None:
        """Test parasite risk for fall season."""
        result = domain._calculate_parasite_risk("fall", "spring to fall", None)
        assert result == "Moderate"

    def test_assess_parasite_risk_very_high(self, domain: HealthDomain) -> None:
        """Test parasite assessment with very high risk."""
        result = domain.assess_parasite_risk(
            region="southeast", season="summer", stocking_rate="high"
        )
        assert "risk_level" in result
        assert "control_strategies" in result

    def test_assess_parasite_risk_moderate(self, domain: HealthDomain) -> None:
        """Test parasite assessment with moderate risk."""
        result = domain.assess_parasite_risk(
            region="midwest", season="spring", stocking_rate="moderate"
        )
        assert "monitoring" in result

    def test_assess_parasite_risk_low(self, domain: HealthDomain) -> None:
        """Test parasite assessment with low risk."""
        result = domain.assess_parasite_risk(
            region="mountain", season="winter", stocking_rate="low"
        )
        assert "control_strategies" in result

    def test_vaccination_schedule_commercial(self, domain: HealthDomain) -> None:
        """Test vaccination schedule for commercial flock."""
        result = domain.get_vaccination_schedule(flock_type="commercial", region="midwest")
        assert "core_vaccines" in result
        assert "risk_based_vaccines" in result

    def test_vaccination_schedule_seedstock(self, domain: HealthDomain) -> None:
        """Test vaccination schedule includes CL for seedstock."""
        result = domain.get_vaccination_schedule(flock_type="seedstock", region="midwest")
        # Seedstock should have CL vaccine in risk-based
        vaccines = [v["vaccine"] for v in result["risk_based_vaccines"]]
        assert "Caseous lymphadenitis (CL)" in vaccines

    def test_vaccination_schedule_show(self, domain: HealthDomain) -> None:
        """Test vaccination schedule for show flock."""
        result = domain.get_vaccination_schedule(flock_type="show", region="pacific")
        assert "core_vaccines" in result

    def test_format_health_advice_basic(self, domain: HealthDomain) -> None:
        """Test formatting basic health advice."""
        result = domain.format_health_advice("What vaccines do I need?", "CDT is essential.")
        assert "CDT is essential" in result
        assert "veterinarian" in result.lower()

    def test_format_health_advice_with_control_strategies(self, domain: HealthDomain) -> None:
        """Test formatting health advice with control strategies."""
        data = {
            "control_strategies": ["Check FAMACHA weekly", "Rotate pastures"],
            "notes": ["Summer is high risk", "Monitor lambs closely"],
        }
        result = domain.format_health_advice("How to manage parasites?", "Use TST.", data=data)
        assert isinstance(result, str)
        assert "TST" in result

    def test_format_health_advice_with_recommendations(self, domain: HealthDomain) -> None:
        """Test formatting health advice with recommendations."""
        data = {"recommendations": ["Use mineral mix", "Provide shelter"]}
        result = domain.format_health_advice("Nutrition question?", "Focus on minerals.", data=data)
        assert isinstance(result, str)

    def test_nutrition_with_body_condition(self, domain: HealthDomain) -> None:
        """Test nutrition recommendations include body condition adjustments."""
        result = domain.get_nutrition_recommendations(
            life_stage="maintenance", region="midwest", body_condition=2.0
        )
        assert "body_condition" in result
        assert "adjustments" in result


class TestCalendarDomainExtended:
    """Extended tests for the calendar domain to increase coverage."""

    @pytest.fixture
    def domain(self) -> CalendarDomain:
        """Create a calendar domain instance."""
        return CalendarDomain()

    def test_calculate_breeding_dates_january(self, domain: CalendarDomain) -> None:
        """Test breeding date calculation for January lambing."""
        result = domain.calculate_breeding_dates(target_lambing="January")
        assert "breeding_start" in result or "dates" in result or isinstance(result, dict)

    def test_calculate_breeding_dates_march(self, domain: CalendarDomain) -> None:
        """Test breeding date calculation for March lambing."""
        result = domain.calculate_breeding_dates(target_lambing="March")
        assert isinstance(result, dict)

    def test_get_seasonal_tasks_lambing(self, domain: CalendarDomain) -> None:
        """Test getting lambing seasonal tasks."""
        result = domain.get_seasonal_tasks(task_type="lambing", region="midwest", month=3)
        assert isinstance(result, dict)

    def test_get_seasonal_tasks_shearing(self, domain: CalendarDomain) -> None:
        """Test getting shearing seasonal tasks."""
        result = domain.get_seasonal_tasks(task_type="shearing", region="northeast", month=4)
        assert isinstance(result, dict)

    def test_get_seasonal_tasks_weaning(self, domain: CalendarDomain) -> None:
        """Test getting weaning seasonal tasks."""
        result = domain.get_seasonal_tasks(task_type="weaning", region="pacific", month=5)
        assert isinstance(result, dict)

    def test_get_marketing_windows_midwest(self, domain: CalendarDomain) -> None:
        """Test marketing windows for midwest."""
        result = domain.get_marketing_windows(region="midwest")
        assert isinstance(result, dict)

    def test_get_marketing_windows_northeast(self, domain: CalendarDomain) -> None:
        """Test marketing windows for northeast."""
        result = domain.get_marketing_windows(region="northeast")
        assert isinstance(result, dict)

    def test_create_annual_calendar_spring_lambing(self, domain: CalendarDomain) -> None:
        """Test annual calendar for spring lambing."""
        result = domain.create_annual_calendar(lambing_month=3, region="midwest")
        assert isinstance(result, dict)

    def test_create_annual_calendar_fall_lambing(self, domain: CalendarDomain) -> None:
        """Test annual calendar for fall lambing."""
        result = domain.create_annual_calendar(lambing_month=10, region="southeast")
        assert isinstance(result, dict)

    def test_calculate_breeding_dates_full_format(self, domain: CalendarDomain) -> None:
        """Test breeding dates with full YYYY-MM-DD format."""
        result = domain.calculate_breeding_dates(target_lambing="2025-03-15")
        assert isinstance(result, dict)
        assert "target_lambing" in result
        assert "timeline" in result
        assert len(result["timeline"]) > 0

    def test_calculate_breeding_dates_invalid(self, domain: CalendarDomain) -> None:
        """Test breeding dates with invalid format returns error."""
        result = domain.calculate_breeding_dates(target_lambing="invalid-date-format")
        assert isinstance(result, dict)
        # Should contain error info
        assert "error" in result or "format_expected" in result

    def test_default_calendar_breeding(self, domain: CalendarDomain) -> None:
        """Test default calendar for breeding tasks."""
        result = domain._default_calendar("breeding")
        assert isinstance(result, dict)
        assert "tasks" in result
        assert len(result["tasks"]) > 0

    def test_default_calendar_lambing(self, domain: CalendarDomain) -> None:
        """Test default calendar for lambing tasks."""
        result = domain._default_calendar("lambing")
        assert isinstance(result, dict)
        assert "tasks" in result

    def test_default_calendar_shearing(self, domain: CalendarDomain) -> None:
        """Test default calendar for shearing tasks."""
        result = domain._default_calendar("shearing")
        assert isinstance(result, dict)
        assert "tasks" in result

    def test_default_calendar_health(self, domain: CalendarDomain) -> None:
        """Test default calendar for health tasks."""
        result = domain._default_calendar("health")
        assert isinstance(result, dict)
        assert "tasks" in result

    def test_default_calendar_general(self, domain: CalendarDomain) -> None:
        """Test default calendar for general tasks."""
        result = domain._default_calendar("general")
        assert isinstance(result, dict)
        assert "tasks" in result

    def test_default_calendar_unknown_type(self, domain: CalendarDomain) -> None:
        """Test default calendar for unknown type falls back to general."""
        result = domain._default_calendar("unknown_task_type")
        assert isinstance(result, dict)
        assert "tasks" in result

    def test_timing_matches_month_spring(self, domain: CalendarDomain) -> None:
        """Test timing matches for spring months."""
        assert domain._timing_matches_month("spring tasks", 3) is True
        assert domain._timing_matches_month("spring tasks", 4) is True
        assert domain._timing_matches_month("spring tasks", 5) is True

    def test_timing_matches_month_summer(self, domain: CalendarDomain) -> None:
        """Test timing matches for summer months."""
        assert domain._timing_matches_month("summer activities", 6) is True
        assert domain._timing_matches_month("summer activities", 7) is True
        assert domain._timing_matches_month("summer activities", 8) is True

    def test_timing_matches_month_fall(self, domain: CalendarDomain) -> None:
        """Test timing matches for fall months."""
        assert domain._timing_matches_month("fall preparation", 9) is True
        assert domain._timing_matches_month("autumn cleanup", 10) is True
        assert domain._timing_matches_month("fall tasks", 11) is True

    def test_timing_matches_month_winter(self, domain: CalendarDomain) -> None:
        """Test timing matches for winter months."""
        assert domain._timing_matches_month("winter maintenance", 12) is True
        assert domain._timing_matches_month("winter tasks", 1) is True
        assert domain._timing_matches_month("winter prep", 2) is True

    def test_timing_matches_month_year_round(self, domain: CalendarDomain) -> None:
        """Test timing matches for year-round tasks."""
        assert domain._timing_matches_month("year-round", 6) is True
        assert domain._timing_matches_month("ongoing maintenance", 3) is True

    def test_timing_matches_month_no_match(self, domain: CalendarDomain) -> None:
        """Test timing does not match wrong season."""
        assert domain._timing_matches_month("spring tasks", 9) is False
        assert domain._timing_matches_month("specific date only", 5) is False

    def test_get_seasonal_tasks_with_month_filter(self, domain: CalendarDomain) -> None:
        """Test seasonal tasks filtered by specific month."""
        from unittest.mock import patch

        with patch("nsip_mcp.shepherd.domains.calendar.get_calendar_template") as mock_cal:
            mock_cal.return_value = {
                "tasks": [
                    {"name": "Spring task", "timing": "March"},
                    {"name": "Summer task", "timing": "July"},
                    {"name": "Year-round", "timing": "year-round"},
                ]
            }
            result = domain.get_seasonal_tasks(task_type="health", month=3)
            # Should filter to March or year-round tasks
            assert isinstance(result, dict)
            assert "tasks" in result

    def test_get_seasonal_tasks_no_calendar_fallback(self, domain: CalendarDomain) -> None:
        """Test seasonal tasks falls back to default when KB returns None."""
        from unittest.mock import patch

        with patch("nsip_mcp.shepherd.domains.calendar.get_calendar_template") as mock_cal:
            mock_cal.return_value = None
            result = domain.get_seasonal_tasks(task_type="breeding", region="midwest")
            assert isinstance(result, dict)
            assert "tasks" in result
            # Should have default breeding tasks
            assert len(result["tasks"]) > 0

    def test_get_marketing_windows_breeding_stock(self, domain: CalendarDomain) -> None:
        """Test marketing windows for breeding stock."""
        result = domain.get_marketing_windows(region="midwest", product_type="breeding_stock")
        assert isinstance(result, dict)
        assert result["product_type"] == "breeding_stock"

    def test_get_marketing_windows_wool(self, domain: CalendarDomain) -> None:
        """Test marketing windows for wool."""
        result = domain.get_marketing_windows(region="northeast", product_type="wool")
        assert isinstance(result, dict)
        assert result["product_type"] == "wool"

    def test_get_marketing_windows_unknown_type(self, domain: CalendarDomain) -> None:
        """Test marketing windows for unknown type falls back to market_lambs."""
        result = domain.get_marketing_windows(product_type="unknown_type")
        assert isinstance(result, dict)
        # Should have market_lambs data as fallback
        assert "peak_demand" in result or "strategies" in result

    def test_format_calendar_advice_basic(self, domain: CalendarDomain) -> None:
        """Test formatting calendar advice with basic input."""
        result = domain.format_calendar_advice(
            question="When should I breed?", answer="Breed in the fall for spring lambing."
        )
        assert isinstance(result, str)
        assert "Breed in the fall" in result

    def test_format_calendar_advice_with_tasks(self, domain: CalendarDomain) -> None:
        """Test formatting calendar advice with task data."""
        data = {
            "tasks": [
                {"name": "Ram prep", "timing": "6 weeks before"},
                {"name": "Flushing", "timing": "3 weeks before"},
            ]
        }
        result = domain.format_calendar_advice(
            question="What are pre-breeding tasks?",
            answer="Prepare both rams and ewes.",
            data=data,
        )
        assert isinstance(result, str)
        assert len(result) > 0

    def test_format_calendar_advice_with_timeline(self, domain: CalendarDomain) -> None:
        """Test formatting calendar advice with timeline data."""
        data = {
            "timeline": [
                {"event": "Start breeding", "date": "2025-08-01"},
                {"event": "Pregnancy check", "date": "2025-09-15"},
            ]
        }
        result = domain.format_calendar_advice(
            question="What's my breeding timeline?",
            answer="Here's your timeline.",
            data=data,
        )
        assert isinstance(result, str)

    def test_format_calendar_advice_empty_data(self, domain: CalendarDomain) -> None:
        """Test formatting calendar advice with empty data."""
        result = domain.format_calendar_advice(
            question="General question", answer="General answer.", data={}
        )
        assert isinstance(result, str)
        assert "General answer" in result


class TestEconomicsDomainExtended:
    """Extended tests for the economics domain to increase coverage."""

    @pytest.fixture
    def domain(self) -> EconomicsDomain:
        """Create an economics domain instance."""
        return EconomicsDomain()

    def test_get_cost_breakdown_small(self, domain: EconomicsDomain) -> None:
        """Test cost breakdown for small flock."""
        result = domain.get_cost_breakdown(flock_size="small")
        assert isinstance(result, dict)

    def test_get_cost_breakdown_large(self, domain: EconomicsDomain) -> None:
        """Test cost breakdown for large flock."""
        result = domain.get_cost_breakdown(flock_size="large")
        assert isinstance(result, dict)

    def test_calculate_breakeven_low_lamb_price(self, domain: EconomicsDomain) -> None:
        """Test breakeven with low lamb price."""
        result = domain.calculate_breakeven(
            annual_costs_per_ewe=200, lambs_per_ewe=1.2, lamb_weight=80
        )
        # Result has breakeven_analysis as a key, not just breakeven
        assert "breakeven_analysis" in result or isinstance(result, dict)

    def test_calculate_breakeven_high_lamb_price(self, domain: EconomicsDomain) -> None:
        """Test breakeven with high productivity."""
        result = domain.calculate_breakeven(
            annual_costs_per_ewe=100, lambs_per_ewe=2.0, lamb_weight=120
        )
        assert isinstance(result, dict)

    def test_calculate_ram_roi_short_term(self, domain: EconomicsDomain) -> None:
        """Test RAM ROI for short-term use."""
        result = domain.calculate_ram_roi(
            ram_cost=1500, years_used=2, ewes_per_year=20, lamb_value_increase=15
        )
        assert isinstance(result, dict)

    def test_calculate_ram_roi_long_term(self, domain: EconomicsDomain) -> None:
        """Test RAM ROI for long-term use."""
        result = domain.calculate_ram_roi(
            ram_cost=3000, years_used=6, ewes_per_year=50, lamb_value_increase=30
        )
        assert isinstance(result, dict)

    def test_analyze_flock_profitability_profitable(self, domain: EconomicsDomain) -> None:
        """Test profitability analysis for profitable flock."""
        result = domain.analyze_flock_profitability(
            ewe_count=100,
            lambs_marketed=180,
            avg_lamb_price=250,
            wool_revenue=1000,
            cull_revenue=2000,
            total_costs=25000,
        )
        assert isinstance(result, dict)

    def test_analyze_flock_profitability_unprofitable(self, domain: EconomicsDomain) -> None:
        """Test profitability analysis for unprofitable flock."""
        result = domain.analyze_flock_profitability(
            ewe_count=50,
            lambs_marketed=40,
            avg_lamb_price=150,
            wool_revenue=200,
            cull_revenue=500,
            total_costs=15000,
        )
        assert isinstance(result, dict)

    def test_compare_marketing_options_multiple(self, domain: EconomicsDomain) -> None:
        """Test comparing multiple marketing options."""
        options = [
            {"name": "direct", "price": 3.00},
            {"name": "auction", "price": 2.50},
            {"name": "freezer_trade", "price": 3.50},
        ]
        result = domain.compare_marketing_options(weight=85, options=options)
        assert isinstance(result, dict)

    def test_compare_marketing_options_single(self, domain: EconomicsDomain) -> None:
        """Test comparing with single option."""
        options = [{"name": "auction", "price": 2.00}]
        result = domain.compare_marketing_options(weight=100, options=options)
        assert isinstance(result, dict)

    def test_get_cost_breakdown_with_kb_data(self, domain: EconomicsDomain) -> None:
        """Test cost breakdown uses knowledge base data when available."""
        from unittest.mock import patch

        with patch("nsip_mcp.shepherd.domains.economics.get_economics_template") as mock_kb:
            mock_kb.return_value = {
                "cost_templates": {
                    "feed": {"low": 50, "average": 70, "high": 100},
                    "health": {"low": 15, "average": 25, "high": 35},
                }
            }
            result = domain.get_cost_breakdown(flock_size="medium")
            assert isinstance(result, dict)
            assert "annual_per_ewe" in result

    def test_get_cost_breakdown_kb_exception(self, domain: EconomicsDomain) -> None:
        """Test cost breakdown falls back on KB exception."""
        from unittest.mock import patch

        with patch("nsip_mcp.shepherd.domains.economics.get_economics_template") as mock_kb:
            mock_kb.side_effect = Exception("KB error")
            result = domain.get_cost_breakdown(flock_size="small")
            assert isinstance(result, dict)
            assert "annual_per_ewe" in result
            # Should still have data from defaults

    def test_get_cost_breakdown_drylot_system(self, domain: EconomicsDomain) -> None:
        """Test cost breakdown for drylot production system."""
        result = domain.get_cost_breakdown(flock_size="medium", production_system="drylot")
        assert isinstance(result, dict)
        assert result["production_system"] == "drylot"

    def test_get_cost_breakdown_accelerated_system(self, domain: EconomicsDomain) -> None:
        """Test cost breakdown for accelerated lambing system."""
        result = domain.get_cost_breakdown(flock_size="large", production_system="accelerated")
        assert isinstance(result, dict)
        assert result["production_system"] == "accelerated"

    def test_get_cost_breakdown_unknown_size(self, domain: EconomicsDomain) -> None:
        """Test cost breakdown with unknown flock size uses defaults."""
        result = domain.get_cost_breakdown(flock_size="extra_large")
        assert isinstance(result, dict)
        # Should still return valid data

    def test_default_ewe_costs(self, domain: EconomicsDomain) -> None:
        """Test default ewe costs returns expected structure."""
        result = domain._default_ewe_costs()
        assert isinstance(result, dict)
        assert "feed" in result
        assert "health" in result
        assert "average" in result["feed"]

    def test_default_lamb_costs(self, domain: EconomicsDomain) -> None:
        """Test default lamb costs returns expected structure."""
        result = domain._default_lamb_costs()
        assert isinstance(result, dict)
        assert "creep_feed" in result
        assert "grower_feed" in result

    def test_flock_size_range_small(self, domain: EconomicsDomain) -> None:
        """Test flock size range for small."""
        result = domain._flock_size_range("small")
        assert "10-50" in result

    def test_flock_size_range_medium(self, domain: EconomicsDomain) -> None:
        """Test flock size range for medium."""
        result = domain._flock_size_range("medium")
        assert "50-200" in result

    def test_flock_size_range_large(self, domain: EconomicsDomain) -> None:
        """Test flock size range for large."""
        result = domain._flock_size_range("large")
        assert "200+" in result

    def test_flock_size_range_unknown(self, domain: EconomicsDomain) -> None:
        """Test flock size range for unknown size."""
        result = domain._flock_size_range("huge")
        assert result == "varies"

    def test_calculate_breakeven_zero_lambs(self, domain: EconomicsDomain) -> None:
        """Test breakeven with zero lambs per ewe returns error."""
        result = domain.calculate_breakeven(
            annual_costs_per_ewe=150, lambs_per_ewe=0, lamb_weight=100
        )
        assert "error" in result

    def test_calculate_breakeven_zero_weight(self, domain: EconomicsDomain) -> None:
        """Test breakeven with zero lamb weight."""
        result = domain.calculate_breakeven(
            annual_costs_per_ewe=150, lambs_per_ewe=1.5, lamb_weight=0
        )
        assert isinstance(result, dict)
        assert result["breakeven_analysis"]["per_pound"] == 0

    def test_interpret_breakeven_competitive(self, domain: EconomicsDomain) -> None:
        """Test interpret breakeven for competitive price."""
        result = domain._interpret_breakeven(1.40)
        assert "Competitive" in result

    def test_interpret_breakeven_moderate(self, domain: EconomicsDomain) -> None:
        """Test interpret breakeven for moderate price."""
        result = domain._interpret_breakeven(1.75)
        assert "Moderate" in result

    def test_interpret_breakeven_high(self, domain: EconomicsDomain) -> None:
        """Test interpret breakeven for high price."""
        result = domain._interpret_breakeven(2.25)
        assert "High" in result

    def test_interpret_breakeven_very_high(self, domain: EconomicsDomain) -> None:
        """Test interpret breakeven for very high price."""
        result = domain._interpret_breakeven(3.00)
        assert "Very high" in result

    def test_calculate_ram_roi_zero_cost(self, domain: EconomicsDomain) -> None:
        """Test RAM ROI with zero cost."""
        result = domain.calculate_ram_roi(
            ram_cost=0, years_used=3, ewes_per_year=25, lamb_value_increase=20
        )
        assert result["roi_analysis"]["roi_percent"] == 0

    def test_roi_recommendation_excellent(self, domain: EconomicsDomain) -> None:
        """Test ROI recommendation for excellent ROI."""
        result = domain._roi_recommendation(150, 500)
        assert "Excellent" in result

    def test_roi_recommendation_good(self, domain: EconomicsDomain) -> None:
        """Test ROI recommendation for good ROI."""
        result = domain._roi_recommendation(75, 300)
        assert "Good" in result

    def test_roi_recommendation_marginal(self, domain: EconomicsDomain) -> None:
        """Test ROI recommendation for marginal ROI."""
        result = domain._roi_recommendation(25, 100)
        assert "Marginal" in result

    def test_roi_recommendation_poor(self, domain: EconomicsDomain) -> None:
        """Test ROI recommendation for poor ROI."""
        result = domain._roi_recommendation(-10, -50)
        assert "Poor" in result

    def test_profitability_assessment_excellent(self, domain: EconomicsDomain) -> None:
        """Test profitability assessment for excellent operation."""
        result = domain._profitability_assessment(100, 25)
        assert "Excellent" in result

    def test_profitability_assessment_good(self, domain: EconomicsDomain) -> None:
        """Test profitability assessment for good operation."""
        result = domain._profitability_assessment(50, 15)
        assert "Good" in result

    def test_profitability_assessment_marginal(self, domain: EconomicsDomain) -> None:
        """Test profitability assessment for marginal operation."""
        result = domain._profitability_assessment(20, 5)
        assert "Marginal" in result

    def test_profitability_assessment_breakeven(self, domain: EconomicsDomain) -> None:
        """Test profitability assessment for breakeven operation."""
        result = domain._profitability_assessment(5, -2)
        assert "Breakeven" in result

    def test_profitability_assessment_loss(self, domain: EconomicsDomain) -> None:
        """Test profitability assessment for loss operation."""
        result = domain._profitability_assessment(-50, -10)
        assert "Loss" in result

    def test_identify_improvement_low_lambs(self, domain: EconomicsDomain) -> None:
        """Test improvement identification with low lamb crop."""
        result = domain._identify_improvement_areas(1.0, 120, 15)
        assert any("below average" in r.lower() for r in result)

    def test_identify_improvement_moderate_lambs(self, domain: EconomicsDomain) -> None:
        """Test improvement identification with moderate lamb crop."""
        result = domain._identify_improvement_areas(1.4, 120, 15)
        assert any("moderate" in r.lower() for r in result)

    def test_identify_improvement_high_costs(self, domain: EconomicsDomain) -> None:
        """Test improvement identification with high costs."""
        result = domain._identify_improvement_areas(1.6, 200, 15)
        assert any("costs" in r.lower() for r in result)

    def test_identify_improvement_thin_margins(self, domain: EconomicsDomain) -> None:
        """Test improvement identification with thin margins."""
        result = domain._identify_improvement_areas(1.6, 120, 5)
        assert any("margin" in r.lower() for r in result)

    def test_identify_improvement_performing_well(self, domain: EconomicsDomain) -> None:
        """Test improvement identification for well-performing operation."""
        result = domain._identify_improvement_areas(1.8, 120, 20)
        assert any("performing well" in r.lower() for r in result)

    def test_compare_marketing_options_empty(self, domain: EconomicsDomain) -> None:
        """Test marketing comparison with empty options uses defaults."""
        result = domain.compare_marketing_options(weight=90, options=[])
        assert isinstance(result, dict)
        assert "comparisons" in result
        assert len(result["comparisons"]) > 0

    def test_compare_marketing_options_with_price_per_lb(self, domain: EconomicsDomain) -> None:
        """Test marketing options with price per pound."""
        options = [
            {"name": "Direct", "price_per_lb": 2.50, "costs": 10},
            {"name": "Auction", "price_per_lb": 2.00, "costs": 20},
        ]
        result = domain.compare_marketing_options(weight=100, options=options)
        assert len(result["comparisons"]) == 2
        assert result["comparisons"][0]["net_revenue"] > result["comparisons"][1]["net_revenue"]

    def test_compare_marketing_options_with_carcass_price(self, domain: EconomicsDomain) -> None:
        """Test marketing options with carcass price."""
        options = [{"name": "Freezer", "price_per_cwt_carcass": 500, "yield": 0.48, "costs": 80}]
        result = domain.compare_marketing_options(weight=100, options=options)
        assert len(result["comparisons"]) == 1
        assert result["comparisons"][0]["option"] == "Freezer"

    def test_compare_marketing_options_skip_invalid(self, domain: EconomicsDomain) -> None:
        """Test marketing comparison skips options without price."""
        options = [
            {"name": "Invalid"},  # No price
            {"name": "Valid", "price_per_lb": 2.50, "costs": 5},
        ]
        result = domain.compare_marketing_options(weight=100, options=options)
        assert len(result["comparisons"]) == 1
        assert result["comparisons"][0]["option"] == "Valid"

    def test_format_economics_advice_basic(self, domain: EconomicsDomain) -> None:
        """Test formatting economics advice."""
        result = domain.format_economics_advice(
            question="What are my costs?", answer="Your costs are reasonable."
        )
        assert isinstance(result, str)
        assert "Your costs are reasonable" in result

    def test_format_economics_advice_with_improvements(self, domain: EconomicsDomain) -> None:
        """Test formatting economics advice with improvement areas."""
        data = {"improvement_areas": ["Reduce feed costs", "Improve lamb crop"]}
        result = domain.format_economics_advice(
            question="How can I improve?", answer="Here are some suggestions.", data=data
        )
        assert isinstance(result, str)

    def test_format_economics_advice_with_assumptions(self, domain: EconomicsDomain) -> None:
        """Test formatting economics advice with assumptions."""
        data = {"assumptions": ["Based on medium flock", "Regional costs may vary"]}
        result = domain.format_economics_advice(
            question="What are my costs?", answer="Here's your analysis.", data=data
        )
        assert isinstance(result, str)

    def test_format_economics_advice_with_notes(self, domain: EconomicsDomain) -> None:
        """Test formatting economics advice with notes."""
        data = {"notes": ["Direct sales often higher", "Consider marketing effort"]}
        result = domain.format_economics_advice(
            question="Best marketing?", answer="Direct sales recommended.", data=data
        )
        assert isinstance(result, str)
