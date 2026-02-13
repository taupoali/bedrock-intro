from __future__ import annotations

from typing import Dict


def build_prompt(docs: Dict[str, str], user_question: str) -> str:
    """
    Simple “docs-in-prompt” grounding.
    Keep the prompt readable and force the assistant to stick to the provided docs.
    """

    # TODO (learner): Add one extra instruction to reduce hallucinations.
    # Example: "If the docs don't mention it, say 'Not covered in policy'."

    docs_block = []
    for filename, content in docs.items():
        docs_block.append(f"--- DOCUMENT: {filename} ---\n{content.strip()}\n")

    context = "\n".join(docs_block)

    return f"""
You are an internal IT support assistant.

Rules:
- Use ONLY the provided internal documents to answer.
- If the answer is not in the documents, say you don't know and suggest who to contact.
- Do not invent internal links, phone numbers, emails, or procedures.
- Keep answers concise and practical.
- Output format:
  1) Short answer (1-2 sentences)
  2) Steps (bullets)
  3) Escalation (who to contact if needed)

INTERNAL DOCUMENTS:
{context}

USER QUESTION:
{user_question}
""".strip()
