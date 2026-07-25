import os
import re
import json
import requests

# Secrets & Environment Variables
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
LINKEDIN_ACCESS_TOKEN = os.getenv("LINKEDIN_ACCESS_TOKEN")
LINKEDIN_AUTHOR_URN = os.getenv("LINKEDIN_AUTHOR_URN")
LEETCODE_USERNAME = os.getenv("LEETCODE_USERNAME", "zukliod")


def fetch_leetcode_stats(username):
    """Fetches real-time LeetCode statistics via open-source API."""
    url = f"https://leetcode-api-faisalshohag.vercel.app/{username}"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        return {
            "totalSolved": data.get("totalSolved", 0),
            "easySolved": data.get("easySolved", 0),
            "mediumSolved": data.get("mediumSolved", 0),
            "hardSolved": data.get("hardSolved", 0),
            "ranking": data.get("ranking", "N/A"),
        }
    except Exception as e:
        print(f"[!] Error fetching LeetCode stats: {e}")
        return None


def generate_linkedin_post(stats):
    """Generates a <120 word 'Build in Public' post using the Gemini API."""
    if not GEMINI_API_KEY:
        print("[!] GEMINI_API_KEY is missing.")
        return None

    endpoint = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={GEMINI_API_KEY}"
    
    prompt = f"""
    Write a short, professional, and inspiring 'Build in Public' LinkedIn post under 120 words.
    Current LeetCode Stats:
    - Total Solved: {stats['totalSolved']}
    - Easy: {stats['easySolved']} | Medium: {stats['mediumSolved']} | Hard: {stats['hardSolved']}
    - Global Ranking: {stats['ranking']}

    Tone: Authentic, technical, growth-oriented. Include 2 relevant hashtags. Do not use generic buzzwords.
    """

    payload = {
        "contents": [{"parts": [{"text": prompt}]}]
    }

    try:
        res = requests.post(endpoint, json=payload, timeout=15)
        res.raise_for_status()
        result = res.json()
        post_text = result["candidates"][0]["content"]["parts"][0]["text"].strip()
        return post_text
    except Exception as e:
        print(f"[!] Error generating AI post: {e}")
        return None


def post_to_linkedin(content):
    """Publishes text content to LinkedIn Feed using UGC Posts API."""
    if not LINKEDIN_ACCESS_TOKEN or not LINKEDIN_AUTHOR_URN:
        print("[!] LinkedIn credentials missing.")
        return False

    url = "https://api.linkedin.com/v2/ugcPosts"
    headers = {
        "Authorization": f"Bearer {LINKEDIN_ACCESS_TOKEN}",
        "Content-Type": "application/json",
        "X-Restli-Protocol-Version": "2.0.0",
    }

    payload = {
        "author": f"urn:li:person:{LINKEDIN_AUTHOR_URN}",
        "lifecycleState": "PUBLISHED",
        "specificContent": {
            "com.linkedin.ugc.ShareContent": {
                "shareCommentary": {"text": content},
                "shareMediaCategory": "NONE",
            }
        },
        "visibility": {"com.linkedin.ugc.ShareKeyValues": [{"projection": "PUBLIC"}]},
    }

    try:
        res = requests.post(url, headers=headers, json=payload, timeout=10)
        res.raise_for_status()
        print("[+] Successfully published to LinkedIn!")
        return True
    except Exception as e:
        print(f"[!] Error publishing to LinkedIn: {e}")
        return False


def update_resume_markdown(total_solved):
    """Updates the solved count in resume.md between hidden comment placeholders."""
    filename = "resume.md"
    if not os.path.exists(filename):
        print(f"[!] {filename} not found.")
        return

    with open(filename, "r", encoding="utf-8") as f:
        content = f.read()

    # Regex search between <!-- LEETCODE_START --> and <!-- LEETCODE_END -->
    pattern = r"(<!-- LEETCODE_START -->)(.*?)(<!-- LEETCODE_END -->)"
    replacement = f"\\1Solved {total_solved}+ algorithmic problems on LeetCode\\3"

    updated_content, count = re.subn(pattern, replacement, content, flags=re.DOTALL)

    if count > 0:
        with open(filename, "w", encoding="utf-8") as f:
            f.write(updated_content)
        print(f"[+] Updated {filename} with new count: {total_solved}")
    else:
        print("[!] Placeholders <!-- LEETCODE_START --> and <!-- LEETCODE_END --> not found in resume.md.")


def main():
    print("[*] Starting Daily Automation Pipeline...")
    stats = fetch_leetcode_stats(LEETCODE_USERNAME)
    
    if not stats:
        print("[!] Aborting due to missing stats.")
        return

    # Update Markdown Resume
    update_resume_markdown(stats["totalSolved"])

    # Generate & Post to LinkedIn
    post = generate_linkedin_post(stats)
    if post:
        print(f"--- Generated Post ---\n{post}\n----------------------")
        post_to_linkedin(post)


if __name__ == "__main__":
    main()
