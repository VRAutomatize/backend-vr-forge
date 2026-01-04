"""Quality engine for validating dataset items."""

from typing import Any, Optional

from app.core.logging import get_logger

logger = get_logger(__name__)


class QualityEngine:
    """Service for quality validation of dataset items."""

    @staticmethod
    def validate_item(
        instruction: str,
        ideal_response: str,
        input_text: Optional[str] = None,
    ) -> tuple[float, dict[str, Any]]:
        """Validate dataset item quality.

        Args:
            instruction: Instruction text
            ideal_response: Ideal response text
            input_text: Input text (optional)

        Returns:
            Tuple of (quality_score, quality_flags)
        """
        flags: dict[str, Any] = {}
        score = 1.0

        # Check minimum lengths
        if len(instruction) < 10:
            flags["short_instruction"] = True
            score -= 0.1

        if len(ideal_response) < 20:
            flags["short_response"] = True
            score -= 0.2

        # Check for empty or whitespace-only
        if not instruction.strip():
            flags["empty_instruction"] = True
            score = 0.0

        if not ideal_response.strip():
            flags["empty_response"] = True
            score = 0.0

        # Check for suspicious patterns
        if ideal_response.lower() == instruction.lower():
            flags["identical_content"] = True
            score -= 0.3

        # Normalize score
        score = max(0.0, min(1.0, score))

        return score, flags

