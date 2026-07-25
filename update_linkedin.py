import os
import requests
from datetime import datetime, timedelta, timezone

# 1. Access Credentials securely from environment variables
LINKEDIN_TOKEN = os.getenv("LINKEDIN_ACCESS_TOKEN")
AUTHOR_URN = os.getenv("LINKEDIN_AUTHOR_URN")
GITHUB_TOKEN = os.getenv("GH_TOKEN")
GEMINI_KEY = os.getenv("GEMINI_API_KEY")

# Type your exact GitHub username here so the API can find your profile
GITHUB_USERNAME = "Zukliod"

def get_recent_github_activity():
    """Fetches global public GitHub events from the last 24 hours."""
    if not GITHUB_USERNAME or not GITHUB_TOKEN:
        print("❌ Missing GitHub variables.")
        return None

    # FIXED: Correct, secure REST API endpoint for public user events
    url = f"https://github.com{GITHUB_USERNAME}/events/public"
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }
    
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

            # Counts any pushes (such as automated LeetHub or manual commits)
            if event["type"] == "PushEvent":
                leetcode_count += len(event["payload"].get("commits", []))
            # Catches freshly created public repositories
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

    raw_data_summary = f"Code commits pushed today: {leetcode_count}. New public repositories built: {new_projects}."
    
    url = f"https://googleapis.com{GEMINI_KEY}"
    headers = {"Content-Type": "application/json"}
    
    prompt = (
        f"You are a professional software engineer building in public on LinkedIn. "
        f"Rewrite the following technical activity metrics into an engaging, conversational, and inspiring LinkedIn post. "
        f"Talk naturally about consistency, algorithmic problem solving, software development, or growth. "
        f"Keep it brief, human-sounding, and well-spaced. Include exactly 3 relevant industry hashtags at the very bottom. "
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
            print(f"⚠️ Gemini Error: {response.status_code}")
            return None
    except Exception as e:
        print(f"⚠️ Failed to communicate with AI: {e}")
        return None

def publish_to_linkedin(message):
    """Posts final content payload to LinkedIn via official API endpoints."""
    # FIXED: Replaced standard homepage link with the official LinkedIn UGC Post Endpoint
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
    if response.status_code in:
        print("🚀 Success! Dynamic AI-generated post published to LinkedIn.")
    else:
        print(f"❌ LinkedIn Error {response.status_code}: {response.text}")

def main():
    print("Gathering developer statistics...")
    activity = get_recent_github_activity()
    if not activity:
        print("ℹ️ No recent activity tracked or error occurred. Exiting.")
        return
        
    leetcode_count, new_projects = activity
    if leetcode_count == 0 and not new_projects:
        print("😴 No updates tracked for today. Pipeline idling.")
        return

    print("Generating intelligent post copy via Gemini...")
    linkedin_message = generate_ai_caption(leetcode_count, new_projects)
    
    # Static Fallback structure if AI key fails or is empty
    if not linkedin_message:
        status_updates = []
        if leetcode_count > 0:
            status_updates.append(f"✅ Pushed {leetcode_count} code solutions and updates to GitHub.")
        if new_projects:
            status_updates.append(f"🛠️ Launched new repositories: {', '.join(new_projects)}.")
        linkedin_message = "📅 Daily Dev Progress Sync\n\n" + "\n".join(status_updates) + "\n\n#BuildInPublic"

    print(f"\nPublishing post content:\n-----\n{linkedin_message}\n-----\n")
    publish_to_linkedin(linkedin_message)

if __name__ == "__main__":
    main()
