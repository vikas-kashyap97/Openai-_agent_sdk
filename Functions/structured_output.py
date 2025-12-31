from agents import Agent, Runner
from dotenv import load_dotenv
from pydantic import BaseModel
from typing import List

load_dotenv()



class Quiz(BaseModel):
    question: str
    options: List[str]  # ✅ Now Gemini knows it's a list of strings
    correct_option: str

agent = Agent(
    name="Assistant",
    instructions="You are a Quiz Agent. You generate quizes",
    
)

query = input("Enter the query: ")

result = Runner.run_sync(
    agent,
    query,
)

print(result.final_output)