import asyncio
import random
import uuid

from pydantic import BaseModel

from agents import (
    Agent,
    HandoffOutputItem,
    ItemHelpers,
    MessageOutputItem,
    RunContextWrapper,
    Runner,
    ToolCallItem,
    ToolCallOutputItem,
    TResponseInputItem,
    function_tool,
    handoff,
    trace,
)
from agents.extensions.handoff_prompt import RECOMMENDED_PROMPT_PREFIX
from dotenv import load_dotenv
load_dotenv()

### CONTEXT


class AirlineAgentContext(BaseModel):
    passenger_name: str | None = None
    confirmation_number: str | None = None
    seat_number: str | None = None
    flight_number: str | None = None


### TOOLS


@function_tool(
    name_override="faq_lookup_tool", description_override="Lookup frequently asked questions."
)
async def faq_lookup_tool( context: RunContextWrapper[AirlineAgentContext], question: str) -> str:
    print("context:", context.context.passenger_name)
    print("context:", context.context.seat_number)
    print("context:", context.context.confirmation_number)
    print("context:", context.context.flight_number)
    question_lower = question.lower()
    if any(
        keyword in question_lower
        for keyword in ["bag", "baggage", "luggage", "carry-on", "hand luggage", "hand carry"]
    ):
        return (
            "You are allowed to bring one bag on the plane. "
            "It must be under 50 pounds and 22 inches x 14 inches x 9 inches."
        )
    elif any(keyword in question_lower for keyword in ["seat", "seats", "seating", "plane"]):
        return (
            "There are 120 seats on the plane. "
            "There are 22 business class seats and 98 economy seats. "
            "Exit rows are rows 4 and 16. "
            "Rows 5-8 are Economy Plus, with extra legroom. "
        )
    elif any(
        keyword in question_lower
        for keyword in ["wifi", "internet", "wireless", "connectivity", "network", "online"]
    ):
        return "We have free wifi on the plane, join Airline-Wifi"
    return "I'm sorry, I don't know the answer to that question."



@function_tool
async def update_seat(
    context: RunContextWrapper[AirlineAgentContext],
    confirmation_number: str,
    new_seat: str,
    passenger_name: str | None = None
) -> str:
    """
    Update the seat for a given confirmation number.
    """
    context.context.confirmation_number = confirmation_number
    context.context.seat_number = new_seat
    if passenger_name:
        context.context.passenger_name = passenger_name

    # Ensure that the flight number has been set by the incoming handoff
    assert context.context.flight_number is not None, "Flight number is required"

    return (
        f"Updated seat to {new_seat} for passenger "
        f"{passenger_name or 'Unknown'} with confirmation {confirmation_number}"
    )



### HOOKS


async def on_seat_booking_handoff(context: RunContextWrapper[AirlineAgentContext]) -> None:
    flight_number = f"FLT-{random.randint(100, 999)}"
    context.context.flight_number = flight_number


### AGENTS
print(RECOMMENDED_PROMPT_PREFIX)
faq_agent = Agent[AirlineAgentContext](
    name="FAQ Agent",
    handoff_description="A helpful agent that can answer questions about the airline.",
    instructions=f"""{RECOMMENDED_PROMPT_PREFIX}
    You are an FAQ agent. If you are speaking to a customer, you probably were transferred to from the triage agent.
    Use the following routine to support the customer.
    # Routine
    1. Identify the last question asked by the customer.
    2. Use the faq lookup tool to answer the question. Do not rely on your own knowledge.
    3. If you cannot answer the question, transfer back to the triage agent.""",
    tools=[faq_lookup_tool],
)

seat_booking_agent = Agent[AirlineAgentContext](
    name="Seat Booking Agent",
    handoff_description="A helpful agent that can update a seat on a flight.",
    instructions=f"""{RECOMMENDED_PROMPT_PREFIX}
    You are a seat booking agent. If you are speaking to a customer, you probably were transferred from the triage agent.

    ## Routine
    - First, check if the customer has already provided their **confirmation number**, **desired seat**, and optionally their **name** in their message.
    - If all details are available, immediately call the `update_seat` tool.
    - If details are missing, ask for the missing information step by step.
    - Always confirm the update back to the customer.

    If the customer asks something unrelated to seat updates, transfer them back to the triage agent.
    """,
    tools=[update_seat],
)


triage_agent = Agent[AirlineAgentContext](
    name="Triage Agent",
    handoff_description="A triage agent that can delegate a customer's request to the appropriate agent.",
    instructions=(
        f"{RECOMMENDED_PROMPT_PREFIX} "
        "You are a helpful triaging agent. You can use your tools to delegate questions to other appropriate agents."
    ),
    handoffs=[
        faq_agent,
        handoff(agent=seat_booking_agent, on_handoff=on_seat_booking_handoff),
    ],
)

faq_agent.handoffs.append(triage_agent)
seat_booking_agent.handoffs.append(triage_agent)


### RUN


async def main():
    current_agent: Agent[AirlineAgentContext] = triage_agent
    input_items: list[TResponseInputItem] = []
    context = AirlineAgentContext()

    # Normally, each input from the user would be an API request to your app, and you can wrap the request in a trace()
    # Here, we'll just use a random UUID for the conversation ID
    conversation_id = uuid.uuid4().hex[:16]

    while True:
        user_input = input("Enter your message: ")
        with trace("Customer service", group_id=conversation_id):
            input_items.append({"content": user_input, "role": "user"})
            result = await Runner.run(current_agent, input_items, context=context)

            for new_item in result.new_items:
                agent_name = new_item.agent.name
                
                if isinstance(new_item, MessageOutputItem):
                    print(f"{agent_name}: {ItemHelpers.text_message_output(new_item)}")
                elif isinstance(new_item, HandoffOutputItem):
                    print(
                        f"Handed off from {new_item.source_agent.name} to {new_item.target_agent.name}"
                    )
                elif isinstance(new_item, ToolCallItem):
                    print(f"{agent_name}: Calling a tool")
                elif isinstance(new_item, ToolCallOutputItem):
                    print(f"{agent_name}: Tool call output: {new_item.output}")
                else:
                    print(f"{agent_name}: Skipping item: {new_item.__class__.__name__}")
            input_items = result.to_input_list()
            current_agent = result.last_agent


if __name__ == "__main__":
    asyncio.run(main())