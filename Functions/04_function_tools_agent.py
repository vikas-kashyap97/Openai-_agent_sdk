from numbers import Number
from agents import Agent, Runner, function_tool
from dotenv import load_dotenv
load_dotenv()


@function_tool  
async def fetch_weather(location: str) -> str:
    """ Goal:Fetch the news for a given location. 

    Args:location: The location to fetch the news for. 

    Expected Output: A string describing the weather in the given location.
    """
    print(f"Fetching weather for {location}...")
    # In real life, we'd fetch the weather from a weather API
    return "sunny"

@function_tool
def bill_calc(unit: float) -> float:
    """
    Goal:
        Calculate the total electricity bill amount for the user based on
        the number of units consumed.

    Formula Used:
        Energy Charge = Units × ₹5
        Fixed Charge = ₹100
        Tax = 18% on (Energy Charge + Fixed Charge)

    Args:
        unit (float): Number of electricity units consumed by the user.
                      Example: 100

    Expected Output:
        float: Total electricity bill amount rounded to 2 decimal places.
               Example: ₹708.00
    """
    print(f"Calculating the bill for {unit}...")

    rate_per_unit = 5
    fixed_charge = 100

    energy_charge = unit * rate_per_unit
    subtotal = energy_charge + fixed_charge
    tax = subtotal * 0.18

    total_bill = subtotal + tax
    return round(total_bill, 2)



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
    tools=[fetch_weather, fetch_news, fetch_stock_price, bill_calc],
)

query = input("Enter the query: ")

result = Runner.run_sync(
    agent,
    query,
)

print(result.final_output)