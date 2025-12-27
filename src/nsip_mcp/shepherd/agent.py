"""Shepherd Agent - Main orchestration for sheep husbandry guidance.

This module provides the main ShepherdAgent class that coordinates
across all domains (breeding, health, calendar, economics) to provide
comprehensive guidance for sheep operations.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from nsip_mcp.metrics import server_metrics
from nsip_mcp.shepherd.domains.breeding import BreedingDomain
from nsip_mcp.shepherd.domains.calendar import CalendarDomain
from nsip_mcp.shepherd.domains.economics import EconomicsDomain
from nsip_mcp.shepherd.domains.health import HealthDomain
from nsip_mcp.shepherd.persona import ShepherdPersona
from nsip_mcp.shepherd.regions import detect_region, get_region_context


class Domain(Enum):
    """Available Shepherd domains."""

    BREEDING = "breeding"
    HEALTH = "health"
    CALENDAR = "calendar"
    ECONOMICS = "economics"
    GENERAL = "general"


@dataclass
class ShepherdAgent:
    """Main Shepherd agent for coordinating husbandry guidance.

    The Shepherd agent combines expertise across four domains:
    - Breeding: Genetic selection, EBVs, mating recommendations
    - Health: Disease prevention, nutrition, parasite management
    - Calendar: Seasonal planning, task scheduling
    - Economics: Costs, profitability, ROI analysis

    The agent uses a neutral expert persona (veterinarian-like) and
    adapts advice to the user's region and production context.
    """

    persona: ShepherdPersona = field(default_factory=ShepherdPersona)
    region: str | None = None
    production_goal: str = "balanced"

    # Domain handlers
    _breeding: BreedingDomain = field(init=False)
    _health: HealthDomain = field(init=False)
    _calendar: CalendarDomain = field(init=False)
    _economics: EconomicsDomain = field(init=False)

    def __post_init__(self):
        """Initialize domain handlers."""
        self._breeding = BreedingDomain(persona=self.persona)
        self._health = HealthDomain(persona=self.persona)
        self._calendar = CalendarDomain(persona=self.persona)
        self._economics = EconomicsDomain(persona=self.persona)

    def set_region(
        self,
        region: str | None = None,
        state: str | None = None,
        zip_code: str | None = None,
    ) -> str | None:
        """Set or detect the user's region.

        Args:
            region: Explicit region ID
            state: State code for detection
            zip_code: ZIP code for detection

        Returns:
            The detected or set region ID
        """
        if region:
            self.region = region
        elif state or zip_code:
            self.region = detect_region(state=state, zip_code=zip_code)
        return self.region

    def get_region_context(self) -> dict[str, Any]:
        """Get context for the current region."""
        if self.region:
            return get_region_context(self.region)
        return {"note": "No region set - advice will be general"}

    def classify_question(self, question: str) -> Domain:
        """Classify a question into the appropriate domain.

        Args:
            question: The user's question

        Returns:
            The most appropriate Domain enum value
        """
        question_lower = question.lower()

        # Breeding keywords
        breeding_keywords = [
            "ebv",
            "breeding",
            "genetic",
            "selection",
            "mating",
            "inbreeding",
            "sire",
            "ram",
            "lineage",
            "pedigree",
            "heritability",
            "trait",
            "index",
            "progeny",
        ]
        if any(kw in question_lower for kw in breeding_keywords):
            return Domain.BREEDING

        # Health keywords
        health_keywords = [
            "health",
            "disease",
            "parasite",
            "worm",
            "nutrition",
            "feed",
            "feeding",
            "vaccination",
            "vaccine",
            "sick",
            "body condition",
            "bcs",
            "mineral",
            "protein",
            "famacha",
            "drench",
            "anthelmintic",
        ]
        if any(kw in question_lower for kw in health_keywords):
            return Domain.HEALTH

        # Calendar keywords
        calendar_keywords = [
            "when",
            "schedule",
            "timing",
            "season",
            "calendar",
            "lambing",
            "shearing",
            "weaning",
            "breeding season",
            "month",
            "spring",
            "summer",
            "fall",
            "winter",
        ]
        if any(kw in question_lower for kw in calendar_keywords):
            return Domain.CALENDAR

        # Economics keywords
        economics_keywords = [
            "cost",
            "price",
            "profit",
            "roi",
            "return",
            "breakeven",
            "budget",
            "market",
            "sell",
            "value",
            "expense",
            "revenue",
            "investment",
        ]
        if any(kw in question_lower for kw in economics_keywords):
            return Domain.ECONOMICS

        return Domain.GENERAL

    def consult(
        self,
        question: str,
        domain: Domain | None = None,
        context: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Main consultation entry point.

        Args:
            question: The user's question
            domain: Optional explicit domain (auto-detected if not provided)
            context: Optional additional context

        Returns:
            Dict with answer, recommendations, and metadata
        """
        # Record consultation
        server_metrics.record_prompt_execution("shepherd_consult", True)

        # Detect domain if not specified
        if domain is None:
            domain = self.classify_question(question)

        # Get regional context
        region_context = self.get_region_context() if self.region else {}

        # Route to appropriate domain handler
        result: dict[str, Any] = {
            "domain": domain.value,
            "region": self.region,
            "question": question,
        }

        try:
            if domain == Domain.BREEDING:
                result.update(self._handle_breeding(question, context))
            elif domain == Domain.HEALTH:
                result.update(self._handle_health(question, context))
            elif domain == Domain.CALENDAR:
                result.update(self._handle_calendar(question, context))
            elif domain == Domain.ECONOMICS:
                result.update(self._handle_economics(question, context))
            else:
                result.update(self._handle_general(question, context))

            # Add regional context
            if region_context:
                result["regional_context"] = {
                    "name": region_context.get("name"),
                    "climate": region_context.get("climate"),
                    "challenges": region_context.get("challenges", [])[:2],
                }

        except Exception as e:
            server_metrics.record_prompt_execution("shepherd_consult", False)
            result["error"] = str(e)
            result["answer"] = (
                "I encountered an issue processing your question. "
                "Please try rephrasing or provide more context."
            )

        return result

    def _handle_breeding(
        self,
        question: str,
        context: dict | None,
    ) -> dict[str, Any]:
        """Handle breeding domain questions."""
        # Check for specific question types
        question_lower = question.lower()

        if "ebv" in question_lower and any(
            word in question_lower for word in ["interpret", "meaning", "what does"]
        ):
            # EBV interpretation question
            return {
                "answer": (
                    "EBVs (Estimated Breeding Values) represent an animal's genetic merit "
                    "for specific traits, expressed as deviations from the breed average. "
                    "Positive values indicate above-average genetic potential."
                ),
                "guidance": self._breeding.interpret_ebv(
                    trait="General",
                    value=0,
                    accuracy=None,
                ),
                "recommendations": [
                    "Compare EBVs within the same breed and evaluation",
                    "Consider accuracy when making selection decisions",
                    "Use selection indexes for balanced improvement",
                ],
            }

        if "inbreeding" in question_lower:
            return {
                "answer": (
                    "Inbreeding management is critical for maintaining genetic diversity "
                    "and avoiding inbreeding depression. NSIP provides tools to calculate "
                    "and manage inbreeding coefficients."
                ),
                "guidance": self._breeding.assess_inbreeding_risk(coefficient=0.05),
                "recommendations": [
                    "Keep inbreeding coefficient below 6.25% if possible",
                    "Avoid mating animals sharing parents or grandparents",
                    "Periodically introduce unrelated genetics",
                ],
            }

        if "selection" in question_lower or "strategy" in question_lower:
            return {
                "answer": (
                    "Selection strategy depends on your production goals. "
                    f"For {self.production_goal} production, focus on the "
                    "traits with highest economic impact for your operation."
                ),
                "guidance": self._breeding.recommend_selection_strategy(
                    goal=self.production_goal,
                ),
            }

        # General breeding question
        return {
            "answer": (
                "I can help with breeding decisions including EBV interpretation, "
                "selection strategies, mating recommendations, and inbreeding management. "
                "What specific aspect would you like to explore?"
            ),
            "available_topics": [
                "EBV interpretation and comparison",
                "Selection index calculation",
                "Inbreeding coefficient analysis",
                "Mating plan optimization",
                "Genetic progress estimation",
            ],
        }

    def _handle_health(
        self,
        question: str,
        context: dict | None,
    ) -> dict[str, Any]:
        """Handle health domain questions."""
        question_lower = question.lower()

        if "parasite" in question_lower or "worm" in question_lower:
            return {
                "answer": (
                    "Parasite management is one of the most important health challenges "
                    "in sheep production. Success requires integrated management including "
                    "monitoring, targeted treatment, and pasture management."
                ),
                "guidance": self._health.assess_parasite_risk(
                    region=self.region or "midwest",
                    season="summer",  # Default
                ),
                "recommendations": [
                    "Use FAMACHA scoring for targeted selective treatment",
                    "Conduct fecal egg counts to monitor burden",
                    "Rotate pastures with 60+ day rest periods",
                    "Select for parasite resistance (hair sheep, resistant lines)",
                ],
            }

        if "nutrition" in question_lower or "feed" in question_lower:
            life_stage = "maintenance"
            if "pregnant" in question_lower or "gestation" in question_lower:
                life_stage = "gestation"
            elif "lactating" in question_lower or "nursing" in question_lower:
                life_stage = "lactation"
            elif "flushing" in question_lower or "breeding" in question_lower:
                life_stage = "flushing"

            return {
                "answer": (
                    f"Nutrition requirements vary significantly by life stage. "
                    f"For {life_stage}, here are the key considerations:"
                ),
                "guidance": self._health.get_nutrition_recommendations(
                    life_stage=life_stage,
                    region=self.region,
                ),
            }

        if "vaccin" in question_lower:
            return {
                "answer": (
                    "A core vaccination program protects against clostridial diseases "
                    "(enterotoxemia, tetanus). Additional vaccines depend on regional "
                    "disease risks and operation type."
                ),
                "guidance": self._health.get_vaccination_schedule(
                    region=self.region,
                ),
            }

        # General health question
        return {
            "answer": (
                "I can help with health and nutrition questions including disease "
                "prevention, parasite management, feeding programs, and body condition. "
                "What specific area concerns you?"
            ),
            "available_topics": [
                "Parasite management and FAMACHA",
                "Nutrition by life stage",
                "Vaccination programs",
                "Disease prevention",
                "Body condition scoring",
            ],
        }

    def _handle_calendar(
        self,
        question: str,
        context: dict | None,
    ) -> dict[str, Any]:
        """Handle calendar domain questions."""
        question_lower = question.lower()

        if "lambing" in question_lower:
            return {
                "answer": (
                    "Lambing preparation should begin 4-6 weeks before expected "
                    "lambing dates. Key tasks include vaccination, nutrition adjustment, "
                    "shearing/crutching, and facility preparation."
                ),
                "guidance": self._calendar.get_seasonal_tasks(
                    task_type="lambing",
                    region=self.region,
                ),
            }

        if "shearing" in question_lower:
            return {
                "answer": (
                    "Shearing timing depends on lambing schedule and climate. "
                    "Most operations shear 4-6 weeks before lambing (wool sheep) "
                    "or in spring before hot weather."
                ),
                "guidance": self._calendar.get_seasonal_tasks(
                    task_type="shearing",
                    region=self.region,
                ),
            }

        if "breeding" in question_lower and "when" in question_lower:
            return {
                "answer": (
                    "Breeding timing is based on desired lambing date. "
                    "Count back 147 days (5 months) from target lambing. "
                    "Ram preparation should begin 4-6 weeks before introduction."
                ),
                "guidance": self._calendar.calculate_breeding_dates(
                    target_lambing="march",  # Default
                ),
            }

        if "market" in question_lower:
            return {
                "answer": (
                    "Marketing timing affects profitability significantly. "
                    "Holiday markets (Easter, Eid) often command premium prices "
                    "for specific weights and types."
                ),
                "guidance": self._calendar.get_marketing_windows(
                    region=self.region,
                ),
            }

        # General calendar question
        return {
            "answer": (
                "I can help with seasonal planning and scheduling including "
                "breeding timing, lambing preparation, shearing, and marketing. "
                "What timeframe or activity would you like to plan?"
            ),
            "available_topics": [
                "Breeding season planning",
                "Lambing preparation checklist",
                "Shearing scheduling",
                "Marketing windows",
                "Annual calendar creation",
            ],
        }

    def _handle_economics(
        self,
        question: str,
        context: dict | None,
    ) -> dict[str, Any]:
        """Handle economics domain questions."""
        question_lower = question.lower()

        if "cost" in question_lower:
            return {
                "answer": (
                    "Production costs vary by flock size, region, and management "
                    "system. Here's a typical cost breakdown for reference:"
                ),
                "guidance": self._economics.get_cost_breakdown(
                    flock_size="medium",
                ),
            }

        if "breakeven" in question_lower:
            return {
                "answer": (
                    "Breakeven analysis helps determine the minimum price needed "
                    "to cover costs. Key factors are annual ewe costs, lamb crop "
                    "percentage, and marketing costs."
                ),
                "guidance": self._economics.calculate_breakeven(
                    annual_costs_per_ewe=150,
                    lambs_per_ewe=1.5,
                    lamb_weight=110,
                ),
            }

        if "ram" in question_lower and ("roi" in question_lower or "worth" in question_lower):
            return {
                "answer": (
                    "Ram ROI depends on purchase price, years of use, ewes bred, "
                    "and the genetic improvement delivered to offspring."
                ),
                "guidance": self._economics.calculate_ram_roi(
                    ram_cost=1500,
                    years_used=3,
                    ewes_per_year=30,
                    lamb_value_increase=15,
                ),
            }

        if "profit" in question_lower:
            return {
                "answer": (
                    "Profitability depends on revenue (lambs, wool, culls) minus "
                    "costs (feed, health, labor, overhead). Key levers are lamb "
                    "crop percentage and cost per ewe."
                ),
                "guidance": self._economics.analyze_flock_profitability(
                    ewe_count=50,
                    lambs_marketed=70,
                    avg_lamb_price=200,
                    wool_revenue=200,
                    cull_revenue=400,
                    total_costs=8000,
                ),
            }

        # General economics question
        return {
            "answer": (
                "I can help with economic analysis including cost breakdowns, "
                "breakeven analysis, RAM ROI, and profitability assessment. "
                "What aspect of your operation economics would you like to explore?"
            ),
            "available_topics": [
                "Cost breakdown by category",
                "Breakeven price calculation",
                "Ram purchase ROI",
                "Flock profitability analysis",
                "Marketing option comparison",
            ],
        }

    def _handle_general(
        self,
        question: str,
        context: dict | None,
    ) -> dict[str, Any]:
        """Handle general questions that don't fit a specific domain."""
        return {
            "answer": (
                "I'm the NSIP Shepherd, your expert advisor for sheep husbandry. "
                "I can help with questions about breeding and genetics, health "
                "and nutrition, seasonal management, and operation economics. "
                "What would you like to know?"
            ),
            "domains": {
                "breeding": "Genetic selection, EBVs, mating plans, inbreeding",
                "health": "Disease prevention, parasites, nutrition, vaccination",
                "calendar": "Seasonal planning, lambing, shearing, marketing timing",
                "economics": "Costs, profitability, ROI, market analysis",
            },
            "tip": (
                "For best results, include your region or state in your question "
                "so I can provide regionally-appropriate advice."
            ),
        }

    def get_quick_answer(
        self,
        topic: str,
        subtopic: str | None = None,
    ) -> dict[str, Any]:
        """Get a quick reference answer for common topics.

        Args:
            topic: Main topic (ebv, parasite, nutrition, etc.)
            subtopic: Optional subtopic for more specific info

        Returns:
            Dict with quick reference information
        """
        quick_refs = {
            "ebv": {
                "summary": "Estimated Breeding Values predict genetic merit for traits",
                "key_points": [
                    "Positive = above breed average",
                    "Compare within same breed/evaluation",
                    "Higher accuracy = more reliable",
                ],
            },
            "heritability": {
                "summary": "Proportion of trait variation due to genetics",
                "key_points": [
                    "High (>0.35): Birth weight, carcass traits",
                    "Moderate (0.20-0.35): Weaning weight, growth",
                    "Low (<0.20): Fertility, survival",
                ],
            },
            "parasite": {
                "summary": "Integrated management is key to parasite control",
                "key_points": [
                    "FAMACHA scoring for targeted treatment",
                    "Fecal egg counts to monitor",
                    "Pasture rotation (60+ day rest)",
                    "Select for resistance",
                ],
            },
            "bcs": {
                "summary": "Body Condition Score (1-5 scale) indicates energy reserves",
                "key_points": [
                    "Target 2.5-3.0 at breeding",
                    "Target 3.0-3.5 at lambing",
                    "Score over loin and rib area",
                    "Half-score changes are significant",
                ],
            },
        }

        if topic.lower() in quick_refs:
            return quick_refs[topic.lower()]

        return {
            "summary": f"Quick reference for '{topic}' not available",
            "suggestion": "Try asking a specific question about this topic",
        }
