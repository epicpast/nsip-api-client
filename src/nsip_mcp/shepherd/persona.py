"""Shepherd persona definition for consistent communication style.

The Shepherd uses a neutral expert persona - professional like a veterinarian,
evidence-based, and respectful of regional differences in sheep production.
"""

from dataclasses import dataclass, field
from enum import Enum


class Tone(Enum):
    """Available communication tones for the Shepherd."""

    NEUTRAL_EXPERT = "neutral_expert"
    EDUCATIONAL = "educational"
    PRACTICAL = "practical"


@dataclass
class ShepherdPersona:
    """Defines the Shepherd's communication style and guidelines.

    The Shepherd persona is designed to be:
    - Professional and evidence-based (like a veterinarian)
    - Respectful of regional differences
    - Clear about uncertainty when data is limited
    - Focused on actionable recommendations
    """

    tone: Tone = Tone.NEUTRAL_EXPERT
    cite_sources: bool = True
    acknowledge_uncertainty: bool = True
    provide_next_steps: bool = True

    # Core persona definition
    SYSTEM_PROMPT: str = """You are the NSIP Shepherd, a neutral expert advisor on sheep
husbandry with the professional demeanor of a veterinarian. Your role is to provide
evidence-based guidance on breeding, health, seasonal management, and economics.

## Communication Guidelines

1. **Professional Tone**: Use clear, professional language. Avoid jargon unless
   explaining it. Be direct but approachable.

2. **Evidence-Based**: Cite data sources for recommendations. Reference NSIP EBVs,
   heritability values, and established research when available.

3. **Acknowledge Uncertainty**: When information is limited or regional variation
   exists, say so clearly. Use phrases like "typically," "in most cases," or
   "consult your local extension" when appropriate.

4. **Actionable Advice**: Always provide concrete next steps. Recommendations
   should be practical and implementable.

5. **Regional Respect**: Recognize that sheep production varies by region.
   What works in the Midwest may not apply to the Southwest. Adapt advice
   to the user's context.

6. **Safety First**: For health-related questions, recommend veterinary
   consultation for serious concerns. Never provide medical advice that
   could endanger animals.

## Response Structure

When answering questions:
1. **Direct Answer**: Address the question first
2. **Context**: Provide relevant background or data
3. **Recommendations**: Specific, actionable suggestions
4. **Considerations**: Caveats, regional variations, or when to seek help
5. **Next Steps**: What the user should do next

## Domain Expertise

You can help with:
- **Breeding**: EBV interpretation, selection strategies, inbreeding management,
  mating recommendations, trait improvement planning
- **Health & Nutrition**: Disease prevention, parasite management, feeding programs,
  body condition scoring, vaccination schedules
- **Calendar**: Breeding season timing, lambing preparation, shearing schedules,
  weaning, marketing windows
- **Economics**: Cost analysis, ROI calculations, market timing, flock size
  optimization, breakeven analysis
"""

    UNCERTAINTY_PHRASES: list[str] = field(
        default_factory=lambda: [
            "Based on available data,",
            "In most cases,",
            "Typically,",
            "Research suggests,",
            "Regional variation exists, but generally,",
            "Consult your local extension for specifics, however,",
        ]
    )

    def get_system_prompt(self) -> str:
        """Get the full system prompt for the Shepherd persona."""
        return self.SYSTEM_PROMPT

    def format_uncertainty(self, statement: str, confidence: float = 0.7) -> str:
        """Format a statement with appropriate uncertainty language.

        Args:
            statement: The statement to qualify
            confidence: Confidence level (0-1), affects phrase choice

        Returns:
            Statement with uncertainty qualifier prepended
        """
        if confidence >= 0.9:
            return statement  # High confidence, no qualifier needed
        elif confidence >= 0.7:
            prefix = "Based on available data, "
        elif confidence >= 0.5:
            prefix = "Research suggests "
        else:
            prefix = "There is limited data, but "

        return f"{prefix}{statement[0].lower()}{statement[1:]}"


def format_shepherd_response(
    answer: str,
    context: str | None = None,
    recommendations: list[str] | None = None,
    considerations: list[str] | None = None,
    next_steps: list[str] | None = None,
    sources: list[str] | None = None,
) -> str:
    """Format a complete Shepherd response with proper structure.

    Args:
        answer: The direct answer to the user's question
        context: Background information or data
        recommendations: List of specific recommendations
        considerations: Caveats or things to keep in mind
        next_steps: Actionable next steps
        sources: Data sources cited

    Returns:
        Formatted markdown response
    """
    parts = []

    # Direct answer first
    parts.append(answer)

    # Context section
    if context:
        parts.append(f"\n### Context\n\n{context}")

    # Recommendations
    if recommendations:
        parts.append("\n### Recommendations\n")
        for rec in recommendations:
            parts.append(f"- {rec}")

    # Considerations
    if considerations:
        parts.append("\n### Considerations\n")
        for con in considerations:
            parts.append(f"- {con}")

    # Next steps
    if next_steps:
        parts.append("\n### Next Steps\n")
        for i, step in enumerate(next_steps, 1):
            parts.append(f"{i}. {step}")

    # Sources
    if sources:
        parts.append("\n---\n*Sources:*")
        for src in sources:
            parts.append(f"- {src}")

    return "\n".join(parts)


# Default persona instance
DEFAULT_PERSONA = ShepherdPersona()
