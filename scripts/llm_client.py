import time
import requests
from typing import Dict
from .config import (
    LLM_PROVIDER, OPENAI_API_KEY, OPENAI_MODEL, OPENAI_BASE_URL,
    ANTHROPIC_API_KEY, ANTHROPIC_MODEL, GEMINI_API_KEY, GEMINI_MODEL,
    LLM_MAX_OUTPUT_TOKENS, LLM_RETRY_MAX, LLM_RETRY_BASE_SECONDS
)

PROMPT_HEADER = (
    "You are a recruiting analyst. Given this JSON applicant profile, do four things:\n"
    "1. Provide a concise 75-word summary.\n"
    "2. Rate overall candidate quality from 1-10 (higher is better).\n"
    "3. List any data gaps or inconsistencies you notice.\n"
    "4. Suggest up to three follow-up questions to clarify gaps.\n\n"
    "Return exactly:\n"
    "Summary: <text>\n"
    "Score: <integer>\n"
    "Issues: <comma-separated list or 'None'>\n"
    "Follow-Ups: <bullet list>"
)

def call_llm(applicant_json_text: str) -> str:
    attempt = 0
    backoff = LLM_RETRY_BASE_SECONDS
    last_err = None
    while attempt < LLM_RETRY_MAX:
        try:
            if LLM_PROVIDER == "openai":
                return _openai_call(applicant_json_text)
            elif LLM_PROVIDER == "anthropic":
                return _anthropic_call(applicant_json_text)
            elif LLM_PROVIDER == "google":
                return _gemini_call(applicant_json_text)
            else:
                raise RuntimeError(f"Unsupported LLM_PROVIDER: {LLM_PROVIDER}")
        except Exception as e:
            last_err = e
            time.sleep(backoff)
            backoff *= 2
            attempt += 1
    raise RuntimeError(f"LLM call failed after {LLM_RETRY_MAX} attempts: {last_err}")

def _openai_call(applicant_json_text: str) -> str:
    url = f"{OPENAI_BASE_URL}/chat/completions"
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": OPENAI_MODEL,
        "messages": [
            {"role": "system", "content": "You are concise and precise."},
            {"role": "user", "content": PROMPT_HEADER + "\n\nJSON:\n" + applicant_json_text}
        ],
        "max_tokens": LLM_MAX_OUTPUT_TOKENS,
        "temperature": 0.2
    }
    resp = requests.post(url, headers=headers, json=data, timeout=60)
    resp.raise_for_status()
    j = resp.json()
    return j["choices"][0]["message"]["content"]

def _anthropic_call(applicant_json_text: str) -> str:
    url = "https://api.anthropic.com/v1/messages"
    headers = {
        "x-api-key": ANTHROPIC_API_KEY,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json"
    }
    data = {
        "model": ANTHROPIC_MODEL,
        "max_tokens": LLM_MAX_OUTPUT_TOKENS,
        "temperature": 0.2,
        "messages": [
            {"role": "user", "content": PROMPT_HEADER + "\n\nJSON:\n" + applicant_json_text}
        ]
    }
    resp = requests.post(url, headers=headers, json=data, timeout=60)
    resp.raise_for_status()
    j = resp.json()
    # Anthropic returns content as a list of blocks
    return "".join([b.get("text", "") for b in j.get("content", [])])

def _gemini_call(applicant_json_text: str) -> str:
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent?key={GEMINI_API_KEY}"
    headers = {"Content-Type": "application/json"}
    data = {
        "contents": [{
            "parts": [{"text": PROMPT_HEADER + "\n\nJSON:\n" + applicant_json_text}]
        }],
        "generationConfig": {
            "temperature": 0.2,
            "maxOutputTokens": LLM_MAX_OUTPUT_TOKENS
        }
    }
    resp = requests.post(url, headers=headers, json=data, timeout=60)
    resp.raise_for_status()
    j = resp.json()
    return j["candidates"][0]["content"]["parts"][0]["text"]
