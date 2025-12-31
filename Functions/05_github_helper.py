from dotenv import load_dotenv
import requests
import os
from agents import function_tool, Agent, Runner
from typing import Dict, Any
import base64

load_dotenv()

GITHUB_API = os.getenv("GITHUB_API_BASE")

def github_headers():
    return {
        "Authorization": f"Bearer {os.getenv('GITHUB_TOKEN')}",
        "Accept": "application/vnd.github+json"
    }

@function_tool
def list_repo_files(owner: str, repo: str) -> list[str]:
    """
    Goal:
        List all files in the root of a GitHub repository.

    Args:
        owner (str): GitHub username or org
        repo (str): Repository name

    Expected Output:
        list[str]: File names in the repository
    """
    url = f"{GITHUB_API}/repos/{owner}/{repo}/contents"
    response = requests.get(url, headers=github_headers())
    response.raise_for_status()

    data = response.json()
    return [item["name"] for item in data if item["type"] == "file"]




@function_tool
def read_repo_file(owner: str, repo: str, path: str) -> str:
    """
    Goal:
        Read the content of a file from a GitHub repository.

    Args:
        owner (str)
        repo (str)
        path (str): File path

    Expected Output:
        str: Raw file content
    """
    url = f"{GITHUB_API}/repos/{owner}/{repo}/contents/{path}"
    response = requests.get(url, headers=github_headers())
    response.raise_for_status()

    data = response.json()
    return base64.b64decode(data["content"]).decode("utf-8")


@function_tool
def get_repo_info(owner:str, repo:str) -> Dict[str, Any]:
    """
    Goal:
    Fetch basic information for github repository.

    Args:
        Owner (str): Github username or organization name.
        repo (str): Repository name.

    Expected Output:
        dict: Repository details like name, stars, forks, open issues.
    """
    url = f"{GITHUB_API}/repos/{owner}/{repo}"
    response = requests.get(url, headers=github_headers())
    response.raise_for_status()

    data = response.json()
    return {
    "full_name": data["full_name"],
    "stars": data["stargazers_count"],
    "forks": data["forks_count"],
    "open_issues": data["open_issues_count"],
    "language": data["language"]
}

@function_tool
def parse_github_url(url: str) -> dict:
    """
    Goal:
    Extract owner and repo name from a GitHub URL.

    Args:
        url (str): A GitHub repo URL (https://github.com/owner/repo.git or without .git)

    Expected Output:
        dict: {"owner": "owner", "repo": "repo"}
    """
    # Remove trailing slash and .git if present
    cleaned = url.rstrip("/").replace(".git", "")
    parts = cleaned.split("/")

    # Last two parts are owner and repo
    owner = parts[-2]
    repo = parts[-1]

    return {"owner": owner, "repo": repo}


agent = Agent(
    name="GitHub Code Analyst",
    instructions="""
You are a GitHub repository code analyst.

Workflow:
1. Parse GitHub URL
2. List repository files
3. Read Python files
4. Summarize what the code does
5. Extract used Python packages from imports

Rules:
- Use tools to fetch code
- Then analyze code
- Output human-readable summary (NOT JSON)
""",
    tools=[
        parse_github_url,
        list_repo_files,
        read_repo_file,
        get_repo_info
    ]
)





query = input("Ask your query about Github: ")

result = Runner.run_sync(
    agent,
    query
)


print(result.final_output)