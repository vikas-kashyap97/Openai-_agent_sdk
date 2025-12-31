from tavily import TavilyClient
from agents import Agent, Runner, function_tool
from dotenv import load_dotenv
import os

load_dotenv()

TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")


client = TavilyClient(api_key=TAVILY_API_KEY)



@function_tool
def web_search(query: str, max_results: int = 5) -> list:
    """
    Tool to perform a web search using Tavily API.
    
    Args:
        query (str): The search query.
        max_results (int): Number of results to retrieve.

    Returns:
        list: A list of search result dictionaries.
    """
    print(f"Searching web for: {query}")
    results = client.search(query=query, search_depth="advanced", max_results=max_results)
    return results.get("results", [])


agent = Agent(
    name="Assistant",
    instructions="You are a web search assistant. You can search the web for information using the `web_search` tools.",
    tools=[web_search]
)

query = input("Enter the query: ")

result = Runner.run_sync(
    agent,
    query,
)

print(result.final_output)
