"""Health domain for the Shepherd agent.

Provides expert guidance on:
- Disease prevention and management
- Parasite control strategies
- Nutrition and feeding programs
- Body condition scoring
- Vaccination schedules
"""

from dataclasses import dataclass, field
from typing import Any

from nsip_mcp.knowledge_base import (
    get_disease_guide,
    get_nutrition_guide,
    get_region_info,
)
from nsip_mcp.shepherd.persona import ShepherdPersona, format_shepherd_response


@dataclass
class HealthDomain:
    """Health domain handler for the Shepherd agent.

    This domain provides expert guidance on sheep health,
    disease prevention, parasite management, and nutrition.
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
        response: dict[str, Any] = {"guidance": formatted_text, "domain": "health"}
        if metadata:
            response["metadata"] = metadata
        return response

    def get_disease_prevention(
        self,
        region: str,
        season: str | None = None,
        age_group: str | None = None,
    ) -> dict[str, Any]:
        """Get disease prevention recommendations for a region.

        Args:
            region: NSIP region identifier
            season: Optional season (spring, summer, fall, winter)
            age_group: Optional age group (lambs, yearlings, adults)

        Returns:
            Dict with disease risks and prevention strategies
        """
        diseases_data = get_disease_guide(region)
        region_info = get_region_info(region)

        if not diseases_data:
            return {
                "region": region,
                "note": "No specific disease data for region; consult local extension",
                "general_recommendations": [
                    "Maintain vaccination program",
                    "Practice good biosecurity",
                    "Monitor body condition regularly",
                    "Work with a veterinarian for health planning",
                ],
            }

        # Convert dict to list of disease entries for easier processing
        # diseases_data is {disease_name: {details...}} format
        diseases_list = []
        for name, details in diseases_data.items():
            if isinstance(details, dict):
                disease_entry = {"name": name, **details}
                diseases_list.append(disease_entry)

        # Filter by season if provided
        if season:
            seasonal_diseases = [
                d
                for d in diseases_list
                if season.lower() in str(d.get("season", "")).lower()
                or d.get("season") == "year-round"
            ]
        else:
            seasonal_diseases = diseases_list

        # Build prevention guide
        prevention: dict[str, Any] = {
            "region": region_info.get("name", region) if region_info else region,
            "climate": region_info.get("climate", "varies") if region_info else "varies",
            "parasite_season": (
                region_info.get("parasite_season", "varies") if region_info else "varies"
            ),
            "diseases": [],
            "general_recommendations": [],
        }

        for disease in seasonal_diseases[:10]:  # Top 10 diseases
            if isinstance(disease, dict):
                prevention["diseases"].append(
                    {
                        "name": disease.get("name", "Unknown"),
                        "risk_level": disease.get("risk_level", "moderate"),
                        "prevention": disease.get("prevention", "Consult veterinarian"),
                        "signs": disease.get("signs", []),
                        "treatment": disease.get("treatment", "Veterinary care required"),
                    }
                )

        # Add regional challenges
        if region_info and "challenges" in region_info:
            prevention["regional_challenges"] = region_info["challenges"]

        return prevention

    def get_nutrition_recommendations(
        self,
        life_stage: str,
        region: str | None = None,
        body_condition: float | None = None,
    ) -> dict[str, Any]:
        """Get nutrition recommendations for a life stage.

        Args:
            life_stage: Life stage (maintenance, flushing, gestation, lactation)
            region: Optional region for local adjustments
            body_condition: Optional BCS (1-5 scale)

        Returns:
            Dict with nutrition recommendations
        """
        nutrition = get_nutrition_guide(region, life_stage)

        if not nutrition:
            # Return general defaults
            nutrition = self._default_nutrition(life_stage)

        recommendations: dict[str, Any] = {
            "life_stage": life_stage,
            "requirements": nutrition,
            "adjustments": [],
            "feed_options": [],
        }

        # Add body condition adjustments
        if body_condition is not None:
            bcs_adjustment = self._bcs_adjustment(body_condition, life_stage)
            recommendations["body_condition"] = {
                "score": body_condition,
                "interpretation": bcs_adjustment["interpretation"],
                "adjustment": bcs_adjustment["adjustment"],
            }
            recommendations["adjustments"].append(bcs_adjustment["recommendation"])

        # Add life stage specific notes
        stage_notes = self._life_stage_notes(life_stage)
        recommendations["notes"] = stage_notes

        return recommendations

    def _default_nutrition(self, life_stage: str) -> dict[str, Any]:
        """Get default nutrition values for a life stage."""
        defaults: dict[str, dict[str, Any]] = {
            "maintenance": {
                "energy": "2.0-2.4 Mcal ME/day",
                "protein": "8-10% CP",
                "minerals": "Sheep-specific mineral free choice",
                "water": "1-2 gallons/day",
            },
            "flushing": {
                "energy": "2.8-3.2 Mcal ME/day (increase 2-3 weeks before breeding)",
                "protein": "10-12% CP",
                "minerals": "Selenium supplementation if deficient region",
                "water": "1.5-2.5 gallons/day",
            },
            "gestation": {
                "early": {
                    "energy": "2.2-2.6 Mcal ME/day",
                    "protein": "9-10% CP",
                },
                "late": {
                    "energy": "3.5-4.5 Mcal ME/day",
                    "protein": "12-14% CP",
                },
                "minerals": "Calcium supplementation last 4 weeks",
                "water": "2-3 gallons/day",
            },
            "lactation": {
                "singles": {
                    "energy": "4.0-4.5 Mcal ME/day",
                    "protein": "13-15% CP",
                },
                "twins": {
                    "energy": "5.0-6.0 Mcal ME/day",
                    "protein": "15-17% CP",
                },
                "minerals": "High calcium, selenium, zinc",
                "water": "2.5-4 gallons/day",
            },
        }
        return defaults.get(life_stage, defaults["maintenance"])

    def _bcs_adjustment(self, bcs: float, life_stage: str) -> dict[str, Any]:
        """Get adjustment recommendations based on BCS."""
        if bcs < 2.0:
            return {
                "interpretation": "Thin - needs increased nutrition",
                "adjustment": "Increase energy 20-30%",
                "recommendation": f"BCS {bcs} is below target; increase energy intake by 20-30%",
            }
        elif bcs < 2.5:
            return {
                "interpretation": "Slightly thin - monitor closely",
                "adjustment": "Increase energy 10-15%",
                "recommendation": f"BCS {bcs} is slightly low; consider 10-15% energy increase",
            }
        elif bcs <= 3.5:
            return {
                "interpretation": "Ideal condition",
                "adjustment": "Maintain current feeding",
                "recommendation": f"BCS {bcs} is ideal; maintain current program",
            }
        elif bcs <= 4.0:
            return {
                "interpretation": "Slightly overconditioned",
                "adjustment": "Reduce energy 10-15% (except late gestation)",
                "recommendation": f"BCS {bcs} is slightly high; consider modest energy reduction",
            }
        else:
            return {
                "interpretation": "Overconditioned - reduce intake",
                "adjustment": "Reduce energy 20-25%",
                "recommendation": f"BCS {bcs} is too high; reduce energy, increase exercise",
            }

    def _life_stage_notes(self, life_stage: str) -> list[str]:
        """Get important notes for each life stage."""
        notes = {
            "maintenance": [
                "Lowest nutrient requirements of any stage",
                "Good time to allow body condition to normalize",
                "Quality pasture can meet most needs",
            ],
            "flushing": [
                "Start 2-3 weeks before ram introduction",
                "Increasing plane of nutrition improves ovulation rate",
                "Most effective for ewes in moderate condition",
                "Monitor for overcondition in easy-keeping ewes",
            ],
            "gestation": [
                "Nutrient needs increase dramatically in last 6 weeks",
                "70% of fetal growth occurs in last 4 weeks",
                "Inadequate nutrition increases pregnancy toxemia risk",
                "Calcium needs increase for lamb skeletal development",
            ],
            "lactation": [
                "Highest nutrient demand of any production stage",
                "Peak milk at 3-4 weeks post-lambing",
                "Ewes often lose body condition; plan for recovery",
                "Twins/triplets require significantly more nutrients",
            ],
        }
        return notes.get(life_stage, [])

    def assess_parasite_risk(
        self,
        region: str,
        season: str,
        pasture_type: str | None = None,
        stocking_rate: str | None = None,
    ) -> dict[str, Any]:
        """Assess parasite risk and provide management recommendations.

        Args:
            region: NSIP region
            season: Current season
            pasture_type: Optional pasture description
            stocking_rate: Optional stocking rate (low, moderate, high)

        Returns:
            Dict with risk assessment and control strategies
        """
        region_info = get_region_info(region)
        parasite_season = "varies"
        if region_info:
            parasite_season = region_info.get("parasite_season", "varies")

        # Determine base risk
        risk_level = self._calculate_parasite_risk(season, parasite_season, stocking_rate)

        assessment = {
            "region": region_info.get("name", region) if region_info else region,
            "season": season,
            "parasite_season_info": parasite_season,
            "risk_level": risk_level,
            "primary_parasites": [
                "Haemonchus contortus (barber pole worm)",
                "Teladorsagia circumcincta (brown stomach worm)",
                "Nematodirus spp.",
                "Coccidia (lambs)",
            ],
            "monitoring": [],
            "control_strategies": [],
        }

        # Monitoring recommendations
        assessment["monitoring"] = [
            "FAMACHA scoring every 2-3 weeks during high-risk periods",
            "Fecal egg counts (FEC) monthly or as indicated",
            "Body condition scoring to detect subclinical infection",
            "Observe for bottle jaw, pale membranes, diarrhea",
        ]

        # Control strategies based on risk
        if risk_level in ["High", "Very High"]:
            assessment["control_strategies"] = [
                "Increase FAMACHA checking frequency to weekly",
                "Consider targeted selective treatment (TST)",
                "Rotate pastures if possible (>60 day rest)",
                "Move susceptible stock (lambs, thin ewes) to safer pastures",
                "Ensure efficacy of anthelmintics via fecal egg count reduction test",
            ]
        elif risk_level == "Moderate":
            assessment["control_strategies"] = [
                "Monitor using FAMACHA every 2-3 weeks",
                "Treat individuals with FAMACHA scores 4-5",
                "Avoid overgrazing - maintain >3 inch residual height",
                "Consider pasture rotation",
            ]
        else:
            assessment["control_strategies"] = [
                "Continue routine monitoring",
                "Treat only animals with clinical signs",
                "This is a good time for pasture rest and recovery",
            ]

        return assessment

    def _calculate_parasite_risk(
        self,
        season: str,
        parasite_season: str,
        stocking_rate: str | None,
    ) -> str:
        """Calculate overall parasite risk level."""
        # Season-based risk
        season_risk = {
            "spring": 3,
            "summer": 4,
            "fall": 3,
            "winter": 1,
        }.get(season.lower(), 2)

        # Adjust for year-round regions
        if "year-round" in parasite_season.lower():
            season_risk = max(season_risk, 3)

        # Adjust for stocking rate
        stocking_adjustment = (
            {
                "low": -1,
                "moderate": 0,
                "high": 2,
            }.get(stocking_rate, 0)
            if stocking_rate
            else 0
        )

        total_risk = season_risk + stocking_adjustment

        if total_risk >= 5:
            return "Very High"
        elif total_risk >= 4:
            return "High"
        elif total_risk >= 2:
            return "Moderate"
        else:
            return "Low"

    def get_vaccination_schedule(
        self,
        flock_type: str = "commercial",
        region: str | None = None,
    ) -> dict[str, Any]:
        """Get recommended vaccination schedule.

        Args:
            flock_type: Type of operation (commercial, seedstock, show)
            region: Optional region for disease-specific vaccines

        Returns:
            Dict with vaccination schedule
        """
        # Core vaccinations (always recommended)
        core = [
            {
                "vaccine": "CDT (Clostridium perfringens C&D, Tetanus)",
                "timing": "Ewes: 4 weeks pre-lambing; Lambs: 6-8 weeks, booster 3-4 weeks later",
                "frequency": "Annual booster for adults",
                "notes": "Most important vaccine for sheep",
            },
        ]

        # Risk-based vaccinations
        risk_based = [
            {
                "vaccine": "Campylobacter/Vibrio",
                "timing": "Pre-breeding and mid-gestation",
                "frequency": "Annual",
                "when_recommended": "If abortion storms have occurred",
            },
            {
                "vaccine": "Chlamydia (EAE)",
                "timing": "Pre-breeding",
                "frequency": "Annual",
                "when_recommended": "If enzootic abortion diagnosed",
            },
            {
                "vaccine": "Footrot",
                "timing": "Pre-exposure",
                "frequency": "As needed",
                "when_recommended": "Endemic areas or outbreaks",
            },
            {
                "vaccine": "Rabies",
                "timing": "Per label",
                "frequency": "Annual",
                "when_recommended": "Endemic areas, show animals",
            },
        ]

        # Seedstock/show additional
        if flock_type in ["seedstock", "show"]:
            risk_based.append(
                {
                    "vaccine": "Caseous lymphadenitis (CL)",
                    "timing": "Per label",
                    "frequency": "Annual",
                    "when_recommended": "CL prevention programs",
                }
            )

        schedule = {
            "flock_type": flock_type,
            "core_vaccines": core,
            "risk_based_vaccines": risk_based,
            "general_notes": [
                "Store vaccines properly (refrigerated, protected from light)",
                "Follow label directions for dosage and route",
                "Observe withdrawal times if applicable",
                "Work with veterinarian to customize for your operation",
            ],
        }

        # Add regional considerations
        if region:
            region_info = get_region_info(region)
            if region_info and "challenges" in region_info:
                schedule["regional_considerations"] = region_info["challenges"]

        return schedule

    def format_health_advice(
        self,
        question: str,
        answer: str,
        data: dict | None = None,
    ) -> str:
        """Format health advice in Shepherd style.

        Args:
            question: The user's health question
            answer: The main answer
            data: Optional supporting data

        Returns:
            Formatted Shepherd response
        """
        recommendations = []
        considerations = [
            "Always consult a veterinarian for serious health concerns",
        ]

        if data:
            if "control_strategies" in data:
                recommendations = data["control_strategies"]
            elif "recommendations" in data:
                recommendations = data["recommendations"]
            if "notes" in data and isinstance(data["notes"], list):
                considerations.extend(data["notes"][:2])

        return format_shepherd_response(
            answer=answer,
            context=f"Question: {question}" if question else None,
            recommendations=recommendations if recommendations else None,
            considerations=considerations,
            sources=["Veterinary references", "Regional extension guidelines"],
        )
