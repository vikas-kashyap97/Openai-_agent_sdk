# from agents import Agent, Runner
# from dotenv import load_dotenv
# load_dotenv()

# agent = Agent(name="Assistant", instructions="You are a helpful assistant")

# query = "Who is the current prime minister of india?"

# result = Runner.run_sync(agent, query)
# print(result.final_output) 



import asyncio
from agents import Agent, Runner
from dotenv import load_dotenv

load_dotenv()

async def main():
    agent = Agent(
        name="Assistant",
        instructions="You are a helpful assistant"
    )

    query = input("Enter your query: ")

    result = Runner.run_streamed(agent, query,
    run_config={
    "max_tokens": 100,
    "temperature": 0.7,
    "top_p": 1,
    "frequency_penalty": 0,
    "presence_penalty": 0,
    "stop": ["\n"],
    "n": 1,
    "stream": True,
    "logprobs": None,
    })

    # Consume the stream (required)
    async for event in result.stream_events():
        pass  # or print tokens if you want

    # Now the run is complete
    print(result.final_output)

if __name__ == "__main__":
    asyncio.run(main())
  