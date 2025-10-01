from agents import Agent, Runner, OpenAIChatCompletionsModel, trace, set_default_openai_api, set_default_openai_client, set_tracing_disabled
import asyncio
import os
from openai import AsyncOpenAI

from dotenv import load_dotenv
load_dotenv()


# This will check the state of the tracing
set_tracing = True
print(f"Tracing is disabled? {set_tracing}")


client = AsyncOpenAI()
set_default_openai_client(client=client, use_for_tracing=True)
set_default_openai_api("chat_completions")

async def main():
    agent = Agent(name="Joke generator", instructions="generate a context about the query asked by the user, then tell a joke based on that context, and finally rate the joke on a scale of 1 to 10",)
    user_input = input("Ask me anything (e.g., 'Tell me a joke'): ")

    with trace("Joke workflow"): 
        first_result = await Runner.run(agent, user_input)
        second_result = await Runner.run(agent, f"Rate this joke: {first_result.final_output}")
        print(f"Joke: {first_result.final_output}")
        print(f"Rating: {second_result.final_output}")

asyncio.run(main())