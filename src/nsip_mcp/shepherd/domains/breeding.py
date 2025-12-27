"""Breeding domain for the Shepherd agent.

Provides expert guidance on:
- EBV interpretation and comparison
- Selection strategies and index calculation
- Mating recommendations and inbreeding avoidance
- Trait improvement planning
- Genetic progress estimation
"""

from dataclasses import dataclass, field
from typing import Any, Optional

from nsip_mcp.knowledge_base import (
    get_heritabilities,
    get_selection_index,
    get_trait_glossary,
)
from nsip_mcp.shepherd.persona import ShepherdPersona, format_shepherd_response


@dataclass
class BreedingDomain:
    """Breeding domain handler for the Shepherd agent.

    This domain provides expert guidance on genetic selection,
    EBV interpretation, mating recommendations, and trait improvement.
    """

    persona: ShepherdPersona = field(default_factory=ShepherdPersona)

    def format_response(
        self,
        content: str,
        metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Format a response using the domain's persona.

        Args:
            content: The main response content
            metadata: Optional metadata to include

        Returns:
            Formatted response dictionary with persona styling
        """
        formatted_text = format_shepherd_response(answer=content)
        response: dict[str, Any] = {"guidance": formatted_text, "domain": "breeding"}
        if metadata:
            response["metadata"] = metadata
        return response

    def interpret_ebv(
        self,
        trait: str,
        value: float,
        accuracy: Optional[float] = None,
        breed_average: Optional[float] = None,
    ) -> dict[str, Any]:
        """Interpret an EBV value in context.

        Args:
            trait: Trait code (e.g., WWT, NLW, PWWT)
            value: The EBV value
            accuracy: Optional accuracy percentage (0-100)
            breed_average: Optional breed average for comparison

        Returns:
            Dict with interpretation, context, and recommendations
        """
        # Get trait information
        glossary = get_trait_glossary()
        trait_info = glossary.get(trait, {}) if glossary else {}

        # Get heritability for context
        heritabilities = get_heritabilities()
        h2 = heritabilities.get(trait, 0.25) if heritabilities else 0.25

        # Build interpretation
        interpretation = {
            "trait": trait,
            "trait_name": trait_info.get("name", trait),
            "value": value,
            "units": trait_info.get("units", "units"),
            "interpretation": self._value_interpretation(value, trait, breed_average),
            "heritability": h2,
            "selection_response": self._selection_response_note(h2),
        }

        if accuracy is not None:
            interpretation["accuracy"] = accuracy
            interpretation["accuracy_note"] = self._accuracy_interpretation(accuracy)

        if breed_average is not None:
            deviation = value - breed_average
            interpretation["vs_breed_avg"] = {
                "deviation": deviation,
                "percentile_estimate": self._estimate_percentile(deviation, trait),
            }

        return interpretation

    def _value_interpretation(
        self,
        value: float,
        trait: str,
        breed_average: Optional[float],
    ) -> str:
        """Generate interpretation text for an EBV value."""
        if breed_average is not None:
            diff = value - breed_average
            if abs(diff) < 0.1 * abs(breed_average) if breed_average != 0 else abs(diff) < 0.5:
                return f"Near breed average ({value:+.2f} vs {breed_average:.2f})"
            elif diff > 0:
                return f"Above breed average ({value:+.2f} vs {breed_average:.2f})"
            else:
                return f"Below breed average ({value:+.2f} vs {breed_average:.2f})"
        else:
            if value > 0:
                return f"Positive EBV ({value:+.2f}) indicates above-average genetic merit"
            elif value < 0:
                return f"Negative EBV ({value:+.2f}) indicates below-average genetic merit"
            else:
                return "EBV at breed average (0.0)"

    def _accuracy_interpretation(self, accuracy: float) -> str:
        """Interpret accuracy percentage."""
        if accuracy >= 90:
            return "Very high accuracy - reliable for selection decisions"
        elif accuracy >= 70:
            return "Good accuracy - suitable for most selection decisions"
        elif accuracy >= 50:
            return "Moderate accuracy - consider with other information"
        else:
            return "Low accuracy - use with caution, may change significantly"

    def _selection_response_note(self, h2: float) -> str:
        """Generate note about expected selection response."""
        if h2 >= 0.35:
            return "High heritability - responds well to selection"
        elif h2 >= 0.20:
            return "Moderate heritability - steady progress possible"
        elif h2 >= 0.10:
            return "Low heritability - slow progress, consider management"
        else:
            return "Very low heritability - limited genetic progress expected"

    def _estimate_percentile(self, deviation: float, trait: str) -> str:
        """Estimate percentile ranking from deviation."""
        # Rough estimates based on normal distribution
        # Assumes SD of ~2-3 for most traits
        if deviation > 4:
            return "Top 5%"
        elif deviation > 2:
            return "Top 15%"
        elif deviation > 0.5:
            return "Top 35%"
        elif deviation > -0.5:
            return "Middle 30%"
        elif deviation > -2:
            return "Bottom 35%"
        else:
            return "Bottom 15%"

    def recommend_selection_strategy(
        self,
        goal: str,
        current_strengths: Optional[list[str]] = None,
        current_weaknesses: Optional[list[str]] = None,
        flock_size: str = "medium",
    ) -> dict[str, Any]:
        """Recommend a selection strategy based on goals.

        Args:
            goal: Production goal (terminal, maternal, hair, balanced)
            current_strengths: Traits where flock excels
            current_weaknesses: Traits needing improvement
            flock_size: Flock size category (small, medium, large)

        Returns:
            Dict with strategy recommendations
        """
        # Get selection index for the goal
        index_info = get_selection_index(goal)

        if not index_info:
            return {
                "error": f"Unknown production goal: {goal}",
                "available_goals": ["terminal", "maternal", "hair", "balanced"],
            }

        heritabilities = get_heritabilities() or {}

        strategy = {
            "goal": goal,
            "index_name": index_info.get("name", goal.title()),
            "description": index_info.get("description", ""),
            "primary_traits": index_info.get("traits", []),
            "weights": index_info.get("weights", {}),
            "recommendations": [],
            "selection_intensity": self._recommend_intensity(flock_size),
        }

        # Add trait-specific recommendations
        for trait in strategy["primary_traits"][:5]:
            h2 = heritabilities.get(trait, 0.25)
            weight = strategy["weights"].get(trait, 1.0)

            if current_weaknesses and trait in current_weaknesses:
                priority = "HIGH - current weakness"
            elif weight > 0.2:
                priority = "Important - high index weight"
            else:
                priority = "Consider - moderate weight"

            strategy["recommendations"].append(
                {
                    "trait": trait,
                    "priority": priority,
                    "heritability": h2,
                    "expected_progress": self._selection_response_note(h2),
                }
            )

        return strategy

    def _recommend_intensity(self, flock_size: str) -> dict[str, Any]:
        """Recommend selection intensity based on flock size."""
        intensities = {
            "small": {
                "percent_selected": "40-50%",
                "rams_to_keep": "2-3 top rams",
                "note": "Limited selection possible; focus on key traits",
            },
            "medium": {
                "percent_selected": "25-35%",
                "rams_to_keep": "4-6 top rams",
                "note": "Good selection possible; balance multiple traits",
            },
            "large": {
                "percent_selected": "15-25%",
                "rams_to_keep": "8+ top rams",
                "note": "Strong selection possible; optimize index values",
            },
        }
        return intensities.get(flock_size, intensities["medium"])

    def estimate_genetic_progress(
        self,
        trait: str,
        current_mean: float,
        selection_differential: float,
        generations: int = 3,
    ) -> dict[str, Any]:
        """Estimate genetic progress over multiple generations.

        Args:
            trait: Target trait code
            current_mean: Current flock mean for the trait
            selection_differential: Difference between selected parents and mean
            generations: Number of generations to project

        Returns:
            Dict with projected progress by generation
        """
        heritabilities = get_heritabilities() or {}
        h2 = heritabilities.get(trait, 0.25)

        # Response to selection: R = h² × S
        response_per_gen = h2 * selection_differential

        projections = []
        cumulative = current_mean

        for gen in range(1, generations + 1):
            cumulative += response_per_gen
            projections.append(
                {
                    "generation": gen,
                    "expected_mean": round(cumulative, 3),
                    "gain_from_start": round(cumulative - current_mean, 3),
                }
            )

        return {
            "trait": trait,
            "heritability": h2,
            "selection_differential": selection_differential,
            "response_per_generation": round(response_per_gen, 3),
            "projections": projections,
            "assumptions": [
                "Constant selection intensity across generations",
                "No change in genetic variance",
                "Random mating within selected group",
            ],
        }

    def assess_inbreeding_risk(
        self,
        coefficient: float,
        trend: Optional[str] = None,
    ) -> dict[str, Any]:
        """Assess inbreeding coefficient and provide guidance.

        Args:
            coefficient: Inbreeding coefficient (0-1 or percentage)
            trend: Optional trend indicator ("increasing", "stable", "decreasing")

        Returns:
            Dict with risk assessment and recommendations
        """
        # Normalize to decimal if percentage
        if coefficient > 1:
            coefficient = coefficient / 100

        # Risk thresholds
        if coefficient < 0.0625:  # < 6.25%
            risk_level = "Low"
            concern = "Minimal concern for inbreeding depression"
        elif coefficient < 0.125:  # 6.25-12.5%
            risk_level = "Moderate"
            concern = "Monitor for inbreeding depression signs"
        elif coefficient < 0.25:  # 12.5-25%
            risk_level = "High"
            concern = "Likely inbreeding depression; introduce new genetics"
        else:
            risk_level = "Very High"
            concern = "Severe inbreeding; immediate genetic diversification needed"

        recommendations = []

        if risk_level in ["High", "Very High"]:
            recommendations.extend(
                [
                    "Introduce unrelated rams from different flocks",
                    "Avoid mating animals sharing grandparents",
                    "Consider AI with unrelated sires",
                ]
            )
        elif risk_level == "Moderate":
            recommendations.extend(
                [
                    "Plan matings to avoid close relatives",
                    "Track pedigrees carefully",
                    "Consider occasional outside genetics",
                ]
            )
        else:
            recommendations.append("Continue current management; maintain pedigree records")

        if trend == "increasing":
            warning = "Trend is concerning - take action before levels rise further"
            recommendations.insert(0, warning)

        return {
            "coefficient": coefficient,
            "percentage": f"{coefficient * 100:.2f}%",
            "risk_level": risk_level,
            "concern": concern,
            "recommendations": recommendations,
            "reference": {
                "low": "< 6.25% (half-sibling mating equivalent)",
                "moderate": "6.25-12.5% (first-cousin mating equivalent)",
                "high": "12.5-25% (half-sibling repeated)",
                "very_high": "> 25% (close inbreeding)",
            },
        }

    def format_breeding_advice(
        self,
        question: str,
        answer: str,
        data: Optional[dict] = None,
    ) -> str:
        """Format breeding advice in Shepherd style.

        Args:
            question: The user's breeding question
            answer: The main answer
            data: Optional supporting data

        Returns:
            Formatted Shepherd response
        """
        recommendations = []
        considerations = []
        sources = ["NSIP EBV Database"]

        if data:
            if "recommendations" in data:
                recommendations = data["recommendations"]
            if "assumptions" in data:
                considerations = data["assumptions"]

        return format_shepherd_response(
            answer=answer,
            context=f"Question: {question}" if question else None,
            recommendations=recommendations if recommendations else None,
            considerations=considerations if considerations else None,
            sources=sources,
        )
