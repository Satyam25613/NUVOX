from __future__ import annotations

import os
import json
import asyncio
import logging
from google import genai

from utils.key_manager import get_next_key, mark_key_exhausted

logger = logging.getLogger("nuvox")

EVAL_PROMPT = """Analyze this interview transcript and return ONLY a JSON object.
No extra text. No markdown. No explanation. Just the JSON.

You MUST respond with ONLY a valid JSON object.
No markdown. No code fences. No explanation. Just JSON.
The JSON must contain EXACTLY these keys with EXACTLY
these names — no variations, no synonyms:

{
  "overall_score": <integer 1-10>,
  "communication_score": <integer 1-10>,
  "technical_score": <integer 1-10>,
  "confidence_score": <integer 1-10>,
  "strengths": [<string>, <string>],
  "improvements": [<string>, <string>],
  "feedback": "<string>",
  "topics_covered": [<string>],
  "recommendation": "<string — one of: Strong Hire, Hire, Maybe, No Hire>"
}

CRITICAL RULES:
- The key must be "feedback" NOT "overall_feedback"
- The key must be "improvements" NOT "areas_of_improvement"
- The key must be "overall_score" NOT "score" or "total_score"
- Every score must be an integer between 1 and 10
- strengths and improvements must each have at least 2 items
- Do not add any extra keys
- Do not nest any values

Transcript:
"""

# Models to try in order (fallback chain)
EVAL_MODELS = [
    "gemini-2.5-flash",
    "gemini-2.0-flash",
    "gemini-2.5-flash-lite",
    "gemini-2.0-flash-lite",
]


def normalize_report_keys(raw: dict) -> dict:
    # Handle common Gemini key name variations
    key_map = {
        "overall_feedback": "feedback",
        "general_feedback": "feedback",
        "summary": "feedback",
        "areas_of_improvement": "improvements",
        "improvement_areas": "improvements",
        "areas_for_improvement": "improvements",
        "score": "overall_score",
        "total_score": "overall_score",
        "final_score": "overall_score",
        "topics": "topics_covered",
        "subjects_covered": "topics_covered"
    }
    normalized = {}
    for key, value in raw.items():
        normalized_key = key_map.get(key, key)
        normalized[normalized_key] = value
    return normalized


async def generate_report(transcript: str) -> dict:
    """
    Send interview transcript to Gemini text API for evaluation.
    Retries with exponential backoff on rate limit (429) errors.
    Falls back to alternative models if primary is exhausted.

    Args:
        transcript: Full interview transcript (Q&A pairs)

    Returns:
        Dictionary with scores, feedback, improvements, and suggested topics

    Raises:
        ValueError: If all attempts fail
    """
    last_error = None

    for model in EVAL_MODELS:
        for attempt in range(3):
            current_key = get_next_key()
            client = genai.Client(api_key=current_key)
            prompt = EVAL_PROMPT + transcript
            
            try:
                logger.info(f"Report: attempt {attempt + 1} with model={model}")
                response = await client.aio.models.generate_content(
                    model=model,
                    contents=prompt,
                )
                result = parse_json_response(response.text)
                if result:
                    result = normalize_report_keys(result)
                    logger.info(f"✓ Report generated successfully with {model}")
                    return validate_report(result)
                else:
                    logger.warning(f"✗ Invalid JSON from {model}: {response.text[:200]}")

            except Exception as e:
                last_error = e
                error_str = str(e)
                logger.warning(f"✗ {model} attempt {attempt + 1} error: {type(e).__name__}: {error_str[:200]}")

                # Rate limit — wait and retry
                if "429" in error_str or "RESOURCE_EXHAUSTED" in error_str:
                    mark_key_exhausted(current_key)
                    # Extract retry delay if available, default to exponential backoff
                    wait_secs = 15 * (attempt + 1)  # 15s, 30s, 45s
                    logger.warning(f"Rate limited. Waiting {wait_secs}s before retry...")
                    await asyncio.sleep(wait_secs)
                    continue

                # Other errors — try next model immediately
                break

    # All models and retries exhausted — raise with details
    raise ValueError(f"Failed to generate report after trying all models. Last error: {last_error}")


def parse_json_response(text: str) -> dict | None:
    """Parse JSON from Gemini response, handling markdown code blocks."""
    if not text:
        return None

    # Strip markdown code block if present
    cleaned = text.strip()
    if cleaned.startswith("```json"):
        cleaned = cleaned[7:]
    elif cleaned.startswith("```"):
        cleaned = cleaned[3:]
    if cleaned.endswith("```"):
        cleaned = cleaned[:-3]
    cleaned = cleaned.strip()

    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        return None


def validate_report(data: dict) -> dict:
    """Validate and sanitize report data."""
    required_keys = [
        "overall_score", "communication_score", "technical_score",
        "confidence_score", "strengths", "improvements", 
        "feedback", "topics_covered", "recommendation"
    ]

    for key in required_keys:
        if key not in data:
            raise ValueError(f"Missing required field: {key}")

    # Clamp scores to 1-10
    for score_key in ["overall_score", "communication_score", "technical_score", "confidence_score"]:
        try:
            data[score_key] = max(1, min(10, int(data[score_key])))
        except (ValueError, TypeError):
            data[score_key] = 1

    # Ensure lists
    if not isinstance(data["strengths"], list):
        data["strengths"] = [str(data["strengths"])]
    if not isinstance(data["improvements"], list):
        data["improvements"] = [str(data["improvements"])]
    if not isinstance(data["topics_covered"], list):
        data["topics_covered"] = [str(data["topics_covered"])]

    return data

