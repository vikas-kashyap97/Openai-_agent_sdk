
import json
from agents import Agent, Runner,function_tool
from dotenv import load_dotenv
import json
from typing import Dict, Any
from datetime import datetime

load_dotenv()


@function_tool
def list_todos():
    """List all todos from the todos.json file."""
    try:
        print("Listing todos...")
        with open("todos.json", "r") as file:
            data = json.load(file)  # Use json.load to read directly from file
        return data
    except Exception as e:
        print(f"Error: {e}")
        raise FileNotFoundError("The file todos.json was not found.")
 

@function_tool
def add_todo(title: str, description: str = "", due_date: str = "") -> Dict[str, Any]:
    """Add a new todo to the todos.json file.
    
    Args:
        title: The title of the todo.
        description: Optional description of the todo.
        due_date: Optional due date in YYYY-MM-DD format.
    
    Returns:
        The newly created todo item title.
    """
    try:
        # Read existing todos
        try:
            with open("todos.json", "r") as file:
                todos = json.load(file)
        except FileNotFoundError:
            todos = []  # If file doesn't exist, start with an empty list
        except json.JSONDecodeError:
            raise ValueError("Error decoding todos.json. Ensure it contains valid JSON.")

        # Create new todo
        new_todo = {
            "id": len(todos) + 1,  # Simple incremental ID
            "title": title,
            "description": description,
            "completed": False,  # Default to not completed
            "dueDate": due_date if due_date else datetime.now().strftime("%Y-%m-%d")
        }

        # Append and save
        todos.append(new_todo)
        with open("todos.json", "w") as file:
            json.dump(todos, file, indent=2)

        return new_todo

    except Exception as e:
        raise Exception(f"Failed to add todo: {str(e)}")


agent = Agent(
    name="Todos Assistant",
    instructions="""
You are a todo management assistant.

You MUST use tools to answer questions about todos.

Rules:
- To answer any question about existing todos, ALWAYS call list_todos first.
- You are allowed to summarize, filter, or extract information from tool results.
- If the user asks for titles, extract only the titles from the todo list.
- Never ask the user to provide todos; todos.json is the source of truth.

You can:
- list todos
- add todos
""",
    tools=[list_todos, add_todo],
)


query = input("Enter the query: ")

result = Runner.run_sync(
    agent,
    query,
)

print(result.final_output)