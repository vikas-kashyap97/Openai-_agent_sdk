from agents import Agent, Runner,function_tool
from dotenv import load_dotenv
load_dotenv()


@function_tool
def calculate_bill(unit: float) -> float:
    """Calculate the bill based on the number of units consumed.
    
    Args:
        unit: The number of units consumed.
    
    Returns:
        The calculated bill amount in indian INR (Rupees).
    """
    try:
        # Define the rate per unit
        print("Calculating bill...", unit)
        rate_per_unit = 3.0
        bill_amount = unit * rate_per_unit
        return bill_amount
    except Exception as e:
        raise ValueError(f"Error calculating bill: {e}")

agent = Agent(
    name="Bill Calculator Assistant",
    instructions="You are an expert calculator. you need to expected calculate bills for users based on their queries.",
    tools=[calculate_bill],
)


while True:
    query = input("\nEnter your query (or type 'quit' to exit): ")
    
    if query.lower() == "quit":
        print("Goodbye!")
        break
    
    result = Runner.run_sync(
        agent,
        query,
    )
    
    print("Result:", result.final_output)
