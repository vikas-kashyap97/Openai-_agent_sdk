from dotenv import load_dotenv
from agents import Agent, Runner

load_dotenv()


french_agent = Agent(
    name="french_agent",
    instructions="You only speak French",
)

spanish_agent = Agent(
    name="spanish_agent",
    instructions="You only speak Spanish",
)

english_agent = Agent(
    name="english_agent",
    instructions="You only speak English",
)

triage_agent = Agent(
    name="triage_agent",
    instructions="Handoff to the appropriate agent based on the language of the request.",
    handoffs=[french_agent, spanish_agent, english_agent],
)

history = []
agent = triage_agent

while True:
    userInput = input("What language do you want to use? (French, Spanish or English): ")
    history.append(
        {
            "role": "user",
            "content": userInput
        }
    )
    result = Runner.run_sync(
        agent,
        history,
    )

    history = result.to_input_list()
    agent = result.last_agent

    print("Final Output:", result.final_output)
    print("==========================================")

    print("Last Agent:", result.last_agent)
    print("==========================================")

    print("To input list:", result.to_input_list())
    print("==========================================")

    print("Raw Response:", result.raw_responses)
    print("==========================================")

    print("User Input:", result.input)
    print("==========================================")

    print("New Items:", result.new_items)
 