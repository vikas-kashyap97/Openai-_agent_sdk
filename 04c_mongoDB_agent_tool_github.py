from agents import Agent, OpenAIChatCompletionsModel, Runner, function_tool
from dotenv import load_dotenv
import requests
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import os

load_dotenv()

# MongoDB connection setup
uri = os.getenv("MONGODB_URI")
client = MongoClient(uri, server_api=ServerApi('1'))

# Choose database and collection
db = client["Github"]
collection = db["users"]

try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)


@function_tool
def fetch_github_user_info(username: str) -> dict:
    """Fetch GitHub user info including repos, followers, and other details, then store in MongoDB."""
    try:
        headers = {}
        user_url = f"https://api.github.com/users/{username}"
        response = requests.get(user_url, headers=headers)
        if response.status_code != 200:
            return {"error": f"User not found or error {response.status_code}"}

        data = response.json()
        # Fetch repos
        repos_url = data.get("repos_url")
        repos_response = requests.get(repos_url, headers=headers)
        repos_data = repos_response.json() if repos_response.status_code == 200 else []

        user_info = {
            "username": data.get("login"),
            "name": data.get("name"),
            "followers": data.get("followers"),
            "following": data.get("following"),
            "public_repos": data.get("public_repos"),
            "repo_names": [repo['name'] for repo in repos_data],
            "bio": data.get("bio"),
            "location": data.get("location"),
            "created_at": data.get("created_at"),
        }

        # Insert into MongoDB (upsert so it updates if already exists)
        collection.update_one(
            {"username": user_info["username"]},
            {"$set": user_info},
            upsert=True
        )

        return user_info
    except Exception as e:
        raise ValueError(f"Error fetching GitHub info: {e}")


# Create the agent
agent = Agent(
    name="GitHub Info Assistant",
    instructions="You are an expert assistant that fetches GitHub user details like repos, followers, bio, etc., and stores them in MongoDB.",
    tools=[fetch_github_user_info],
)

# Get username input
query = input("Enter GitHub username to fetch info: ")

# Run the agent synchronously
result = Runner.run_sync(agent, query)

# Print the output
print(result.final_output)
