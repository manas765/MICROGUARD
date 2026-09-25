"""
Calls a model on Groq (free tier, rate-limited) to answer a question,
grounded strictly in the context built by context_builder.py.

Groq was chosen over a paid API specifically because it has a real
free tier - no billing required to test or run this feature.
"""

import os

from groq import Groq

MODEL = "llama-3.3-70b-versatile"

SYSTEM_PROMPT = """You are MICROGUARD's financial assistant, helping a microfinance borrower or loan officer understand their own loan, risk, and forecast data.

Rules you must follow:
- Answer ONLY using the data provided in the context below. Never invent, estimate, or guess a number that isn't explicitly given.
- If the answer requires information not present in the context, say plainly that you don't have that information, rather than guessing.
- Explain risk scores, stress scores, fraud flags, and loan health in plain, encouraging language a small-business owner can act on - not jargon.
- You are not a lawyer or licensed financial advisor. Explain what the numbers mean; don't give definitive legal or investment advice. Where a decision is genuinely the person's own call (e.g. whether to take a loan), lay out the relevant factors rather than telling them what to do.
- Keep answers concise - a few sentences, not an essay, unless the question genuinely needs more detail.
- If the question is unrelated to their loans, business finances, or this platform, politely redirect - you're scoped to their MICROGUARD data only.
"""


def ask_assistant(question: str, context: str) -> str:
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        return (
            "The AI assistant isn't configured yet - a GROQ_API_KEY environment "
            "variable needs to be set on the server."
        )

    client = Groq(api_key=api_key)

    completion = client.chat.completions.create(
        model=MODEL,
        max_tokens=500,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {
                "role": "user",
                "content": f"Here is the relevant data:\n\n{context}\n\nQuestion: {question}",
            },
        ],
    )

    return completion.choices[0].message.content