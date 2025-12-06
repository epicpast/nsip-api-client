#!/usr/bin/env python3
"""
Prompt Analyzer Hook (UserPromptSubmit)
Detect LPN IDs, query intent, and comparative analysis opportunities in user prompts.
Merged from: smart_search_detector.py + comparative_analyzer.py
"""

import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List

# Add script directory to path for sibling module imports
sys.path.insert(0, str(Path(__file__).parent))

from _config import config
from nsip_types import UserPromptSubmitInput, HookOutput
from _validation import LPNValidator
from _exceptions import PromptAnalysisError


class PromptAnalyzer:
    """Analyze user prompts for LPN IDs, intent, and comparison opportunities."""

    def __init__(self):
        """Initialize prompt analyzer."""
        config.LOG_DIR.mkdir(parents=True, exist_ok=True)
        self.log_file = config.LOG_DIR / "prompt_analysis.jsonl"
        self.validator = LPNValidator()

        # Intent detection keywords
        self.intent_keywords = {
            "search_animal": ["search", "find", "look for", "locate"],
            "get_lineage": ["lineage", "pedigree", "parents", "ancestors", "family"],
            "get_progeny": ["progeny", "offspring", "children", "descendants"],
            "compare_traits": ["compare", "comparison", "versus", "vs", "difference"],
            "trait_analysis": [
                "trait", "ebv", "breeding value", "weight", "wool",
                "parasite", "resistance", "muscle", "fat"
            ]
        }

        # Comparison indicators
        self.comparison_keywords = [
            "compare", "comparison", "versus", "vs", "vs.", "v.",
            "better", "worse", "difference", "between",
            "which", "best", "superior", "prefer",
            "against", "relative to", "compared to"
        ]

        self.multiple_indicators = [
            "animals", "sheep", "rams", "ewes",
            "these", "those", "both", "all",
            "multiple", "several", "few", "pair"
        ]

        # Trait focus keywords
        self.trait_keywords = {
            "weight": ["weight", "wwt", "pwwt", "ywt"],
            "wool": ["wool", "fleece", "fiber", "micron", "cfw"],
            "meat": ["meat", "muscle", "carcass", "eye muscle", "fat"],
            "parasite": ["parasite", "worm", "fec", "wec", "resistance"],
            "growth": ["growth", "gain", "rate"],
            "reproduction": ["reproduction", "lambing", "fertility", "nlb", "nlw"]
        }

    def _log_analysis(self, entry: dict) -> None:
        """Log analysis to JSONL file."""
        try:
            with open(self.log_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(entry) + "\n")
        except OSError:
            pass

    def _detect_query_intent(self, text: str) -> Dict[str, bool]:
        """Detect user's query intent from text."""
        text_lower = text.lower()
        return {
            intent: any(kw in text_lower for kw in keywords)
            for intent, keywords in self.intent_keywords.items()
        }

    def _detect_comparison_intent(self, text: str) -> bool:
        """Detect if user intends to compare animals."""
        text_lower = text.lower()
        has_comparison = any(kw in text_lower for kw in self.comparison_keywords)
        has_multiple = any(ind in text_lower for ind in self.multiple_indicators)
        return has_comparison or has_multiple

    def _detect_trait_focus(self, text: str) -> List[str]:
        """Detect which trait categories the user is interested in."""
        text_lower = text.lower()
        return [
            category
            for category, keywords in self.trait_keywords.items()
            if any(kw in text_lower for kw in keywords)
        ]

    def _build_suggestion_message(
        self,
        detected_ids: List[str],
        intents: Dict[str, bool],
        has_comparison: bool,
        trait_focus: List[str]
    ) -> str:
        """Build context message with suggestions."""
        lines = []

        # LPN ID detection
        if detected_ids:
            if len(detected_ids) == 1:
                lines.append(f"Detected LPN ID: {detected_ids[0]}")
            else:
                lines.append(f"Detected {len(detected_ids)} LPN IDs: {', '.join(detected_ids)}")

        # Intent-based suggestions
        if detected_ids:
            if intents.get("get_lineage"):
                lines.append("Suggested: nsip_get_lineage for ancestry/pedigree")
            elif intents.get("get_progeny"):
                lines.append("Suggested: nsip_get_progeny for offspring")
            elif has_comparison and len(detected_ids) > 1:
                lines.append("Suggested: nsip_get_animal for each ID, then compare traits")
                if trait_focus:
                    lines.append(f"Focus traits: {', '.join(trait_focus)}")
            else:
                lines.append("Suggested: nsip_get_animal or nsip_search_by_lpn")

        elif intents.get("trait_analysis"):
            lines.append("Suggested: nsip_search_animals with trait criteria")

        return "\n".join(lines) if lines else ""

    def analyze(self, prompt: str) -> Dict:
        """
        Analyze user prompt for LPN IDs, intent, and comparison opportunities.

        Args:
            prompt: User prompt text

        Returns:
            Analysis metadata including suggestions
        """
        # Extract and validate LPN IDs
        detected_ids = self.validator.extract_from_text(prompt)

        # Detect intents
        intents = self._detect_query_intent(prompt)
        has_comparison = self._detect_comparison_intent(prompt)
        trait_focus = self._detect_trait_focus(prompt)

        # Log analysis
        if detected_ids or any(intents.values()) or has_comparison:
            self._log_analysis({
                "timestamp": datetime.now().isoformat(),
                "detected_ids": detected_ids,
                "intents": {k: v for k, v in intents.items() if v},
                "comparison_intent": has_comparison,
                "trait_focus": trait_focus,
                "prompt_length": len(prompt)
            })

        # Build suggestion message
        suggestion = self._build_suggestion_message(
            detected_ids, intents, has_comparison, trait_focus
        )

        return {
            "analysis_performed": True,
            "ids_detected": len(detected_ids),
            "detected_ids": detected_ids,
            "intents": intents,
            "comparison_intent": has_comparison,
            "trait_focus": trait_focus,
            "suggestion_message": suggestion
        }


def main():
    """Process UserPromptSubmit hook for prompt analysis."""
    try:
        hook_data: UserPromptSubmitInput = json.loads(sys.stdin.read())
        prompt = hook_data.get("prompt", "")

        if not prompt:
            output: HookOutput = {
                "continue": True,
                "metadata": {"analysis_performed": False, "reason": "Empty prompt"}
            }
            print(json.dumps(output))
            sys.exit(0)

        analyzer = PromptAnalyzer()
        analysis = analyzer.analyze(prompt)

        output: HookOutput = {
            "continue": True,
            "metadata": analysis
        }

        if analysis.get("suggestion_message"):
            output["context"] = analysis["suggestion_message"]

        print(json.dumps(output))

    except json.JSONDecodeError as e:
        output: HookOutput = {
            "continue": True,
            "metadata": {"analysis_performed": False, "error": f"Invalid JSON: {e}"}
        }
        print(json.dumps(output))

    except PromptAnalysisError as e:
        output: HookOutput = {
            "continue": True,
            "metadata": {"analysis_performed": False, "error": str(e)}
        }
        print(json.dumps(output))

    except Exception as e:
        # Catch-all for any unexpected errors - always continue (fail-safe)
        output: HookOutput = {
            "continue": True,
            "metadata": {"analysis_performed": False, "error": str(e)}
        }
        print(json.dumps(output))

    sys.exit(0)


if __name__ == "__main__":
    main()
