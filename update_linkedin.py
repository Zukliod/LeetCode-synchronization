import os
import requests
from datetime import datetime, timedelta, timezone

# 1. Access Credentials securely from environment variables
LINKEDIN_TOKEN = os.getenv("LINKEDIN_ACCESS_TOKEN")
AUTHOR_URN = os.getenv("LINKEDIN_AUTHOR_URN")
GITHUB_TOKEN = os.getenv("GH_TOKEN")
GEMINI_KEY = os.getenv("GEMINI_API_KEY")

# 2. Hardcoded profile username to guarantee zero parsing issues
GITHUB_USERNAME = "Zukliod"

def get_recent_github_activity():
    """Fetches global public GitHub events from the last 24 hours."""
    url = f"https://github.com{GITHUB_USERNAME}/events/public"
    headers = {
        "Accept": "application/vnd.github.v3+json"
    }
    # Pass token to increase rate limit ceiling
    if GITHUB_TOKEN:
        headers["Authorization"] = f"token {GITHUB_TOKEN}"
    
    try:
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            print(f"❌ GitHub API Error {response.status_code}: {response.text}")
            return None
            
        events = response.json()
        time_threshold = datetime.now(timezone.utc) - timedelta(days=1)
        
        leetcode_count = 0
        new_projects = []

        for event in events:
            created_at = datetime.strptime(event["created_at"], "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
            if created_at < time_threshold:
                continue

            repo_name = event["repo"]["name"].split("/")[-1]

            # Tracks pushes into your public repositories (including LeetHub updates)
            if event["type"] == "PushEvent":
                leetcode_count += len(event["payload"].get("commits", []))
            # Tracks any freshly initialized projects
            elif event["type"] == "CreateEvent" and event["payload"].get("ref_type") == "repository":
                if repo_name not in new_projects:
                    new_projects.append(repo_name)

        return leetcode_count, new_projects
    except Exception as e:
        print(f"❌ Error collecting metrics: {e}")
        return None

def generate_ai_caption(leetcode_count, new_projects):
    """Uses Gemini API to rewrite plain statistics into an organic engineering post."""
    if not GEMINI_KEY:
        print("⚠️ Gemini Key missing. Falling back to basic formatting.")
        return None

    raw_data_summary = f"Code commits pushed today: {leetcode_count}. New repositories created: {new_projects}."
    
    url = f"https://googleapis.com{GEMINI_KEY}"
    headers = {"Content-Type": "application/json"}
    
    prompt = (
        f"You are a professional software engineer building in public on LinkedIn. "
        f"Rewrite the following data metrics into an engaging, conversational, and inspiring LinkedIn post. "
        f"Talk naturally about consistency, programming growth, computer science fundamentals, or problem-solving. "
        f"Keep it brief and well-spaced. Include exactly 3 relevant tech hashtags at the very bottom. "
        f"Raw data to format: {raw_data_summary}"
    )

    payload = {
        "contents": [{
            "parts": [{"text": prompt}]
        }]
    }

    try:
        response = requests.post(url, headers=headers, json=payload)
        if response.status_code == 200:
            res_json = response.json()
            ai_text = res_json['candidates']['content']['parts']['text']
            return ai_text.strip()
        else:
            print(f"⚠️ Gemini API Status Code Error: {response.status_code}")
            return None
    except Exception as e:
        print(f"⚠️ Failed to communicate with AI: {e}")
        return None

def publish_to_linkedin(message):
    """Posts final content payload to LinkedIn via official API endpoints."""
    api_url = "https://linkedin.com"
    headers = {
        "Authorization": f"Bearer {LINKEDIN_TOKEN}",
        "Content-Type": "application/json",
        "X-Restli-Protocol-Version": "2.0.0"
    }
    
    payload = {
        "author": f"urn:li:person:{AUTHOR_URN}",
        "lifecycleState": "PUBLISHED",
        "specificContent": {
            "com.linkedin.ugc.ShareContent": {
                "shareCommentary": {"text": message},
                "shareMediaCategory": "NONE"
            }
        },
        "visibility": {"com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"}
    }
    
    response = requests.post(api_url, json=payload, headers=headers)
    
    # FIXED: Handled list numbers inside python natively without structural collapse
    success_status_codes = [200, 201]
    if response.status_code in success_status_codes:
        print("🚀 Success! Dynamic AI-generated post published to LinkedIn.")
    else:
        print(f"❌ LinkedIn Error {response.status_code}: {response.text}")

def main():
    print("Gathering public developer statistics...")
    activity = get_recent_github_activity()
    if not activity:
        return
        
    leetcode_count, new_projects = activity
    if leetcode_count == 0 and not new_projects:
        print("😴 No public updates tracked for today. Pipeline idling.")
        return

    print("Generating intelligent post copy via Gemini...")
    linkedin_message = generate_ai_caption(leetcode_count, new_projects)
    
    # Fallback configuration structure if AI key fails
    if not linkedin_message:
        status_updates = []
        if leetcode_count > 0:
            status_updates.append(f"✅ Completed {leetcode_count} code solutions and pushed them to GitHub.")
        if new_projects:
            status_updates.append(f"🛠️ Launched new repositories: {', '.join(new_projects)}.")
        linkedin_message = "📅 Daily Dev Progress Sync\n\n" + "\n".join(status_updates) + "\n\n#BuildInPublic"

    print(f"\nPublishing post content:\n-----\n{linkedin_message}\n-----\n")
    publish_to_linkedin(linkedin_message)

if __name__ == "__main__":
    main()
