"""Small Groq wrapper. The client can be passed in, so tests can use a fake one."""
from __future__ import annotations

from groq import Groq

MODEL = "llama-3.3-70b-versatile"


def ask_groq(question: str, client: Groq | None = None) -> str:
    """Send a question to Groq and return the answer."""
    if not question.strip():
        raise ValueError("Question cannot be empty")

    client = client or Groq()  # reads GROQ_API_KEY from the environment
    response = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": question}],
        max_tokens=1024,
    )
    return response.choices[0].message.content
