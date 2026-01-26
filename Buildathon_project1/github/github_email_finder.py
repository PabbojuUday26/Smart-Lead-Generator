import requests
import os
from dotenv import load_dotenv
from core.csv_manager import save_to_csv

load_dotenv()

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

headers = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Accept": "application/vnd.github+json"
}

def search_users(query="python", max_results=20, page=1):
    # Determine if query looks like a specific qualifier (has :) or just a keyword
    if ":" in query:
        q_param = query
    else:
        # Default to searching text matches in user profiles (bio, location, etc) or language if single word
        # For broader result, we'll just pass the query directly to 'q'
        q_param = query
    
    url = f"https://api.github.com/search/users?q={q_param}&per_page={max_results}&page={page}"
    res = requests.get(url, headers=headers)
    return res.json().get("items", [])

def get_public_email(username):
    profile = requests.get(f"https://api.github.com/users/{username}", headers=headers).json()
    if profile.get("email"):
        return profile["email"]

    response = requests.get(f"https://api.github.com/users/{username}/public", headers=headers)
    if response.status_code != 200:
        return None
        
    events = response.json()
    if not isinstance(events, list):
        return None

    for event in events:
        if isinstance(event, dict) and event.get("type") == "PushEvent":
            payload = event.get("payload", {})
            for commit in payload.get("commits", []):
                if not isinstance(commit, dict):
                    continue
                # Some commits might not have a URL or might be distinct
                if "url" in commit:
                    try:
                        commit_res = requests.get(commit["url"], headers=headers)
                        if commit_res.status_code == 200:
                            commit_data = commit_res.json()
                            author = commit_data.get("commit", {}).get("author", {})
                            email = author.get("email")
                            if email and "noreply" not in email:
                                return email
                    except:
                        continue
    return None

def main():
    print("[SEARCH] Searching GitHub for Python Developers...\n")

    users = search_users()
    results = []

    for user in users:
        username = user["login"]
        print(f"Checking {username}...")
        email = get_public_email(username)

        if email:
            print(f"   [FOUND] {email}")
            results.append([username, email])
        else:
            print("   [x] No email found")

    save_to_csv(results)

if __name__ == "__main__":
    main()
