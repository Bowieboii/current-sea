"""A deterministic first micro-asset: possible ambiguity detection.

This deliberately uses transparent heuristics. It is cheap to invoke, easy to
test, and honest about its limits. Real usage can later tell us whether it
deserves descendants or replacement by a stronger method.
"""

from dataclasses import dataclass
import re


ASSET_ID = "ambiguity-scan"
ASSET_NAME = "Ambiguity Scan"
ASSET_VERSION = "0.1.0"
METHOD_VERSION = "deterministic-heuristics-v1"


@dataclass(frozen=True)
class Rule:
    code: str
    category: str
    pattern: re.Pattern[str]
    weight: int
    explanation: str
    clarification_question: str


RULES = (
    Rule(
        code="VAGUE_TIME",
        category="time",
        pattern=re.compile(
            r"\b(soon|later|eventually|sometime|recently|promptly|asap)\b",
            re.IGNORECASE,
        ),
        weight=20,
        explanation="The timing is relative rather than measurable.",
        clarification_question="What date, time, or deadline does this mean?",
    ),
    Rule(
        code="VAGUE_QUANTITY",
        category="quantity",
        pattern=re.compile(
            r"\b(some|several|many|few|enough|numerous|a lot)\b",
            re.IGNORECASE,
        ),
        weight=15,
        explanation="The amount is open to more than one interpretation.",
        clarification_question="What number, range, or threshold does this mean?",
    ),
    Rule(
        code="UNCERTAIN_COMMITMENT",
        category="commitment",
        pattern=re.compile(
            r"\b(maybe|perhaps|possibly|probably|might|could)\b",
            re.IGNORECASE,
        ),
        weight=15,
        explanation="The wording leaves the commitment or likelihood unstated.",
        clarification_question="Is this required, optional, or merely possible?",
    ),
    Rule(
        code="POSSIBLE_UNRESOLVED_REFERENCE",
        category="reference",
        pattern=re.compile(
            r"\b(this|that|it|they|them|these|those)\b",
            re.IGNORECASE,
        ),
        weight=25,
        explanation="The reference may not identify one specific subject or object.",
        clarification_question="What exact person, object, action, or idea is referenced?",
    ),
    Rule(
        code="SUBJECTIVE_THRESHOLD",
        category="standard",
        pattern=re.compile(
            r"\b(reasonable|normal|appropriate|effective|significant|better|best|quality)\b",
            re.IGNORECASE,
        ),
        weight=15,
        explanation="The standard depends on an unstated judge or criterion.",
        clarification_question="What observable criterion determines whether this standard is met?",
    ),
)


def scan_text(text: str) -> dict[str, object]:
    """Return explainable ambiguity signals and a deliberately simple score."""
    signals: list[dict[str, object]] = []
    score = 0

    for rule in RULES:
        for match in rule.pattern.finditer(text):
            signals.append(
                {
                    "code": rule.code,
                    "category": rule.category,
                    "phrase": match.group(0),
                    "start": match.start(),
                    "end": match.end(),
                    "explanation": rule.explanation,
                    "clarification_question": rule.clarification_question,
                }
            )
            score += rule.weight

    signals.sort(key=lambda signal: (int(signal["start"]), int(signal["end"])))
    bounded_score = min(100, score)

    return {
        "method": METHOD_VERSION,
        "ambiguous": bool(signals),
        "ambiguity_score": bounded_score,
        "signal_count": len(signals),
        "signals": signals,
        "limitation": (
            "This is a transparent wording heuristic, not proof that a statement "
            "is ambiguous. Context may resolve any flagged phrase."
        ),
    }

