import os
import re
import json
import requests
import markdown
from xhtml2pdf import pisa

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
        print("[!] GEMINI_API_KEY is missing. Skipping post generation.")
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

    payload = {"contents": [{"parts": [{"text": prompt}]}]}

    try:
        res = requests.post(endpoint, json=payload, timeout=15)
        res.raise_for_status()
        result = res.json()
        return result["candidates"][0]["content"]["parts"][0]["text"].strip()
    except Exception as e:
        print(f"[!] Error generating AI post: {e}")
        return None


def post_to_linkedin(content):
    """Publishes text content to LinkedIn Feed using UGC Posts API."""
    if not LINKEDIN_ACCESS_TOKEN or not LINKEDIN_AUTHOR_URN:
        print("[!] LinkedIn credentials missing. Skipping publishing.")
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
        return ""

    with open(filename, "r", encoding="utf-8") as f:
        content = f.read()

    pattern = r"(<!-- LEETCODE_START -->)(.*?)(<!-- LEETCODE_END -->)"
    replacement = f"\\1Solved {total_solved}+ algorithmic problems on LeetCode\\3"

    updated_content, count = re.subn(pattern, replacement, content, flags=re.DOTALL)

    if count > 0:
        with open(filename, "w", encoding="utf-8") as f:
            f.write(updated_content)
        print(f"[+] Updated {filename} with new count: {total_solved}")
        return updated_content
    else:
        print("[!] LeetCode placeholders not found in resume.md.")
        return content


def compile_pdf_variant(md_content, output_pdf, title_role, filter_type):
    """Filters markdown and compiles an ATS-compliant single-column PDF variant."""
    content = md_content

    # Role-specific content filtering using HTML comments
    if filter_type == "fullstack":
        # Remove backend-only sections
        content = re.sub(r"<!-- BACKEND_ONLY_START -->.*?<!-- BACKEND_ONLY_END -->", "", content, flags=re.DOTALL)
        # Keep fullstack sections clean
        content = content.replace("<!-- FULLSTACK_ONLY_START -->", "").replace("<!-- FULLSTACK_ONLY_END -->", "")
    elif filter_type == "backend":
        # Remove fullstack-only sections
        content = re.sub(r"<!-- FULLSTACK_ONLY_START -->.*?<!-- FULLSTACK_ONLY_END -->", "", content, flags=re.DOTALL)
        # Keep backend sections clean
        content = content.replace("<!-- BACKEND_ONLY_START -->", "").replace("<!-- BACKEND_ONLY_END -->", "")

    # Clean up any leftover placeholders
    content = re.sub(r"<!-- LEETCODE_START -->|<!-- LEETCODE_END -->", "", content)

    html_content = markdown.markdown(content, extensions=['tables'])

    pdf_template = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <style>
            @page {{
                size: letter;
                margin: 0.5in;
            }}
            body {{
                font-family: Helvetica, Arial, sans-serif;
                font-size: 10pt;
                line-height: 1.4;
                color: #111111;
            }}
            h1 {{ font-size: 18pt; margin-bottom: 2px; text-transform: uppercase; }}
            .role-title {{ font-size: 11pt; font-weight: bold; color: #333333; margin-bottom: 8px; }}
            h2 {{ font-size: 12pt; border-bottom: 1px solid #333; margin-top: 12px; margin-bottom: 6px; text-transform: uppercase; }}
            h3 {{ font-size: 10pt; margin-top: 6px; margin-bottom: 2px; }}
            ul {{ margin-top: 2px; margin-bottom: 6px; padding-left: 18px; }}
            li {{ margin-bottom: 2px; }}
            p {{ margin-top: 2px; margin-bottom: 4px; }}
        </style>
    </head>
    <body>
        {html_content}
    </body>
    </html>
    """

    with open(output_pdf, "wb") as pdf_file:
        pisa.CreatePDF(pdf_template, dest=pdf_file)
    print(f"[+] Compiled variant: {output_pdf}")


def main():
    print("[*] Starting Daily Automation Pipeline...")
    stats = fetch_leetcode_stats(LEETCODE_USERNAME)
    
    if not stats:
        print("[!] Aborting due to missing stats.")
        return

    # 1. Update Markdown Master File
    updated_md = update_resume_markdown(stats["totalSolved"])

    # 2. Compile PDF Variants
    if updated_md:
        compile_pdf_variant(updated_md, "Harshit_FullStack_Resume.pdf", "Full-Stack Engineer", "fullstack")
        compile_pdf_variant(updated_md, "Harshit_Backend_Resume.pdf", "Backend & Automation Engineer", "backend")

    # 3. Generate & Post to LinkedIn
    post = generate_linkedin_post(stats)
    if post:
        print(f"--- Generated Post ---\n{post}\n----------------------")
        post_to_linkedin(post)


if __name__ == "__main__":
    main()
