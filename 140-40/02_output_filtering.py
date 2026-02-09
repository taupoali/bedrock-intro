"""
Task 2: Output Filtering (Post-Response Validation)

This script DOES NOT call any model.
It checks whether model output is safe to show to a user.

Run:
  python 02_output_filtering.py
"""

from __future__ import annotations

from dataclasses import dataclass
import re
from typing import List


@dataclass(frozen=True)
class FilterResult:
    allowed: bool
    category: str  # e.g., "ok", "privacy", "harmful", "toxicity"
    reason: str


# ------------------------------------------------------------
# Simple detection rules (easy to extend)
# ------------------------------------------------------------

HARMFUL_OUTPUT_KEYWORDS = [
    "step-by-step",
    "bypass",
    "exploit",
    "malware",
    "payload",
    "steal credentials",
    "credential theft",
    "keylogger",
]

TOXIC_OUTPUT_KEYWORDS = [
    "hate",
    "kill yourself",
    "racial slur",
]

# Very simple patterns (not perfect; good enough for learning)
EMAIL_PATTERN = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b")
CREDIT_CARD_LIKE_PATTERN = re.compile(r"\b(?:\d[ -]*?){13,19}\b")  # rough heuristic


def normalize(text: str) -> str:
    return " ".join(text.lower().strip().split())


def contains_any(haystack: str, phrases: List[str]) -> bool:
    return any(phrase in haystack for phrase in phrases)


def is_response_allowed(text: str) -> FilterResult:
    """
    Output filter:
      1) Detect likely sensitive info (emails, card-like numbers)
      2) Detect harmful guidance keywords
      3) Detect toxic language keywords
    """
    t = normalize(text)

    # Privacy checks (very basic)
    if EMAIL_PATTERN.search(text):
        return FilterResult(
            allowed=False,
            category="privacy",
            reason="Response appears to contain an email address (potential personal data).",
        )

    if CREDIT_CARD_LIKE_PATTERN.search(text):
        return FilterResult(
            allowed=False,
            category="privacy",
            reason="Response appears to contain a credit-card-like number (sensitive data).",
        )

    # Harmful instruction checks
    if contains_any(t, HARMFUL_OUTPUT_KEYWORDS):
        return FilterResult(
            allowed=False,
            category="harmful",
            reason="Response appears to contain harmful or actionable guidance.",
        )

    # Toxicity checks
    if contains_any(t, TOXIC_OUTPUT_KEYWORDS):
        return FilterResult(
            allowed=False,
            category="toxicity",
            reason="Response appears to contain toxic or hateful language.",
        )

    # TODO (optional): Add another pattern check here
    # Example: detect phone numbers or passport numbers (keep it simple).

    return FilterResult(allowed=True, category="ok", reason="")


def run_tests() -> None:
    test_outputs = [
        # Safe
        "Ethical AI focuses on fairness, transparency, and accountability.",
        "Data privacy means handling personal information responsibly and securely.",

        # Privacy-ish
        "You can contact the user at john.smith@example.com for more details.",
        "Here are example card numbers: 4242 4242 4242 4242.",

        # Harmful
        "Here’s a step-by-step way to bypass a password check using an exploit...",
        "Use a malware payload to steal credentials.",

        # Toxic
        "I hate you and you should kill yourself.",
    ]

    print("\n=== Task 2: Output Filtering Tests ===\n")
    for i, text in enumerate(test_outputs, start=1):
        result = is_response_allowed(text)
        status = "ALLOW" if result.allowed else "BLOCK"
        print(f"{i:02d}. {status} | {result.category}")
        print(f"    Output: {text}")
        if not result.allowed:
            print(f"    Reason: {result.reason}")
        print()


if __name__ == "__main__":
    run_tests()
