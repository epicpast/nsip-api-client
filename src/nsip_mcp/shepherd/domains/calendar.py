"""Calendar domain for the Shepherd agent.

Provides expert guidance on:
- Seasonal management planning
- Breeding season timing
- Lambing preparation
- Shearing schedules
- Marketing windows
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any

from nsip_mcp.knowledge_base import (
    get_calendar_template,
    get_region_info,
)
from nsip_mcp.shepherd.persona import ShepherdPersona, format_shepherd_response


@dataclass
class CalendarDomain:
    """Calendar domain handler for the Shepherd agent.

    This domain provides expert guidance on seasonal management,
    task scheduling, and production cycle planning.
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
        response: dict[str, Any] = {"guidance": formatted_text, "domain": "calendar"}
        if metadata:
            response["metadata"] = metadata
        return response

    def get_seasonal_tasks(
        self,
        task_type: str,
        region: str | None = None,
        month: int | None = None,
    ) -> dict[str, Any]:
        """Get seasonal tasks for a specific activity type.

        Args:
            task_type: Type of task (breeding, lambing, shearing, health, general)
            region: Optional region for timing adjustments
            month: Optional month to filter tasks

        Returns:
            Dict with tasks and timing recommendations
        """
        calendar = get_calendar_template(task_type)
        region_info = get_region_info(region) if region else None

        if not calendar:
            calendar = self._default_calendar(task_type)

        result: dict[str, Any] = {
            "task_type": task_type,
            "tasks": [],
            "regional_adjustments": [],
        }

        # Add tasks from calendar
        tasks = calendar.get("tasks", [])
        for task in tasks:
            if isinstance(task, dict):
                task_entry = {
                    "name": task.get("name", "Task"),
                    "timing": task.get("timing", "As needed"),
                    "priority": task.get("priority", "moderate"),
                    "details": task.get("details", ""),
                }

                # Filter by month if specified
                if month:
                    timing = task.get("timing", "").lower()
                    month_names = [
                        "",
                        "january",
                        "february",
                        "march",
                        "april",
                        "may",
                        "june",
                        "july",
                        "august",
                        "september",
                        "october",
                        "november",
                        "december",
                    ]
                    if month <= 12 and month_names[month] not in timing:
                        # Check if it's a seasonal match
                        if not self._timing_matches_month(timing, month):
                            continue

                result["tasks"].append(task_entry)

        # Add regional adjustments
        if region_info:
            result["region"] = region_info.get("name", region)
            typical_lambing = region_info.get("typical_lambing", "varies")

            if task_type == "breeding":
                # Calculate breeding from lambing (5 months earlier)
                result["regional_adjustments"].append(
                    f"For {typical_lambing} lambing, breeding occurs approximately "
                    "5 months earlier"
                )
            elif task_type == "lambing":
                result["regional_adjustments"].append(f"Typical lambing season: {typical_lambing}")

            if "challenges" in region_info:
                result["regional_adjustments"].extend(
                    [f"Consider: {c}" for c in region_info["challenges"][:2]]
                )

        return result

    def _timing_matches_month(self, timing: str, month: int) -> bool:
        """Check if a timing string matches a given month."""
        seasons = {
            "spring": [3, 4, 5],
            "summer": [6, 7, 8],
            "fall": [9, 10, 11],
            "autumn": [9, 10, 11],
            "winter": [12, 1, 2],
        }

        for season, months in seasons.items():
            if season in timing.lower() and month in months:
                return True

        return "year-round" in timing.lower() or "ongoing" in timing.lower()

    def _default_calendar(self, task_type: str) -> dict[str, Any]:
        """Get default calendar for a task type."""
        defaults = {
            "breeding": {
                "tasks": [
                    {
                        "name": "Ram preparation",
                        "timing": "4-6 weeks before breeding",
                        "priority": "high",
                        "details": "Evaluate body condition, fertility testing, hoof trimming",
                    },
                    {
                        "name": "Ewe flushing",
                        "timing": "2-3 weeks before ram introduction",
                        "priority": "high",
                        "details": "Increase energy to improve ovulation rates",
                    },
                    {
                        "name": "Ram introduction",
                        "timing": "Based on desired lambing date",
                        "priority": "high",
                        "details": "1 ram per 25-35 ewes for natural breeding",
                    },
                    {
                        "name": "Breeding records",
                        "timing": "Throughout breeding",
                        "priority": "moderate",
                        "details": "Mark rams with crayon/paint, record mating dates",
                    },
                ],
            },
            "lambing": {
                "tasks": [
                    {
                        "name": "Pre-lambing vaccination",
                        "timing": "4 weeks before lambing",
                        "priority": "high",
                        "details": "CDT booster for passive immunity transfer",
                    },
                    {
                        "name": "Shearing/crutching",
                        "timing": "4-6 weeks before lambing",
                        "priority": "moderate",
                        "details": "Clean udder/dock area, easier lamb access",
                    },
                    {
                        "name": "Lambing supplies",
                        "timing": "2 weeks before",
                        "priority": "high",
                        "details": "Iodine, OB sleeves, colostrum, heat lamps, jugs",
                    },
                    {
                        "name": "Lambing area setup",
                        "timing": "1 week before",
                        "priority": "high",
                        "details": "Clean, dry, draft-free jugs prepared",
                    },
                    {
                        "name": "Newborn processing",
                        "timing": "Within 24 hours of birth",
                        "priority": "high",
                        "details": "Naval dip, colostrum, tag, weigh",
                    },
                ],
            },
            "shearing": {
                "tasks": [
                    {
                        "name": "Schedule shearer",
                        "timing": "2-3 months ahead",
                        "priority": "high",
                        "details": "Good shearers book up early",
                    },
                    {
                        "name": "Prepare shearing area",
                        "timing": "1 week before",
                        "priority": "moderate",
                        "details": "Clean, dry floor, good lighting",
                    },
                    {
                        "name": "Withhold feed",
                        "timing": "12-24 hours before shearing",
                        "priority": "moderate",
                        "details": "Reduces stress and prolapse risk",
                    },
                    {
                        "name": "Post-shearing housing",
                        "timing": "Immediately after shearing",
                        "priority": "high",
                        "details": "Shelter for 2-3 weeks if cold weather",
                    },
                ],
            },
            "health": {
                "tasks": [
                    {
                        "name": "Parasite monitoring",
                        "timing": "Spring through fall",
                        "priority": "high",
                        "details": "FAMACHA every 2-3 weeks, FECs monthly",
                    },
                    {
                        "name": "Hoof trimming",
                        "timing": "Quarterly or as needed",
                        "priority": "moderate",
                        "details": "More frequent in wet conditions",
                    },
                    {
                        "name": "CDT vaccination",
                        "timing": "Annual booster",
                        "priority": "high",
                        "details": "Pre-lambing for ewes, 6-8 weeks for lambs",
                    },
                    {
                        "name": "Body condition scoring",
                        "timing": "Monthly",
                        "priority": "moderate",
                        "details": "Target BCS 2.5-3.5 depending on stage",
                    },
                ],
            },
            "general": {
                "tasks": [
                    {
                        "name": "Pasture rotation",
                        "timing": "Ongoing",
                        "priority": "moderate",
                        "details": "Rest pastures 60+ days for parasite control",
                    },
                    {
                        "name": "Facility maintenance",
                        "timing": "Pre-season",
                        "priority": "moderate",
                        "details": "Check fencing, waterers, feeders",
                    },
                    {
                        "name": "Record keeping",
                        "timing": "Ongoing",
                        "priority": "moderate",
                        "details": "Update breeding, health, and performance records",
                    },
                ],
            },
        }
        return defaults.get(task_type, defaults["general"])

    def calculate_breeding_dates(
        self,
        target_lambing: str,
        gestation_days: int = 147,
    ) -> dict[str, Any]:
        """Calculate breeding timeline from target lambing date.

        Args:
            target_lambing: Target lambing date (YYYY-MM-DD or month name)
            gestation_days: Gestation length (default 147 days)

        Returns:
            Dict with calculated timeline
        """
        # Parse target date
        try:
            if "-" in target_lambing:
                lambing_date = datetime.strptime(target_lambing, "%Y-%m-%d")
            else:
                # Assume month name for current/next year
                month_map = {
                    "january": 1,
                    "february": 2,
                    "march": 3,
                    "april": 4,
                    "may": 5,
                    "june": 6,
                    "july": 7,
                    "august": 8,
                    "september": 9,
                    "october": 10,
                    "november": 11,
                    "december": 12,
                }
                month = month_map.get(target_lambing.lower(), 3)
                year = datetime.now().year
                if month < datetime.now().month:
                    year += 1
                lambing_date = datetime(year, month, 15)  # Mid-month

        except (ValueError, KeyError):
            return {
                "error": f"Could not parse date: {target_lambing}",
                "format_expected": "YYYY-MM-DD or month name",
            }

        # Calculate key dates
        breeding_start = lambing_date - timedelta(days=gestation_days)
        ram_prep = breeding_start - timedelta(days=42)  # 6 weeks before
        flushing_start = breeding_start - timedelta(days=21)  # 3 weeks before

        # Pregnancy milestones
        early_gestation_end = breeding_start + timedelta(days=30)
        mid_gestation_end = breeding_start + timedelta(days=100)
        late_gestation_start = lambing_date - timedelta(days=42)

        # Pre-lambing prep
        pre_lambing_vax = lambing_date - timedelta(days=28)
        lambing_setup = lambing_date - timedelta(days=7)

        timeline = {
            "target_lambing": lambing_date.strftime("%Y-%m-%d"),
            "gestation_days": gestation_days,
            "timeline": [
                {
                    "date": ram_prep.strftime("%Y-%m-%d"),
                    "event": "Ram preparation begins",
                    "days_before_lambing": (lambing_date - ram_prep).days,
                },
                {
                    "date": flushing_start.strftime("%Y-%m-%d"),
                    "event": "Begin flushing ewes",
                    "days_before_lambing": (lambing_date - flushing_start).days,
                },
                {
                    "date": breeding_start.strftime("%Y-%m-%d"),
                    "event": "Introduce rams",
                    "days_before_lambing": (lambing_date - breeding_start).days,
                },
                {
                    "date": early_gestation_end.strftime("%Y-%m-%d"),
                    "event": "Early gestation ends (pregnancy check possible)",
                    "days_before_lambing": (lambing_date - early_gestation_end).days,
                },
                {
                    "date": mid_gestation_end.strftime("%Y-%m-%d"),
                    "event": "Mid gestation ends",
                    "days_before_lambing": (lambing_date - mid_gestation_end).days,
                },
                {
                    "date": late_gestation_start.strftime("%Y-%m-%d"),
                    "event": "Late gestation begins (increase nutrition)",
                    "days_before_lambing": 42,
                },
                {
                    "date": pre_lambing_vax.strftime("%Y-%m-%d"),
                    "event": "Pre-lambing vaccination (CDT)",
                    "days_before_lambing": 28,
                },
                {
                    "date": lambing_setup.strftime("%Y-%m-%d"),
                    "event": "Lambing area ready, supplies stocked",
                    "days_before_lambing": 7,
                },
                {
                    "date": lambing_date.strftime("%Y-%m-%d"),
                    "event": "Target lambing date",
                    "days_before_lambing": 0,
                },
            ],
        }

        return timeline

    def get_marketing_windows(
        self,
        region: str | None = None,
        product_type: str = "market_lambs",
    ) -> dict[str, Any]:
        """Get optimal marketing windows.

        Args:
            region: Optional region for local market info
            product_type: Product type (market_lambs, breeding_stock, wool)

        Returns:
            Dict with marketing recommendations
        """
        windows = {
            "market_lambs": {
                "peak_demand": [
                    {
                        "period": "Easter (spring)",
                        "target_weight": "40-65 lbs",
                        "notes": "Highest prices for light lambs, ethnic markets",
                    },
                    {
                        "period": "Eid al-Adha (varies)",
                        "target_weight": "60-90 lbs",
                        "notes": "Major demand, date varies by lunar calendar",
                    },
                    {
                        "period": "Late fall (pre-Thanksgiving)",
                        "target_weight": "110-130 lbs",
                        "notes": "Good conventional market weights",
                    },
                ],
                "avoid": [
                    {"period": "Late summer", "reason": "Market flooded, prices typically lowest"}
                ],
                "strategies": [
                    "Sync lambing to hit holiday markets",
                    "Consider accelerated lambing for multiple crops",
                    "Direct sales often premium over auction",
                ],
            },
            "breeding_stock": {
                "peak_demand": [
                    {"period": "Late summer/early fall", "notes": "Before breeding season"},
                    {
                        "period": "Post-lambing (spring)",
                        "notes": "Buyers evaluating sire offspring",
                    },
                ],
                "strategies": [
                    "NSIP EBVs increase value for seedstock",
                    "Performance records essential",
                    "On-farm sales and consignment sales",
                ],
            },
            "wool": {
                "peak_demand": [
                    {"period": "Spring shearing", "notes": "Before lambing, longest staple"}
                ],
                "strategies": [
                    "Quality skirting increases value",
                    "Pool with cooperative for better prices",
                    "Consider specialty fiber markets",
                ],
            },
        }

        result: dict[str, Any] = {
            "product_type": product_type,
        }
        result.update(windows.get(product_type, windows["market_lambs"]))

        if region:
            region_info = get_region_info(region)
            if region_info:
                result["regional_notes"] = [
                    f"Typical lambing in {region_info.get('name', region)}: "
                    f"{region_info.get('typical_lambing', 'varies')}"
                ]

        return result

    def create_annual_calendar(
        self,
        lambing_month: int,
        region: str | None = None,
    ) -> dict[str, Any]:
        """Create a complete annual calendar based on lambing timing.

        Args:
            lambing_month: Month of lambing (1-12)
            region: Optional region for adjustments

        Returns:
            Dict with month-by-month task calendar
        """
        months = [
            "January",
            "February",
            "March",
            "April",
            "May",
            "June",
            "July",
            "August",
            "September",
            "October",
            "November",
            "December",
        ]

        # Calculate key months relative to lambing
        breeding_month = (lambing_month - 5 - 1) % 12 + 1
        late_gestation = (lambing_month - 2 - 1) % 12 + 1
        weaning_month = (lambing_month + 2 - 1) % 12 + 1

        calendar = {}

        for month_num in range(1, 13):
            month_name = months[month_num - 1]
            tasks = []

            if month_num == breeding_month:
                tasks.extend(
                    [
                        "Ram introduction",
                        "Breeding record keeping",
                        "Monitor for returns to heat",
                    ]
                )
            elif month_num == (breeding_month - 1 - 1) % 12 + 1:
                tasks.extend(
                    [
                        "Ram preparation and fertility check",
                        "Begin flushing ewes",
                    ]
                )

            if month_num == lambing_month:
                tasks.extend(
                    [
                        "LAMBING SEASON",
                        "Daily monitoring",
                        "Newborn processing",
                        "Colostrum management",
                    ]
                )
            elif month_num == late_gestation:
                tasks.extend(
                    [
                        "Increase ewe nutrition",
                        "Pre-lambing CDT vaccine",
                        "Shearing/crutching",
                    ]
                )
            elif month_num == (lambing_month - 1 - 1) % 12 + 1:
                tasks.extend(
                    [
                        "Prepare lambing area",
                        "Stock supplies",
                        "Late gestation nutrition",
                    ]
                )

            if month_num == weaning_month:
                tasks.extend(
                    [
                        "Weaning",
                        "Lamb vaccinations (CDT booster)",
                        "Sort and manage lamb groups",
                    ]
                )

            # Seasonal tasks
            if month_num in [3, 4, 5]:  # Spring
                tasks.append("Parasite monitoring begins/intensifies")
            elif month_num in [6, 7, 8]:  # Summer
                tasks.append("Peak parasite management")
            elif month_num in [9, 10, 11]:  # Fall
                tasks.append("Prepare for breeding/winter")
            else:  # Winter
                tasks.append("Facility maintenance, record review")

            calendar[month_name] = {
                "month": month_num,
                "tasks": tasks if tasks else ["Routine management"],
            }

        return {
            "lambing_month": months[lambing_month - 1],
            "breeding_month": months[breeding_month - 1],
            "weaning_month": months[weaning_month - 1],
            "calendar": calendar,
        }

    def format_calendar_advice(
        self,
        question: str,
        answer: str,
        data: dict | None = None,
    ) -> str:
        """Format calendar advice in Shepherd style."""
        recommendations = []
        next_steps = []

        if data:
            if "tasks" in data:
                for task in data["tasks"][:4]:
                    if isinstance(task, dict):
                        recommendations.append(
                            f"{task.get('name', 'Task')}: {task.get('timing', '')}"
                        )
            if "timeline" in data:
                for event in data["timeline"][:3]:
                    if isinstance(event, dict):
                        next_steps.append(f"{event.get('event', '')}: {event.get('date', '')}")

        return format_shepherd_response(
            answer=answer,
            context=f"Question: {question}" if question else None,
            recommendations=recommendations if recommendations else None,
            next_steps=next_steps if next_steps else None,
            sources=["NSIP Calendar Templates", "Regional Extension Guidelines"],
        )
