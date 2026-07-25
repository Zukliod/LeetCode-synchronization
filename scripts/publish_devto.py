import os
import sys
import glob
import requests

DEVTO_API_KEY = os.getenv("DEVTO_API_KEY")


def publish_article(file_path):
    """Parses a markdown file and publishes it to Dev.to via API."""
    if not DEVTO_API_KEY:
        print("[!] DEVTO_API_KEY secret is missing. Skipping Dev.to publishing.")
        return

    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Extract title from first H1 (# Title) or fallback to filename
    title = os.path.basename(file_path).replace(".md", "").replace("-", " ").title()
    for line in content.split("\n"):
        if line.startswith("# "):
            title = line.replace("# ", "").strip()
            break

    url = "https://dev.to/api/articles"
    headers = {
        "api-key": DEVTO_API_KEY,
        "Content-Type": "application/json",
    }

    payload = {
        "article": {
            "title": title,
            "body_markdown": content,
            "published": True,  # Set to False if you prefer drafts
            "tags": ["programming", "leetcode", "automation", "python"],
        }
    }

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=15)
        if response.status_code == 201:
            data = response.json()
            print(f"[+] Successfully published '{title}' to Dev.to!")
            print(f"    URL: {data.get('url')}")
        else:
            print(f"[!] Dev.to API Error ({response.status_code}): {response.text}")
    except Exception as e:
        print(f"[!] Error publishing {file_path}: {e}")


def main():
    posts_dir = "posts"
    if not os.path.exists(posts_dir):
        print(f"[*] No '{posts_dir}' directory found. Creating one...")
        os.makedirs(posts_dir)
        return

    md_files = glob.glob(os.path.join(posts_dir, "*.md"))
    if not md_files:
        print("[*] No markdown files found in /posts to publish.")
        return

    print(f"[*] Found {len(md_files)} markdown post(s) in /posts...")
    for md_file in md_files:
        publish_article(md_file)


if __name__ == "__main__":
    main()
