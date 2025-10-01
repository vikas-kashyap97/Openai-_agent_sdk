from agents import Agent, Runner
from dotenv import load_dotenv
load_dotenv()
import asyncio


async def main():
    agent = Agent(name="Assistant", instructions="You are a helpful assistant")

    result = await Runner.run(agent, "What is the briefened history of AI?")
    
    print(result.final_output)

asyncio.run(main())