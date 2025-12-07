"""Unit tests for knowledge base schema module.

Tests for dataclasses and enums used in knowledge base validation.
"""

from nsip_mcp.knowledge_base.schema.kb_schema import (
    CalendarTask,
    Climate,
    DiseaseInfo,
    EconomicsCategory,
    LifeStageNutrition,
    RegionInfo,
    RiskLevel,
    SelectionIndex,
    TraitCategory,
    TraitInfo,
    TraitInterpretation,
)


class TestTraitCategoryEnum:
    """Tests for TraitCategory enum."""

    def test_growth_category(self) -> None:
        """Test GROWTH category value."""
        assert TraitCategory.GROWTH == "growth"
        assert TraitCategory.GROWTH.value == "growth"

    def test_maternal_category(self) -> None:
        """Test MATERNAL category value."""
        assert TraitCategory.MATERNAL == "maternal"
        assert TraitCategory.MATERNAL.value == "maternal"

    def test_carcass_category(self) -> None:
        """Test CARCASS category value."""
        assert TraitCategory.CARCASS == "carcass"
        assert TraitCategory.CARCASS.value == "carcass"

    def test_health_category(self) -> None:
        """Test HEALTH category value."""
        assert TraitCategory.HEALTH == "health"
        assert TraitCategory.HEALTH.value == "health"

    def test_wool_category(self) -> None:
        """Test WOOL category value."""
        assert TraitCategory.WOOL == "wool"
        assert TraitCategory.WOOL.value == "wool"

    def test_all_categories_accessible(self) -> None:
        """Test all categories can be iterated."""
        categories = list(TraitCategory)
        assert len(categories) == 5
        assert TraitCategory.GROWTH in categories


class TestTraitInterpretationEnum:
    """Tests for TraitInterpretation enum."""

    def test_higher_better(self) -> None:
        """Test HIGHER_BETTER interpretation."""
        assert TraitInterpretation.HIGHER_BETTER == "higher_better"
        assert TraitInterpretation.HIGHER_BETTER.value == "higher_better"

    def test_lower_better(self) -> None:
        """Test LOWER_BETTER interpretation."""
        assert TraitInterpretation.LOWER_BETTER == "lower_better"
        assert TraitInterpretation.LOWER_BETTER.value == "lower_better"


class TestRiskLevelEnum:
    """Tests for RiskLevel enum."""

    def test_low_risk(self) -> None:
        """Test LOW risk level."""
        assert RiskLevel.LOW == "low"
        assert RiskLevel.LOW.value == "low"

    def test_moderate_risk(self) -> None:
        """Test MODERATE risk level."""
        assert RiskLevel.MODERATE == "moderate"

    def test_high_risk(self) -> None:
        """Test HIGH risk level."""
        assert RiskLevel.HIGH == "high"

    def test_very_high_risk(self) -> None:
        """Test VERY_HIGH risk level."""
        assert RiskLevel.VERY_HIGH == "very_high"

    def test_unknown_risk(self) -> None:
        """Test UNKNOWN risk level."""
        assert RiskLevel.UNKNOWN == "unknown"


class TestClimateEnum:
    """Tests for Climate enum."""

    def test_humid_continental(self) -> None:
        """Test HUMID_CONTINENTAL climate."""
        assert Climate.HUMID_CONTINENTAL == "humid_continental"

    def test_humid_subtropical(self) -> None:
        """Test HUMID_SUBTROPICAL climate."""
        assert Climate.HUMID_SUBTROPICAL == "humid_subtropical"

    def test_continental(self) -> None:
        """Test CONTINENTAL climate."""
        assert Climate.CONTINENTAL == "continental"

    def test_semi_arid(self) -> None:
        """Test SEMI_ARID climate."""
        assert Climate.SEMI_ARID == "semi_arid"

    def test_alpine_semi_arid(self) -> None:
        """Test ALPINE_SEMI_ARID climate."""
        assert Climate.ALPINE_SEMI_ARID == "alpine_semi_arid"

    def test_varied(self) -> None:
        """Test VARIED climate."""
        assert Climate.VARIED == "varied"


class TestTraitInfo:
    """Tests for TraitInfo dataclass."""

    def test_create_trait_info(self) -> None:
        """Test creating a TraitInfo instance."""
        trait = TraitInfo(
            code="WWT",
            name="Weaning Weight",
            description="Weight at weaning",
            unit="kg",
            interpretation=TraitInterpretation.HIGHER_BETTER,
            category=TraitCategory.GROWTH,
        )
        assert trait.code == "WWT"
        assert trait.name == "Weaning Weight"
        assert trait.description == "Weight at weaning"
        assert trait.unit == "kg"
        assert trait.interpretation == TraitInterpretation.HIGHER_BETTER
        assert trait.category == TraitCategory.GROWTH
        assert trait.heritability_range == (0.0, 1.0)

    def test_trait_info_custom_heritability(self) -> None:
        """Test TraitInfo with custom heritability range."""
        trait = TraitInfo(
            code="BWT",
            name="Birth Weight",
            description="Weight at birth",
            unit="kg",
            interpretation=TraitInterpretation.LOWER_BETTER,
            category=TraitCategory.MATERNAL,
            heritability_range=(0.25, 0.35),
        )
        assert trait.heritability_range == (0.25, 0.35)

    def test_trait_info_to_dict(self) -> None:
        """Test TraitInfo.to_dict() method."""
        trait = TraitInfo(
            code="NLW",
            name="Number of Lambs Weaned",
            description="Lambs weaned per ewe",
            unit="count",
            interpretation=TraitInterpretation.HIGHER_BETTER,
            category=TraitCategory.MATERNAL,
            heritability_range=(0.10, 0.15),
        )
        result = trait.to_dict()

        assert result["code"] == "NLW"
        assert result["name"] == "Number of Lambs Weaned"
        assert result["description"] == "Lambs weaned per ewe"
        assert result["unit"] == "count"
        assert result["interpretation"] == "higher_better"
        assert result["category"] == "maternal"
        assert result["heritability_range"] == [0.10, 0.15]


class TestSelectionIndex:
    """Tests for SelectionIndex dataclass."""

    def test_create_selection_index(self) -> None:
        """Test creating a SelectionIndex instance."""
        index = SelectionIndex(
            name="Terminal Sire Index",
            description="Index for terminal sire selection",
            weights={"PWWT": 0.5, "PFAT": -0.3, "PEMD": 0.2},
            use_case="Terminal sire selection for meat production",
        )
        assert index.name == "Terminal Sire Index"
        assert index.description == "Index for terminal sire selection"
        assert index.weights == {"PWWT": 0.5, "PFAT": -0.3, "PEMD": 0.2}
        assert index.use_case == "Terminal sire selection for meat production"
        assert index.breed_focus == []

    def test_selection_index_with_breed_focus(self) -> None:
        """Test SelectionIndex with breed_focus."""
        index = SelectionIndex(
            name="Hair Sheep Index",
            description="Index for hair sheep",
            weights={"WWT": 0.4, "FEC": -0.3, "NLW": 0.3},
            use_case="Selection for parasite resistance",
            breed_focus=["Katahdin", "St. Croix", "Barbados Blackbelly"],
        )
        assert len(index.breed_focus) == 3
        assert "Katahdin" in index.breed_focus

    def test_selection_index_to_dict(self) -> None:
        """Test SelectionIndex.to_dict() method."""
        index = SelectionIndex(
            name="Maternal Index",
            description="Maternal trait selection",
            weights={"NLW": 0.5, "MWWT": 0.3, "BWT": -0.2},
            use_case="Ewe selection",
            breed_focus=["Polypay", "Finnsheep"],
        )
        result = index.to_dict()

        assert result["name"] == "Maternal Index"
        assert result["description"] == "Maternal trait selection"
        assert result["weights"] == {"NLW": 0.5, "MWWT": 0.3, "BWT": -0.2}
        assert result["use_case"] == "Ewe selection"
        assert result["breed_focus"] == ["Polypay", "Finnsheep"]


class TestRegionInfo:
    """Tests for RegionInfo dataclass."""

    def test_create_region_info(self) -> None:
        """Test creating a RegionInfo instance."""
        region = RegionInfo(
            name="Midwest",
            states=["OH", "IN", "IL", "MI", "WI"],
            climate=Climate.CONTINENTAL,
            primary_breeds=["Suffolk", "Hampshire", "Dorset"],
            lambing_season="February-April",
        )
        assert region.name == "Midwest"
        assert len(region.states) == 5
        assert region.climate == Climate.CONTINENTAL
        assert len(region.primary_breeds) == 3
        assert region.lambing_season == "February-April"
        assert region.challenges == []

    def test_region_info_with_challenges(self) -> None:
        """Test RegionInfo with challenges."""
        region = RegionInfo(
            name="Southeast",
            states=["GA", "FL", "SC"],
            climate=Climate.HUMID_SUBTROPICAL,
            primary_breeds=["Katahdin", "St. Croix"],
            lambing_season="January-March",
            challenges=["High parasite pressure", "Heat stress", "Humidity"],
        )
        assert len(region.challenges) == 3
        assert "High parasite pressure" in region.challenges

    def test_region_info_to_dict(self) -> None:
        """Test RegionInfo.to_dict() method."""
        region = RegionInfo(
            name="Mountain West",
            states=["CO", "WY", "MT"],
            climate=Climate.ALPINE_SEMI_ARID,
            primary_breeds=["Rambouillet", "Targhee"],
            lambing_season="April-May",
            challenges=["Predators", "Altitude"],
        )
        result = region.to_dict()

        assert result["name"] == "Mountain West"
        assert result["states"] == ["CO", "WY", "MT"]
        assert result["climate"] == "alpine_semi_arid"
        assert result["primary_breeds"] == ["Rambouillet", "Targhee"]
        assert result["lambing_season"] == "April-May"
        assert result["challenges"] == ["Predators", "Altitude"]


class TestDiseaseInfo:
    """Tests for DiseaseInfo dataclass."""

    def test_create_disease_info(self) -> None:
        """Test creating a DiseaseInfo instance."""
        disease = DiseaseInfo(
            name="Footrot",
            description="Bacterial infection of the hoof",
            prevention=["Dry conditions", "Footbaths", "Culling carriers"],
            treatment="Zinc sulfate footbath and antibiotics",
            regional_risk={
                "midwest": RiskLevel.MODERATE,
                "southeast": RiskLevel.HIGH,
                "mountain": RiskLevel.LOW,
            },
        )
        assert disease.name == "Footrot"
        assert disease.description == "Bacterial infection of the hoof"
        assert len(disease.prevention) == 3
        assert disease.treatment == "Zinc sulfate footbath and antibiotics"
        assert disease.regional_risk["midwest"] == RiskLevel.MODERATE
        assert disease.regional_risk["southeast"] == RiskLevel.HIGH

    def test_disease_info_to_dict(self) -> None:
        """Test DiseaseInfo.to_dict() method."""
        disease = DiseaseInfo(
            name="Caseous Lymphadenitis (CL)",
            description="Chronic abscess disease",
            prevention=["Closed flock", "Vaccination"],
            treatment="None (manage abscesses)",
            regional_risk={
                "pacific": RiskLevel.MODERATE,
                "southwest": RiskLevel.HIGH,
            },
        )
        result = disease.to_dict()

        assert result["name"] == "Caseous Lymphadenitis (CL)"
        assert result["description"] == "Chronic abscess disease"
        assert result["prevention"] == ["Closed flock", "Vaccination"]
        assert result["treatment"] == "None (manage abscesses)"
        assert result["regional_risk"]["pacific"] == "moderate"
        assert result["regional_risk"]["southwest"] == "high"


class TestLifeStageNutrition:
    """Tests for LifeStageNutrition dataclass."""

    def test_create_life_stage_nutrition(self) -> None:
        """Test creating a LifeStageNutrition instance."""
        nutrition = LifeStageNutrition(
            name="Late Gestation",
            description="Final 6 weeks of pregnancy",
            timing="Weeks 15-21 of gestation",
            protein_percent="14-16%",
            energy_adjustment="+25%",
        )
        assert nutrition.name == "Late Gestation"
        assert nutrition.description == "Final 6 weeks of pregnancy"
        assert nutrition.timing == "Weeks 15-21 of gestation"
        assert nutrition.protein_percent == "14-16%"
        assert nutrition.energy_adjustment == "+25%"
        assert nutrition.critical_nutrients == []
        assert nutrition.notes == ""

    def test_life_stage_nutrition_full(self) -> None:
        """Test LifeStageNutrition with all optional fields."""
        nutrition = LifeStageNutrition(
            name="Lactation - Early",
            description="First 8 weeks of lactation",
            timing="Weeks 1-8 post-lambing",
            protein_percent="16-18%",
            energy_adjustment="+50%",
            critical_nutrients=["Calcium", "Phosphorus", "Selenium"],
            notes="Monitor body condition closely",
        )
        assert len(nutrition.critical_nutrients) == 3
        assert "Selenium" in nutrition.critical_nutrients
        assert nutrition.notes == "Monitor body condition closely"

    def test_life_stage_nutrition_to_dict(self) -> None:
        """Test LifeStageNutrition.to_dict() method."""
        nutrition = LifeStageNutrition(
            name="Maintenance",
            description="Non-breeding ewes",
            timing="Year-round",
            protein_percent="10-12%",
            energy_adjustment="0%",
            critical_nutrients=["Salt", "Minerals"],
            notes="Adjust for body condition",
        )
        result = nutrition.to_dict()

        assert result["name"] == "Maintenance"
        assert result["description"] == "Non-breeding ewes"
        assert result["timing"] == "Year-round"
        assert result["protein_percent"] == "10-12%"
        assert result["energy_adjustment"] == "0%"
        assert result["critical_nutrients"] == ["Salt", "Minerals"]
        assert result["notes"] == "Adjust for body condition"


class TestCalendarTask:
    """Tests for CalendarTask dataclass."""

    def test_create_calendar_task(self) -> None:
        """Test creating a CalendarTask instance."""
        task = CalendarTask(
            name="Shearing",
            description="Annual fleece removal",
            timing="Spring (March-April)",
            category="husbandry",
        )
        assert task.name == "Shearing"
        assert task.description == "Annual fleece removal"
        assert task.timing == "Spring (March-April)"
        assert task.category == "husbandry"
        assert task.priority == "normal"
        assert task.region_specific is False

    def test_calendar_task_high_priority(self) -> None:
        """Test CalendarTask with high priority."""
        task = CalendarTask(
            name="Ram turnout",
            description="Introduce rams to ewes",
            timing="Fall (October-November)",
            category="breeding",
            priority="high",
            region_specific=True,
        )
        assert task.priority == "high"
        assert task.region_specific is True

    def test_calendar_task_to_dict(self) -> None:
        """Test CalendarTask.to_dict() method."""
        task = CalendarTask(
            name="Vaccination - CDT",
            description="Clostridial disease vaccination",
            timing="Pre-breeding and pre-lambing",
            category="health",
            priority="high",
            region_specific=False,
        )
        result = task.to_dict()

        assert result["name"] == "Vaccination - CDT"
        assert result["description"] == "Clostridial disease vaccination"
        assert result["timing"] == "Pre-breeding and pre-lambing"
        assert result["category"] == "health"
        assert result["priority"] == "high"
        assert result["region_specific"] is False


class TestEconomicsCategory:
    """Tests for EconomicsCategory dataclass."""

    def test_create_economics_category(self) -> None:
        """Test creating an EconomicsCategory instance."""
        category = EconomicsCategory(
            name="Cost Per Ewe",
            description="Annual cost to maintain one ewe",
            variables=["feed_cost", "vet_cost", "labor_cost", "overhead"],
            formula="sum(feed_cost + vet_cost + labor_cost + overhead)",
        )
        assert category.name == "Cost Per Ewe"
        assert category.description == "Annual cost to maintain one ewe"
        assert len(category.variables) == 4
        assert "feed_cost" in category.variables
        assert category.formula == "sum(feed_cost + vet_cost + labor_cost + overhead)"
        assert category.notes == ""

    def test_economics_category_with_notes(self) -> None:
        """Test EconomicsCategory with notes."""
        category = EconomicsCategory(
            name="Breakeven Price",
            description="Price needed to cover costs",
            variables=["total_cost", "lambs_sold"],
            formula="total_cost / lambs_sold",
            notes="Adjust for market weight targets",
        )
        assert category.notes == "Adjust for market weight targets"

    def test_economics_category_to_dict(self) -> None:
        """Test EconomicsCategory.to_dict() method."""
        category = EconomicsCategory(
            name="Ram ROI",
            description="Return on investment for ram purchase",
            variables=["ram_cost", "lambs_sired", "lamb_premium"],
            formula="(lambs_sired * lamb_premium - ram_cost) / ram_cost * 100",
            notes="Calculate over breeding lifespan",
        )
        result = category.to_dict()

        assert result["name"] == "Ram ROI"
        assert result["description"] == "Return on investment for ram purchase"
        assert result["variables"] == ["ram_cost", "lambs_sired", "lamb_premium"]
        assert result["formula"] == "(lambs_sired * lamb_premium - ram_cost) / ram_cost * 100"
        assert result["notes"] == "Calculate over breeding lifespan"
