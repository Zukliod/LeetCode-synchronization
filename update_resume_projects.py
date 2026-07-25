import os
import re
import requests

GITHUB_USERNAME = "zukliod"
RESUME_PATH = "resume.md"

def fetch_top_repos():
    url = f"https://api.github.com/users/{GITHUB_USERNAME}/repos?per_page=100&sort=updated"
    headers = {"Accept": "application/vnd.github.v3+json"}
    
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print(f"Failed to fetch repositories: {response.status_code}")
        return []

    repos = response.json()
    scored_repos = []

    for repo in repos:
        # Exclude forks, archived, or user profile repos
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
        if any(term in combined_text for term in ["mern", "react", "node", "mongo", "express"]):
            score += 50

        # Python / AI Boost
        if any(term in combined_text for term in ["python", "ai", "machine-learning", "ml", "pandas", "visualization"]):
            score += 40

        scored_repos.append({
            "name": name.replace("-", " ").replace("_", " ").title(),
            "description": description,
            "html_url": repo["html_url"],
            "homepage": repo.get("homepage"),
            "language": repo.get("language") or "Full-Stack",
            "score": score
        })

    # Sort descending by score and pick top 3
    scored_repos.sort(key=lambda x: x["score"], reverse=True)
    return scored_repos[:3]

def generate_markdown(projects):
    markdown_lines = []
    for proj in projects:
        title = f"**{proj['name']}**"
        links = f"[Source Code ({proj['language']})]({proj['html_url']})"
        
        if proj["homepage"]:
            links += f" | [Live Demo]({proj['homepage']})"
        
        markdown_lines.append(f"{title}  \n*{links}*")
        markdown_lines.append(f"* {proj['description']}\n")

    return "\n".join(markdown_lines)

def update_resume_file():
    if not os.path.exists(RESUME_PATH):
        print(f"Error: {RESUME_PATH} not found.")
        return

    top_projects = fetch_top_repos()
    if not top_projects:
        print("No eligible projects found.")
        return

    projects_md = generate_markdown(top_projects)

    with open(RESUME_PATH, "r", encoding="utf-8") as f:
        content = f.read()

    # Pattern to match the comment block
    pattern = r"(<!-- START_GITHUB_PROJECTS -->)(.*?)(<!-- END_GITHUB_PROJECTS -->)"
    replacement = f"\\1\n{projects_md}\n\\3"

    updated_content = re.sub(pattern, replacement, content, flags=re.DOTALL)

    with open(RESUME_PATH, "w", encoding="utf-8") as f:
        f.write(updated_content)

    print("resume.md updated successfully with top MERN & AI projects!")

if __name__ == "__main__":
    update_resume_file()
