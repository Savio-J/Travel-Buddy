import requests
import base64

# GitHub details (Store the token securely in environment variables)
GITHUB_TOKEN = "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"
REPO_OWNER = "Savio-J"
REPO_NAME = "MINI-UNOFFICIAL"

def fetch_github_file(filepath):
    """Fetch and decode a file from the GitHub repository."""
    url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/contents/{filepath}"
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        file_data = response.json()
        decoded_content = base64.b64decode(file_data["content"]).decode("utf-8")
        return decoded_content  # Return actual file content
    else:
        return f"Error: {response.status_code} - {response.json().get('message', '')}"
