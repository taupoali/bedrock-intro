"""
Task 3: Fallback Responses

This script DOES NOT call any model.
It returns consistent, safe messages when something is blocked.

Run:
  python 03_fallback_responses.py
"""

from __future__ import annotations


def fallback_message(category: str) -> str:
    """
    Return a safe, user-friendly fallback message.

    Note: We avoid telling the user exactly which keyword/pattern triggered the block.
    That’s deliberate: it reduces “gaming” the filter.
    """
    category = (category or "").strip().lower()

    if category == "privacy":
        return (
            "I can’t help with requests involving personal or sensitive data. "
            "If you want, rephrase without identifying details and I can help."
        )

    if category == "harmful":
        return (
            "I can’t assist with harmful or illegal instructions. "
            "If you want, I can explain safe, defensive best practices instead."
        )

    if category == "injection":
        return (
            "I can’t follow requests to ignore rules or reveal hidden instructions. "
            "Ask your question normally and I’ll do my best to help."
        )

    if category == "toxicity":
        return (
            "I can’t continue with abusive or hateful content. "
            "If you rephrase respectfully, I can help."
        )

    if category == "output_unsafe":
        return (
            "I’m not able to share that response. "
            "Try asking in a different way or request high-level, non-actionable information."
        )

    # TODO (optional): Add a new category message here, e.g. "medical" or "financial"

    return (
        "I can’t help with that request as written. "
        "Try rephrasing, and avoid personal data or harmful instructions."
    )


def run_demo() -> None:
    categories = ["privacy", "harmful", "injection", "toxicity", "output_unsafe", "unknown"]

    print("\n=== Task 3: Fallback Responses Demo ===\n")
    for c in categories:
        print(f"- Category: {c}")
        print(f"  Message : {fallback_message(c)}\n")


if __name__ == "__main__":
    run_demo()
