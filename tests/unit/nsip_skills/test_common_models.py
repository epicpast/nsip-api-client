"""
Unit tests for nsip_skills.common.data_models

Tests:
- Dataclass instantiation and default values
- Enum member validation
- to_dict serialization methods
- SelectionIndex score calculation
- Preset index definitions

Target: >80% coverage
"""

from nsip_skills.common.data_models import (
    HAIR_INDEX,
    MATERNAL_INDEX,
    PRESET_INDEXES,
    RANGE_INDEX,
    TERMINAL_INDEX,
    AnimalAnalysis,
    BreedingGoal,
    FlockSummary,
    InbreedingResult,
    MatingPair,
    PedigreeNode,
    PedigreeTree,
    RiskLevel,
    SelectionIndex,
    TraitProfile,
    TraitValue,
)


class TestRiskLevel:
    """Tests for RiskLevel enum."""

    def test_risk_levels_exist(self):
        """Verify all risk levels are defined."""
        assert RiskLevel.LOW.value == "low"
        assert RiskLevel.MODERATE.value == "moderate"
        assert RiskLevel.HIGH.value == "high"

    def test_risk_level_from_coefficient_low(self):
        """Verify low risk threshold (<6.25%)."""
        assert RiskLevel.from_coefficient(0.0) == RiskLevel.LOW
        assert RiskLevel.from_coefficient(0.05) == RiskLevel.LOW
        assert RiskLevel.from_coefficient(0.0624) == RiskLevel.LOW

    def test_risk_level_from_coefficient_moderate(self):
        """Verify moderate risk threshold (6.25-12.5%)."""
        assert RiskLevel.from_coefficient(0.0625) == RiskLevel.MODERATE
        assert RiskLevel.from_coefficient(0.10) == RiskLevel.MODERATE
        assert RiskLevel.from_coefficient(0.124) == RiskLevel.MODERATE

    def test_risk_level_from_coefficient_high(self):
        """Verify high risk threshold (>12.5%)."""
        assert RiskLevel.from_coefficient(0.125) == RiskLevel.HIGH
        assert RiskLevel.from_coefficient(0.20) == RiskLevel.HIGH
        assert RiskLevel.from_coefficient(0.50) == RiskLevel.HIGH


class TestBreedingGoal:
    """Tests for BreedingGoal enum."""

    def test_breeding_goals_exist(self):
        """Verify all breeding goals are defined."""
        assert BreedingGoal.TERMINAL.value == "terminal"
        assert BreedingGoal.MATERNAL.value == "maternal"
        assert BreedingGoal.BALANCED.value == "balanced"
        assert BreedingGoal.CUSTOM.value == "custom"


class TestTraitValue:
    """Tests for TraitValue dataclass."""

    def test_basic_creation(self):
        """Verify basic trait value creation."""
        tv = TraitValue(name="BWT", value=0.5)
        assert tv.name == "BWT"
        assert tv.value == 0.5
        assert tv.accuracy is None
        assert tv.percentile is None

    def test_full_creation(self):
        """Verify trait value with all fields."""
        tv = TraitValue(name="WWT", value=2.5, accuracy=0.75, percentile=85.0)
        assert tv.accuracy == 0.75
        assert tv.percentile == 85.0

    def test_to_dict(self):
        """Verify dict serialization."""
        tv = TraitValue(name="PWWT", value=3.0, accuracy=0.6)
        d = tv.to_dict()

        assert d["name"] == "PWWT"
        assert d["value"] == 3.0
        assert d["accuracy"] == 0.6
        assert d["percentile"] is None


class TestTraitProfile:
    """Tests for TraitProfile dataclass."""

    def test_creation_with_traits(self):
        """Verify profile creation with trait dictionary."""
        traits = {
            "BWT": TraitValue(name="BWT", value=0.5),
            "WWT": TraitValue(name="WWT", value=2.0),
        }
        profile = TraitProfile(lpn_id="TEST123", breed="Suffolk", traits=traits)

        assert profile.lpn_id == "TEST123"
        assert profile.breed == "Suffolk"
        assert len(profile.traits) == 2
        assert profile.traits["BWT"].value == 0.5

    def test_to_dict(self):
        """Verify profile serialization."""
        traits = {"BWT": TraitValue(name="BWT", value=0.5)}
        profile = TraitProfile(lpn_id="TEST123", traits=traits)
        d = profile.to_dict()

        assert d["lpn_id"] == "TEST123"
        assert "BWT" in d["traits"]


class TestPedigreeNode:
    """Tests for PedigreeNode dataclass."""

    def test_basic_creation(self):
        """Verify basic node creation."""
        node = PedigreeNode(lpn_id="TEST123", generation=1)
        assert node.lpn_id == "TEST123"
        assert node.generation == 1
        assert node.breed is None
        assert node.farm_name is None

    def test_full_creation(self):
        """Verify node with all fields."""
        node = PedigreeNode(
            lpn_id="TEST123",
            generation=2,
            breed="Hampshire",
            gender="Male",
            date_of_birth="2018-04-01",
            farm_name="Test Farm",
            us_index=125.5,
        )
        assert node.breed == "Hampshire"
        assert node.farm_name == "Test Farm"
        assert node.us_index == 125.5

    def test_to_dict(self):
        """Verify node serialization."""
        node = PedigreeNode(lpn_id="TEST123", generation=0, breed="Dorset")
        d = node.to_dict()

        assert d["lpn_id"] == "TEST123"
        assert d["generation"] == 0
        assert d["breed"] == "Dorset"


class TestPedigreeTree:
    """Tests for PedigreeTree dataclass."""

    def test_basic_creation(self):
        """Verify basic tree creation."""
        subject = PedigreeNode(lpn_id="CHILD", generation=0)
        tree = PedigreeTree(subject=subject)

        assert tree.subject.lpn_id == "CHILD"
        assert tree.sire is None
        assert tree.dam is None

    def test_with_parents(self):
        """Verify tree with parent nodes."""
        subject = PedigreeNode(lpn_id="CHILD", generation=0)
        sire = PedigreeNode(lpn_id="SIRE", generation=1)
        dam = PedigreeNode(lpn_id="DAM", generation=1)

        tree = PedigreeTree(subject=subject, sire=sire, dam=dam)

        assert tree.sire.lpn_id == "SIRE"
        assert tree.dam.lpn_id == "DAM"

    def test_all_ancestors_empty(self):
        """Verify all_ancestors with no ancestors."""
        subject = PedigreeNode(lpn_id="CHILD", generation=0)
        tree = PedigreeTree(subject=subject)

        ancestors = tree.all_ancestors()
        assert ancestors == []

    def test_all_ancestors_with_parents(self):
        """Verify all_ancestors includes parents."""
        subject = PedigreeNode(lpn_id="CHILD", generation=0)
        sire = PedigreeNode(lpn_id="SIRE", generation=1)
        dam = PedigreeNode(lpn_id="DAM", generation=1)

        tree = PedigreeTree(subject=subject, sire=sire, dam=dam)

        ancestors = tree.all_ancestors()
        lpn_ids = [a.lpn_id for a in ancestors]

        assert "SIRE" in lpn_ids
        assert "DAM" in lpn_ids

    def test_all_ancestors_with_grandparents(self):
        """Verify all_ancestors includes grandparents."""
        subject = PedigreeNode(lpn_id="CHILD", generation=0)
        sire = PedigreeNode(lpn_id="SIRE", generation=1)
        dam = PedigreeNode(lpn_id="DAM", generation=1)
        sire_sire = PedigreeNode(lpn_id="SS", generation=2)
        dam_dam = PedigreeNode(lpn_id="DD", generation=2)

        tree = PedigreeTree(
            subject=subject,
            sire=sire,
            dam=dam,
            sire_sire=sire_sire,
            dam_dam=dam_dam,
        )

        ancestors = tree.all_ancestors()
        assert len(ancestors) == 4

    def test_to_dict(self):
        """Verify tree serialization."""
        subject = PedigreeNode(lpn_id="CHILD", generation=0)
        sire = PedigreeNode(lpn_id="SIRE", generation=1)

        tree = PedigreeTree(subject=subject, sire=sire)
        d = tree.to_dict()

        assert d["subject"]["lpn_id"] == "CHILD"
        assert d["sire"]["lpn_id"] == "SIRE"
        assert d["dam"] is None


class TestInbreedingResult:
    """Tests for InbreedingResult dataclass."""

    def test_basic_creation(self):
        """Verify basic result creation."""
        result = InbreedingResult(lpn_id="TEST123", coefficient=0.05)

        assert result.lpn_id == "TEST123"
        assert result.coefficient == 0.05
        assert result.risk_level == RiskLevel.LOW
        assert result.common_ancestors == []

    def test_with_common_ancestors(self):
        """Verify result with common ancestors."""
        result = InbreedingResult(
            lpn_id="TEST123",
            coefficient=0.0625,
            common_ancestors=["ANCESTOR1", "ANCESTOR2"],
        )

        assert result.risk_level == RiskLevel.MODERATE
        assert len(result.common_ancestors) == 2

    def test_to_dict(self):
        """Verify result serialization."""
        result = InbreedingResult(lpn_id="TEST123", coefficient=0.125)
        d = result.to_dict()

        assert d["lpn_id"] == "TEST123"
        assert d["coefficient"] == 0.125
        assert d["risk_level"] == "high"


class TestSelectionIndex:
    """Tests for SelectionIndex dataclass."""

    def test_basic_creation(self):
        """Verify basic index creation."""
        index = SelectionIndex(
            name="Test Index",
            trait_weights={"BWT": 0.5, "WWT": 1.0},
        )

        assert index.name == "Test Index"
        assert index.trait_weights["BWT"] == 0.5
        assert index.is_preset is False

    def test_calculate_score_basic(self):
        """Verify basic score calculation."""
        index = SelectionIndex(
            name="Simple",
            trait_weights={"A": 1.0, "B": 2.0},
        )

        ebvs = {"A": 5.0, "B": 3.0}
        score = index.calculate_score(ebvs)

        # 1.0 * 5.0 + 2.0 * 3.0 = 5.0 + 6.0 = 11.0
        assert score == 11.0

    def test_calculate_score_missing_traits(self):
        """Verify score with missing traits uses defaults."""
        index = SelectionIndex(
            name="Full",
            trait_weights={"A": 1.0, "B": 2.0, "C": 3.0},
        )

        ebvs = {"A": 5.0}  # Missing B and C
        score = index.calculate_score(ebvs)

        # Only A contributes: 1.0 * 5.0 = 5.0
        assert score == 5.0

    def test_calculate_score_negative_weights(self):
        """Verify score with negative weights."""
        index = SelectionIndex(
            name="NegWeight",
            trait_weights={"BWT": -0.5, "WWT": 1.0},
        )

        ebvs = {"BWT": 2.0, "WWT": 4.0}
        score = index.calculate_score(ebvs)

        # -0.5 * 2.0 + 1.0 * 4.0 = -1.0 + 4.0 = 3.0
        assert score == 3.0

    def test_to_dict(self):
        """Verify index serialization."""
        index = SelectionIndex(
            name="Test",
            description="A test index",
            trait_weights={"X": 1.0},
            is_preset=True,
        )
        d = index.to_dict()

        assert d["name"] == "Test"
        assert d["description"] == "A test index"
        assert d["trait_weights"] == {"X": 1.0}
        assert d["is_preset"] is True


class TestPresetIndexes:
    """Tests for preset selection indexes."""

    def test_terminal_index_exists(self):
        """Verify Terminal Index is defined correctly."""
        assert "terminal" in PRESET_INDEXES
        assert TERMINAL_INDEX is not None
        assert TERMINAL_INDEX.name == "Terminal Index"
        assert TERMINAL_INDEX.is_preset is True
        assert "PWWT" in TERMINAL_INDEX.trait_weights

    def test_maternal_index_exists(self):
        """Verify Maternal Index is defined correctly."""
        assert "maternal" in PRESET_INDEXES
        assert MATERNAL_INDEX is not None
        assert "NLW" in MATERNAL_INDEX.trait_weights
        assert "MWWT" in MATERNAL_INDEX.trait_weights

    def test_range_index_exists(self):
        """Verify Range Index is defined correctly."""
        assert "range" in PRESET_INDEXES
        assert RANGE_INDEX is not None
        assert RANGE_INDEX.is_preset is True

    def test_hair_index_exists(self):
        """Verify Hair Index is defined correctly."""
        assert "hair" in PRESET_INDEXES
        assert HAIR_INDEX is not None

    def test_all_preset_indexes_are_preset(self):
        """Verify all preset indexes have is_preset=True."""
        for name, index in PRESET_INDEXES.items():
            assert index.is_preset is True, f"{name} should be preset"


class TestFlockSummary:
    """Tests for FlockSummary dataclass."""

    def test_basic_creation(self):
        """Verify basic summary creation."""
        summary = FlockSummary(total_animals=100)

        assert summary.total_animals == 100
        assert summary.male_count == 0
        assert summary.female_count == 0
        assert summary.trait_summary == {}

    def test_with_full_data(self):
        """Verify summary with all fields."""
        summary = FlockSummary(
            flock_name="Test Flock",
            total_animals=50,
            male_count=10,
            female_count=40,
            status_breakdown={"Active": 45, "Sold": 5},
            breed_breakdown={"Suffolk": 30, "Hampshire": 20},
            trait_summary={"BWT": {"mean": 0.5, "std": 0.2}},
        )

        assert summary.flock_name == "Test Flock"
        assert summary.status_breakdown["Active"] == 45
        assert summary.trait_summary["BWT"]["mean"] == 0.5

    def test_to_dict(self):
        """Verify summary serialization."""
        summary = FlockSummary(
            total_animals=10,
            male_count=3,
            female_count=7,
        )
        d = summary.to_dict()

        assert d["total_animals"] == 10
        assert d["male_count"] == 3
        assert d["female_count"] == 7


class TestMatingPair:
    """Tests for MatingPair dataclass."""

    def test_basic_creation(self):
        """Verify basic mating pair creation."""
        pair = MatingPair(
            ram_lpn="RAM001",
            ewe_lpn="EWE001",
            composite_score=85.5,
        )

        assert pair.ram_lpn == "RAM001"
        assert pair.ewe_lpn == "EWE001"
        assert pair.composite_score == 85.5

    def test_with_projections(self):
        """Verify mating pair with projected values."""
        pair = MatingPair(
            ram_lpn="RAM001",
            ewe_lpn="EWE001",
            composite_score=90.0,
            projected_offspring_ebvs={"BWT": 0.5, "WWT": 3.0},
            projected_inbreeding=0.03,
        )

        assert pair.projected_offspring_ebvs["BWT"] == 0.5
        assert pair.projected_inbreeding == 0.03

    def test_to_dict(self):
        """Verify mating pair serialization."""
        pair = MatingPair(
            ram_lpn="RAM001",
            ewe_lpn="EWE001",
            composite_score=75.0,
            notes=["Good match"],
        )
        d = pair.to_dict()

        assert d["ram_lpn"] == "RAM001"
        assert d["notes"] == ["Good match"]


class TestAnimalAnalysis:
    """Tests for AnimalAnalysis dataclass."""

    def test_basic_creation(self):
        """Verify basic analysis creation."""
        analysis = AnimalAnalysis(lpn_id="TEST123")

        assert analysis.lpn_id == "TEST123"
        assert analysis.breed is None
        assert analysis.index_scores == {}

    def test_with_trait_profile(self):
        """Verify analysis with trait profile."""
        profile = TraitProfile(
            lpn_id="TEST123",
            traits={"BWT": TraitValue(name="BWT", value=0.5)},
        )
        analysis = AnimalAnalysis(
            lpn_id="TEST123",
            breed="Suffolk",
            trait_profile=profile,
            index_scores={"Terminal": 85.0},
        )

        assert analysis.trait_profile.traits["BWT"].value == 0.5
        assert analysis.index_scores["Terminal"] == 85.0

    def test_to_dict(self):
        """Verify analysis serialization."""
        analysis = AnimalAnalysis(
            lpn_id="TEST123",
            breed="Dorset",
            gender="Male",
        )
        d = analysis.to_dict()

        assert d["lpn_id"] == "TEST123"
        assert d["breed"] == "Dorset"
        assert d["gender"] == "Male"
