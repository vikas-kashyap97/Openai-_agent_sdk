
from agents import Agent, Runner
from openai.types.responses import ResponseTextDeltaEvent
from dotenv import load_dotenv
import asyncio

load_dotenv()




async def main():
    agent = Agent(
    name="Assistant",
    instructions="You are an AI expert.",
    )
    query = input("Enter the query: ")
    result = Runner.run_streamed(agent, input=query)
    async for event in result.stream_events():
        if event.type == "raw_response_event" and isinstance(event.data, ResponseTextDeltaEvent):
            print(event.data.delta, end="", flush=True)


asyncio.run(main())   