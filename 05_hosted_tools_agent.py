
from agents import Agent, OpenAIChatCompletionsModel, Runner, WebSearchTool, FileSearchTool
from dotenv import load_dotenv


load_dotenv()



agent = Agent(
    name="Assistant",
    instructions="You are an expert of agentic AI.",
    tools = [WebSearchTool()]
)

query = input("Enter the query: ")

result = Runner.run_sync(
    agent,
    query,
)

print(result.final_output)