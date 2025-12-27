"""Economics domain for the Shepherd agent.

Provides expert guidance on:
- Cost analysis and budgeting
- ROI calculations
- Market timing
- Flock size optimization
- Breakeven analysis
"""

import logging
from dataclasses import dataclass, field
from typing import Any

from nsip_mcp.knowledge_base import get_economics_template
from nsip_mcp.shepherd.persona import ShepherdPersona, format_shepherd_response

logger = logging.getLogger(__name__)


@dataclass
class EconomicsDomain:
    """Economics domain handler for the Shepherd agent.

    This domain provides expert guidance on sheep operation economics,
    profitability analysis, and business decision-making.
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
        response: dict[str, Any] = {"guidance": formatted_text, "domain": "economics"}
        if metadata:
            response["metadata"] = metadata
        return response

    def get_cost_breakdown(
        self,
        flock_size: str = "medium",
        production_system: str = "pasture",
    ) -> dict[str, Any]:
        """Get detailed cost breakdown for an operation.

        Args:
            flock_size: Size category (small, medium, large)
            production_system: System type (pasture, drylot, accelerated)

        Returns:
            Dict with itemized costs and totals
        """
        # Use cost_templates from knowledge base, with fallback to defaults
        try:
            cost_data = get_economics_template("cost_templates")
            ewe_costs = cost_data.get("cost_templates", {})
        except Exception as e:
            logger.debug(f"Failed to load cost templates from KB: {e}")
            ewe_costs = {}

        if not ewe_costs:
            ewe_costs = self._default_ewe_costs()

        # Get lamb costs from same template or use defaults
        lamb_costs = self._default_lamb_costs()

        # Scale adjustments based on flock size
        scale_factor = {
            "small": 1.15,  # Higher per-unit costs
            "medium": 1.0,  # Baseline
            "large": 0.85,  # Economies of scale
        }.get(flock_size, 1.0)

        # System adjustments
        system_factor = {
            "pasture": 1.0,
            "drylot": 1.25,  # Higher feed costs
            "accelerated": 1.20,  # More intensive management
        }.get(production_system, 1.0)

        combined_factor = scale_factor * system_factor

        breakdown: dict[str, Any] = {
            "flock_size": flock_size,
            "production_system": production_system,
            "annual_per_ewe": {},
            "per_lamb": {},
            "totals": {},
            "assumptions": [],
        }

        # Process ewe costs
        ewe_total = 0
        for category, values in ewe_costs.items():
            if isinstance(values, dict) and "average" in values:
                adjusted = values["average"] * combined_factor
                breakdown["annual_per_ewe"][category] = {
                    "amount": round(adjusted, 2),
                    "range": f"${values.get('low', 0) * combined_factor:.2f}-"
                    f"${values.get('high', 0) * combined_factor:.2f}",
                }
                ewe_total += adjusted

        breakdown["totals"]["annual_per_ewe"] = round(ewe_total, 2)

        # Process lamb costs
        lamb_total = 0
        for category, values in lamb_costs.items():
            if isinstance(values, dict) and "average" in values:
                adjusted = values["average"] * combined_factor
                breakdown["per_lamb"][category] = {
                    "amount": round(adjusted, 2),
                }
                lamb_total += adjusted

        breakdown["totals"]["per_lamb_raised"] = round(lamb_total, 2)

        # Add assumptions
        breakdown["assumptions"] = [
            f"Based on {flock_size} flock size ({self._flock_size_range(flock_size)})",
            f"{production_system.title()} production system",
            "Regional costs may vary significantly",
            "Labor valued at regional wage rates",
        ]

        return breakdown

    def _default_ewe_costs(self) -> dict[str, dict]:
        """Default annual ewe costs if knowledge base unavailable."""
        return {
            "feed": {"low": 40, "average": 60, "high": 90},
            "minerals": {"low": 8, "average": 12, "high": 18},
            "health": {"low": 10, "average": 18, "high": 30},
            "shearing": {"low": 5, "average": 8, "high": 12},
            "labor": {"low": 15, "average": 25, "high": 40},
            "facilities": {"low": 8, "average": 15, "high": 25},
            "overhead": {"low": 5, "average": 10, "high": 15},
            "ram_share": {"low": 5, "average": 8, "high": 12},
        }

    def _default_lamb_costs(self) -> dict[str, dict]:
        """Default per-lamb costs if knowledge base unavailable."""
        return {
            "creep_feed": {"average": 15},
            "grower_feed": {"average": 25},
            "health": {"average": 8},
            "marketing": {"average": 10},
        }

    def _flock_size_range(self, size: str) -> str:
        """Get flock size range description."""
        ranges = {
            "small": "10-50 ewes",
            "medium": "50-200 ewes",
            "large": "200+ ewes",
        }
        return ranges.get(size, "varies")

    def calculate_breakeven(
        self,
        annual_costs_per_ewe: float,
        lambs_per_ewe: float,
        lamb_weight: float,
        cost_per_lamb: float = 50,
        wool_revenue: float = 5,
    ) -> dict[str, Any]:
        """Calculate breakeven price for lamb production.

        Args:
            annual_costs_per_ewe: Total annual cost per ewe
            lambs_per_ewe: Number of lambs marketed per ewe
            lamb_weight: Average market weight in pounds
            cost_per_lamb: Cost to raise each lamb
            wool_revenue: Annual wool revenue per ewe

        Returns:
            Dict with breakeven analysis
        """
        # Total costs per ewe
        total_lamb_costs = lambs_per_ewe * cost_per_lamb
        total_costs = annual_costs_per_ewe + total_lamb_costs

        # Net costs after wool credit
        net_costs = total_costs - wool_revenue

        # Breakeven per lamb
        if lambs_per_ewe > 0:
            breakeven_per_lamb = net_costs / lambs_per_ewe
        else:
            return {"error": "Lambs per ewe must be greater than 0"}

        # Breakeven per pound
        if lamb_weight > 0:
            breakeven_per_lb = breakeven_per_lamb / lamb_weight
        else:
            breakeven_per_lb = 0

        return {
            "breakeven_analysis": {
                "per_lamb": round(breakeven_per_lamb, 2),
                "per_pound": round(breakeven_per_lb, 2),
                "per_pound_live": round(breakeven_per_lb, 2),
                "per_cwt": round(breakeven_per_lb * 100, 2),
            },
            "inputs": {
                "annual_costs_per_ewe": annual_costs_per_ewe,
                "lambs_per_ewe": lambs_per_ewe,
                "lamb_weight": lamb_weight,
                "cost_per_lamb": cost_per_lamb,
                "wool_revenue": wool_revenue,
            },
            "interpretation": self._interpret_breakeven(breakeven_per_lb),
        }

    def _interpret_breakeven(self, breakeven_per_lb: float) -> str:
        """Interpret breakeven relative to typical market prices."""
        if breakeven_per_lb < 1.50:
            return "Competitive breakeven - well positioned for most markets"
        elif breakeven_per_lb < 2.00:
            return "Moderate breakeven - profitable in good markets"
        elif breakeven_per_lb < 2.50:
            return "High breakeven - requires premium markets or cost reduction"
        else:
            return "Very high breakeven - review costs and efficiency"

    def calculate_ram_roi(
        self,
        ram_cost: float,
        years_used: int,
        ewes_per_year: int,
        lamb_value_increase: float,
        lambs_per_ewe: float = 1.5,
    ) -> dict[str, Any]:
        """Calculate return on investment for a ram purchase.

        Args:
            ram_cost: Purchase price of ram
            years_used: Expected years of use
            ewes_per_year: Number of ewes bred per year
            lamb_value_increase: Additional value per lamb from superior genetics
            lambs_per_ewe: Average lambs marketed per ewe

        Returns:
            Dict with ROI analysis
        """
        # Total lambs sired
        total_lambs = ewes_per_year * lambs_per_ewe * years_used

        # Total value added
        total_value_added = total_lambs * lamb_value_increase

        # Annual cost of ram (depreciation)
        salvage_value = ram_cost * 0.2  # Assume 20% salvage
        annual_cost = (ram_cost - salvage_value) / years_used

        # Net benefit
        annual_benefit = (ewes_per_year * lambs_per_ewe * lamb_value_increase) - annual_cost
        total_net_benefit = total_value_added - (ram_cost - salvage_value)

        # ROI calculation
        if ram_cost > 0:
            roi_percent = ((total_value_added + salvage_value) / ram_cost - 1) * 100
        else:
            roi_percent = 0

        return {
            "roi_analysis": {
                "total_return": round(total_value_added + salvage_value, 2),
                "net_benefit": round(total_net_benefit, 2),
                "roi_percent": round(roi_percent, 1),
                "annual_benefit": round(annual_benefit, 2),
                "payback_years": (
                    round(ram_cost / (annual_benefit + annual_cost), 1)
                    if annual_benefit > 0
                    else "N/A"
                ),
            },
            "inputs": {
                "ram_cost": ram_cost,
                "years_used": years_used,
                "ewes_per_year": ewes_per_year,
                "lamb_value_increase": lamb_value_increase,
                "total_lambs_sired": round(total_lambs, 0),
            },
            "recommendation": self._roi_recommendation(roi_percent, annual_benefit),
        }

    def _roi_recommendation(self, roi_percent: float, annual_benefit: float) -> str:
        """Generate recommendation based on ROI."""
        if roi_percent > 100:
            return "Excellent investment - strong genetic value"
        elif roi_percent > 50:
            return "Good investment - solid returns expected"
        elif roi_percent > 0:
            return "Marginal investment - consider alternatives"
        else:
            return "Poor investment - genetics may not justify cost"

    def analyze_flock_profitability(
        self,
        ewe_count: int,
        lambs_marketed: int,
        avg_lamb_price: float,
        wool_revenue: float,
        cull_revenue: float,
        total_costs: float,
    ) -> dict[str, Any]:
        """Analyze overall flock profitability.

        Args:
            ewe_count: Number of ewes
            lambs_marketed: Total lambs sold
            avg_lamb_price: Average price per lamb
            wool_revenue: Total wool sales
            cull_revenue: Revenue from cull animals
            total_costs: Total annual operating costs

        Returns:
            Dict with profitability analysis
        """
        # Revenue breakdown
        lamb_revenue = lambs_marketed * avg_lamb_price
        total_revenue = lamb_revenue + wool_revenue + cull_revenue

        # Profit calculations
        gross_profit = total_revenue - total_costs
        profit_per_ewe = gross_profit / ewe_count if ewe_count > 0 else 0
        profit_margin = (gross_profit / total_revenue * 100) if total_revenue > 0 else 0

        # Productivity metrics
        lambs_per_ewe = lambs_marketed / ewe_count if ewe_count > 0 else 0
        revenue_per_ewe = total_revenue / ewe_count if ewe_count > 0 else 0
        cost_per_ewe = total_costs / ewe_count if ewe_count > 0 else 0

        return {
            "revenue": {
                "lamb_sales": round(lamb_revenue, 2),
                "wool": round(wool_revenue, 2),
                "culls": round(cull_revenue, 2),
                "total": round(total_revenue, 2),
            },
            "costs": {
                "total": round(total_costs, 2),
                "per_ewe": round(cost_per_ewe, 2),
            },
            "profitability": {
                "gross_profit": round(gross_profit, 2),
                "profit_per_ewe": round(profit_per_ewe, 2),
                "profit_margin": round(profit_margin, 1),
            },
            "productivity": {
                "lambs_per_ewe": round(lambs_per_ewe, 2),
                "revenue_per_ewe": round(revenue_per_ewe, 2),
            },
            "assessment": self._profitability_assessment(profit_per_ewe, profit_margin),
            "improvement_areas": self._identify_improvement_areas(
                lambs_per_ewe, cost_per_ewe, profit_margin
            ),
        }

    def _profitability_assessment(self, profit_per_ewe: float, margin: float) -> str:
        """Assess overall profitability."""
        if profit_per_ewe > 75 and margin > 20:
            return "Excellent - highly profitable operation"
        elif profit_per_ewe > 40 and margin > 10:
            return "Good - solid profitability"
        elif profit_per_ewe > 10 and margin > 0:
            return "Marginal - room for improvement"
        elif profit_per_ewe > 0:
            return "Breakeven - costs nearly equal revenue"
        else:
            return "Loss - costs exceed revenue, changes needed"

    def _identify_improvement_areas(
        self,
        lambs_per_ewe: float,
        cost_per_ewe: float,
        margin: float,
    ) -> list[str]:
        """Identify potential areas for improvement."""
        improvements = []

        if lambs_per_ewe < 1.3:
            improvements.append("Lamb crop below average (<1.3) - review breeding management")
        elif lambs_per_ewe < 1.5:
            improvements.append("Lamb crop moderate - evaluate ewe nutrition and ram fertility")

        if cost_per_ewe > 175:
            improvements.append("Costs above typical range - review feed, health, labor efficiency")

        if margin < 10:
            improvements.append("Thin margins - consider premium markets or cost reduction")

        if not improvements:
            improvements.append("Operation performing well across key metrics")

        return improvements

    def compare_marketing_options(
        self,
        weight: float,
        options: list[dict],
    ) -> dict[str, Any]:
        """Compare different marketing options for lambs.

        Args:
            weight: Lamb weight in pounds
            options: List of marketing options with name and price

        Returns:
            Dict with comparison and recommendations
        """
        if not options:
            # Use default options
            options = [
                {"name": "Auction", "price_per_lb": 1.80, "costs": 15},
                {"name": "Direct sale", "price_per_lb": 2.50, "costs": 5},
                {"name": "Freezer lamb", "price_per_cwt_carcass": 450, "yield": 0.50, "costs": 75},
            ]

        comparisons = []

        for opt in options:
            if "price_per_lb" in opt:
                gross = weight * opt["price_per_lb"]
            elif "price_per_cwt_carcass" in opt:
                carcass_weight = weight * opt.get("yield", 0.50)
                gross = carcass_weight / 100 * opt["price_per_cwt_carcass"]
            else:
                continue

            costs = opt.get("costs", 0)
            net = gross - costs

            comparisons.append(
                {
                    "option": opt.get("name", "Unknown"),
                    "gross_revenue": round(gross, 2),
                    "costs": costs,
                    "net_revenue": round(net, 2),
                    "net_per_lb": round(net / weight, 2) if weight > 0 else 0,
                }
            )

        # Sort by net revenue
        comparisons.sort(key=lambda x: x["net_revenue"], reverse=True)

        return {
            "lamb_weight": weight,
            "comparisons": comparisons,
            "recommendation": comparisons[0]["option"] if comparisons else "Unable to compare",
            "notes": [
                "Direct sales require more marketing effort but often higher returns",
                "Freezer lamb requires processing costs but captures retail value",
                "Auction provides market liquidity but typically lower prices",
            ],
        }

    def format_economics_advice(
        self,
        question: str,
        answer: str,
        data: dict | None = None,
    ) -> str:
        """Format economics advice in Shepherd style."""
        recommendations = []
        considerations = []

        if data:
            if "improvement_areas" in data:
                recommendations = data["improvement_areas"]
            if "assumptions" in data:
                considerations = data["assumptions"]
            if "notes" in data:
                considerations.extend(data["notes"])

        return format_shepherd_response(
            answer=answer,
            context=f"Question: {question}" if question else None,
            recommendations=recommendations if recommendations else None,
            considerations=considerations[:3] if considerations else None,
            sources=["USDA Market Data", "Extension Budget Templates"],
        )
