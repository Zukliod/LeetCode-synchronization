import os
import requests
from datetime import datetime, timedelta, timezone

# 1. Access Environment Variables (Set securely via GitHub Secrets)
LINKEDIN_TOKEN = os.getenv("LINKEDIN_ACCESS_TOKEN")
AUTHOR_URN = os.getenv("LINKEDIN_AUTHOR_URN")
GITHUB_TOKEN = os.getenv("GH_TOKEN")
GITHUB_USERNAME = os.getenv("GITHUB_REPOSITORY", "").split("/")[0]

def get_recent_github_activity():
    """Fetches GitHub events from the last 24 hours to find LeetCode or Project updates."""
    if not GITHUB_USERNAME or not GITHUB_TOKEN:
        print("❌ Missing GitHub configuration variables.")
        return None

    url = f"https://github.com{GITHUB_USERNAME}/events/public"
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    try:
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            print(f"❌ Failed to fetch GitHub events: {response.status_code}")
            return None
            
        events = response.json()
        time_threshold = datetime.now(timezone.utc) - timedelta(days=1)
        
        leetcode_count = 0
        new_projects = []

        for event in events:
            # Parse event timestamp
            created_at = datetime.strptime(event["created_at"], "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
            if created_at < time_threshold:
                continue # Skip events older than 24 hours

            repo_name = event["repo"]["name"].split("/")[-1]

            # Match LeetCode pushes (adjust 'leetcode' if your repo has a different name)
            if event["type"] == "PushEvent" and "leetcode" in repo_name.lower():
                # Count commits pushed
                leetcode_count += len(event["payload"].get("commits", []))
            
            # Match freshly created public repositories
            elif event["type"] == "CreateEvent" and event["payload"].get("ref_type") == "repository":
                if repo_name not in new_projects:
                    new_projects.append(repo_name)

        return leetcode_count, new_projects

    except Exception as e:
        print(f"❌ Error parsing GitHub Data: {e}")
        return None

def publish_to_linkedin(message):
    """Sends a clean POST request to LinkedIn's Restli API v2 to publish content."""
    # LinkedIn uses /v2/ugcPosts or /rest/posts depending on your specific app version
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
    
    if response.status_code in [201, 200]:
        print("🚀 Successfully published update to LinkedIn!")
    else:
        print(f"❌ LinkedIn API Error {response.status_code}: {response.text}")

def main():
    print("Checking daily developer metrics...")
    activity = get_recent_github_activity()
    
    if not activity:
        print("ℹ️ No recent activity tracked or error occurred. Exiting.")
        return
        
    leetcode_count, new_projects = activity
    
    # Construct update post text dynamically
    status_updates = []
    if leetcode_count > 0:
        status_updates.append(f"✅ Solved and synced {leetcode_count} problem(s) on LeetCode to sharpen my DSA skills.")
    if new_projects:
        projects_str = ", ".join([f"'{p}'" for p in new_projects])
        status_updates.append(f"🛠️ Launched a new open-source repository: {projects_str}.")

    if status_updates:
        bullet_points = "\n".join(status_updates)
        linkedin_message = (
            f"📅 Daily Dev Update\n\n"
            f"Here is what I accomplished today:\n"
            f"{bullet_points}\n\n"
            f"#BuildInPublic #GitHub #LeetCode #SoftwareEngineering"
        )
        print(f"Drafting post:\n---\n{linkedin_message}\n---")
        publish_to_linkedin(linkedin_message)
    else:
        print("😴 No updates found for today. Skipping LinkedIn post.")

if __name__ == "__main__":
    main()
