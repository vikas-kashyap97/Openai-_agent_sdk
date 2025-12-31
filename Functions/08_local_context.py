from agents import Agent, Runner, function_tool, RunContextWrapper
import os
from dataclasses import dataclass
from dotenv import load_dotenv
load_dotenv()




@dataclass
class User:
  user_id: str


@function_tool  
async def get_user_info(ctx: RunContextWrapper[User]) -> str:
    
    """Fetches the user personal information to personalize responses. Whenver you require user personal info. call this function

    Args:
        id: The user unique indentifier
    """
    id = ctx.context.user_id
    if id == 1:
        user_info = "User name is Vikas. He is 19 years old. He is a Agentic AI Engineer by profession. He likes playing Cricket."
    elif id == 2:
        user_info = "User name is Sachin. He is 130 years old. He is a doctor by profession. He likes mountains."
    else:
        user_info = "user not found"

    return user_info

agent = Agent[User](
    name="Assistant",
    instructions="You are an expert of agentic AI.",
    tools=[get_user_info]
)

query = input("Enter the query: ")

result = Runner.run_sync(
    agent,
    query,
    context=User(user_id=1)
)

print(result.final_output)