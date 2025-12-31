from agents import Agent, Runner, function_tool
from dotenv import load_dotenv
load_dotenv()


@function_tool  
async def fetch_weather(location: str) -> str:
    """Fetch the weather for a given location.

    Args:
        location: The location to fetch the weather for.
    """
    print(f"Fetching weather for {location}...")
    # In real life, we'd fetch the weather from a weather API
    return "sunny"


@function_tool  
def fetch_news(location: str) -> str:
    """Fetch the news for a given location.

    Args:
        location: The location to fetch the news for.
    """
    print(f"Fetching news for {location}...")
    # In real life, we'd fetch the news from a news API
    return "breaking news"

@function_tool
def fetch_stock_price(location: str) -> str:
    """Fetch the stock price for a given location.

    Args:
        location: The location to fetch the stock price for.
    """
    print(f"Fetching stock price for {location}...")
    # In real life, we'd fetch the stock price from a stock API
    return "USD 1000.00"




agent = Agent(
    name="Assistant",
    instructions="You are an expert of agentic AI.",
    tools=[fetch_weather, fetch_news, fetch_stock_price],
)

query = input("Enter the query: ")

result = Runner.run_sync(
    agent,
    query,
)

print(result.final_output)