import requests

from config import GEMINI_API_KEY
from utils import log, warning, error


def generate_linkedin_post(stats: dict) -> str | None:
    """
    Generate a professional LinkedIn Build-in-Public post.
    """

    if not GEMINI_API_KEY:
        warning("GEMINI_API_KEY not configured.")
        return None

    endpoint = (
        "https://generativelanguage.googleapis.com/v1beta/models/"
        f"gemini-2.5-flash:generateContent?key={GEMINI_API_KEY}"
    )

    prompt = f"""
Write a professional Build in Public LinkedIn post.

Keep it under 120 words.

Current Progress

Total Solved : {stats["totalSolved"]}

Easy : {stats["easySolved"]}

Medium : {stats["mediumSolved"]}

Hard : {stats["hardSolved"]}

Global Ranking : {stats["ranking"]}

Requirements

• Authentic tone

• Technical

• Growth mindset

• Add 2 relevant hashtags

• No emojis

• No marketing buzzwords
"""

    payload = {
        "contents": [
            {
                "parts": [
                    {
                        "text": prompt
                    }
                ]
            }
        ]
    }

    try:

        log("Generating LinkedIn content...")

        response = requests.post(
            endpoint,
            json=payload,
            timeout=15
        )

        response.raise_for_status()

        data = response.json()

        return (
            data["candidates"][0]
            ["content"]["parts"][0]["text"]
            .strip()
        )

    except Exception as e:

        error(f"Gemini Error : {e}")

        return None
