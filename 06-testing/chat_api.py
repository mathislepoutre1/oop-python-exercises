"""FastAPI chat endpoint backed by Groq.

- the Groq client comes from a FastAPI dependency (`Depends(get_client)`), so tests can
  replace it with a mock
- the API key is read from the GROQ_API_KEY environment variable
- each Groq error is turned into an HTTP status (500 / 429 / 503)

Run it (from this folder):  uvicorn chat_api:app --reload   with GROQ_API_KEY set
"""
from __future__ import annotations

import os
from functools import lru_cache

import groq
from fastapi import Depends, FastAPI, HTTPException
from pydantic import BaseModel, Field

from groq_chat import MODEL

app = FastAPI(title="Chat API")


@lru_cache(maxsize=1)
def get_client() -> groq.Groq:
    """One shared client for the whole app, created on the first request."""
    return groq.Groq(api_key=os.environ.get("GROQ_API_KEY"), timeout=20.0, max_retries=1)


class Prompt(BaseModel):
    prompt: str = Field(min_length=1, max_length=4000)


class ChatResponse(BaseModel):
    response: str


@app.get("/status")
async def get_status() -> dict:
    return {"message": "OK"}


@app.post("/chat", response_model=ChatResponse)
async def post_chat(prompt: Prompt, client: groq.Groq = Depends(get_client)) -> ChatResponse:
    try:
        completion = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt.prompt},
            ],
        )
    except groq.APIConnectionError:
        raise HTTPException(status_code=500, detail="API Connection Error")
    except groq.RateLimitError:
        raise HTTPException(status_code=429, detail="Rate Limit Exceeded")
    except groq.APIStatusError as e:
        raise HTTPException(status_code=503, detail=f"Groq API error ({e.status_code})")
    return ChatResponse(response=completion.choices[0].message.content)
