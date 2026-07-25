import os
import re
import requests

GITHUB_USERNAME = "zukliod"
RESUME_PATH = "resume.md"

def fetch_top_repos():
    url = f"https://api.github.com/users/{GITHUB_USERNAME}/repos?per_page=100&sort=updated"
    headers = {"Accept": "application/vnd.github.v3+json", "User-Agent": "Resume-Updater"}
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code != 200:
            print(f"Warning: GitHub API returned status {response.status_code}")
            return []
        repos = response.json()
    except Exception as e:
        print(f"Error connecting to GitHub API: {e}")
        return []

    scored_repos = []

    for repo in repos:
        # Exclude forks, archived, or profile repos
        if repo.get("fork") or repo.get("archived") or repo["name"].lower() == GITHUB_USERNAME.lower():
            continue
        
        description = repo.get("description") or ""
        if not description:
            continue

        name = repo["name"]
        topics = repo.get("topics", [])
        combined_text = f"{name} {description} {' '.join(topics)}".lower()

        score = (repo.get("stargazers_count", 0) * 10) + (repo.get("forks_count", 0) * 5)

        # MERN Stack Boost
        if any(term in combined_text for term in ["mern", "react", "node", "mongo", "express", "typescript"]):
            score += 50

        # Python / AI Boost
        if any(term in combined_text for term in ["python", "ai", "machine-learning", "ml", "pandas", "ocr", "visualization"]):
            score += 40

        scored_repos.append({
            "name": name.replace("-", " ").replace("_", " ").title(),
            "description": description,
            "html_url": repo["html_url"],
            "homepage": repo.get("homepage"),
            "language": repo.get("language") or "Full-Stack",
            "score": score
        })

    # Sort descending by score and select top 3
    scored_repos.sort(key=lambda x: x["score"], reverse=True)
    return scored_repos[:3]

def generate_markdown(projects):
    if not projects:
        # Fallback default projects if API is unreachable
        return """**KESCO Substation Information System**  
*[Source Code (TypeScript)](https://github.com/zukliod)*
* Enterprise Substation Information System with RBAC, real-time asset dashboards, Excel imports, and automated reporting.

**KodeKalesh 2025 - AI Document Verification**  
*[Source Code (Python / React)](https://github.com/zukliod)*
* AI-powered legal document verification & summary platform using Python, OCR, NLP, React, and smart contract verification.

**Sports Event Management System**  
*[Source Code (Node.js)](https://github.com/zukliod)*
* Real-time Sports Event Management & Live Scoring System with Node.js, Express, Prisma ORM, Redis, and WebSockets."""

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
        print(f"Error: {RESUME_PATH} not found.")
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

    print("resume.md updated successfully!")

if __name__ == "__main__":
    update_resume_file()
