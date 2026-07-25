import os
import re
import time
import requests
from datetime import datetime, timezone

GITHUB_USERNAME = "zukliod"

# Automatically resolve path to resume.md relative to this script
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
RESUME_PATH = os.path.join(SCRIPT_DIR, "resume.md")

# Strict guardrail blacklist (practice, automation, or meta repos)
EXCLUDED_PATTERNS = [
    "leetcode", "dsa", "practice", "blog", "tutorial", "exercise", 
    "assignment", "solution", "problem", "hacker-rank", "hackerrank",
    "zukliod", "linkedin-synchronization", "leetcode-synchronization"
]

# Major flagship projects automatically opted-in
FLAGSHIP_KEYWORDS = [
    "kesco", "kodekaleesh", "sports", "yantra", "ecoeducation", "sis"
]

def calculate_recency_score(updated_at_str):
    try:
        updated_time = datetime.fromisoformat(updated_at_str.replace("Z", "+00:00"))
        now = datetime.now(timezone.utc)
        days_ago = (now - updated_time).days

        if days_ago <= 7:
            return 100
        elif days_ago <= 30:
            return 80
        elif days_ago <= 90:
            return 60
        elif days_ago <= 180:
            return 40
        elif days_ago <= 365:
            return 20
        else:
            return 5
    except Exception:
        return 0

def fetch_top_repos():
    url = f"https://api.github.com/users/{GITHUB_USERNAME}/repos?per_page=100&sort=updated"
    headers = {"Accept": "application/vnd.github.v3+json", "User-Agent": "Resume-Updater"}
    
    repos = []
    for attempt in range(1, 4):
        try:
            print(f"Connecting to GitHub API (Attempt {attempt}/3)...")
            response = requests.get(url, headers=headers, timeout=15)
            if response.status_code == 200:
                repos = response.json()
                break
            else:
                print(f"Warning: GitHub API returned status {response.status_code}")
        except Exception as e:
            print(f"Network warning (Attempt {attempt}): {e}")
            time.sleep(2)

    if not repos:
        print("Network unavailable or API timed out. Proceeding with fallback project metadata...")
        return []

    scored_repos = []

    for repo in repos:
        raw_name = repo["name"].lower()
        normalized_name = raw_name.replace("_", "-")
        topics = repo.get("topics", [])

        # TIER 1 & TIER 2: OPT-IN & GUARDRAIL FILTERS
        if repo.get("fork") or repo.get("archived"):
            continue

        # Hard blacklist check
        if any(bad_pattern in normalized_name for bad_pattern in EXCLUDED_PATTERNS):
            continue

        # Check if project is explicitly opted-in (tagged with 'portfolio') OR matches flagship keywords
        is_opted_in = "portfolio" in topics or any(key in normalized_name for key in FLAGSHIP_KEYWORDS)
        
        # If it's not opted-in and lacks basic tech keywords, skip
        description = repo.get("description") or ""
        language = repo.get("language") or ""
        combined_text = f"{normalized_name} {description} {language} {' '.join(topics)}".lower()

        if not is_opted_in and not any(k in combined_text for k in ["mern", "react", "node", "python", "ai", "machine-learning"]):
            continue

        # TIER 3: HYBRID SCORING
        recency_score = calculate_recency_score(repo.get("updated_at", ""))
        
        stack_score = 0
        if "portfolio" in topics:
            stack_score += 200  # Explicit user tagging priority bonus

        if any(term in combined_text for term in ["mern", "react", "node", "express", "mongo", "prisma", "typescript", "full-stack"]):
            stack_score += 150

        if any(term in combined_text for term in ["python", "ai", "machine-learning", "ml", "ocr", "nlp", "pandas"]):
            stack_score += 120

        if repo.get("homepage"):
            stack_score += 80  # Live site bonus

        traction_score = (repo.get("stargazers_count", 0) * 10) + (repo.get("forks_count", 0) * 5)
        final_score = stack_score + recency_score + traction_score

        scored_repos.append({
            "name": repo["name"].replace("-", " ").replace("_", " ").title(),
            "description": description if description else "Full-stack software engineering application.",
            "html_url": repo["html_url"],
            "homepage": repo.get("homepage"),
            "language": repo.get("language") or "Full-Stack",
            "score": final_score
        })

    scored_repos.sort(key=lambda x: x["score"], reverse=True)
    return scored_repos[:3]

def generate_markdown(projects):
    if not projects:
        return """**KESCO Substation Information System**  
*[Source Code (TypeScript)](https://github.com/zukliod)*
* Enterprise Substation Information System for KESCO power discoms featuring RBAC, real-time asset dashboards, Excel imports, and automated reporting.

**KodeKalesh 2025 - AI Document Verification**  
*[Source Code (Python / React)](https://github.com/zukliod)*
* AI-powered legal document verification & summary platform using Python, OCR, NLP, React, and smart contract proof verification.

**Sports Event Management System**  
*[Source Code (TypeScript / Node.js)](https://github.com/zukliod)*
* Real-time Sports Event Management & Live Scoring System built with Node.js, Express, Prisma ORM, Redis, and WebSockets."""

    markdown_lines = []
    for proj in projects:
        title = f"**{proj['name']}**"
        links = f"[Source Code ({proj['language']})]({proj['html_url']})"
        
        if proj["homepage"]:
            links += f" | [Live Demo]({proj['homepage']})"
        
        markdown_lines.append(f"{title}  \n*{links}*\n* {proj['description']}\n")

    return "\n".join(markdown_lines)

def update_resume_file():
    if not os.path.exists(RESUME_PATH):
        print(f"Error: {RESUME_PATH} not found at {RESUME_PATH}")
        return

    top_projects = fetch_top_repos()
    projects_md = generate_markdown(top_projects)

    with open(RESUME_PATH, "r", encoding="utf-8") as f:
        content = f.read()

    pattern = r"(<!-- START_GITHUB_PROJECTS -->)(.*?)(<!-- END_GITHUB_PROJECTS -->)"
    replacement = f"\\1\n{projects_md}\n\\3"

    updated_content = re.sub(pattern, replacement, content, flags=re.DOTALL)

    with open(RESUME_PATH, "w", encoding="utf-8") as f:
        f.write(updated_content)

    print(f"Success: {RESUME_PATH} updated successfully using Optimum 3-Tier Curator!")

if __name__ == "__main__":
    update_resume_file()