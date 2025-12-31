from turtle import title
from unittest import result
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from dotenv import load_dotenv
from agents import function_tool, Agent, Runner
from datetime import datetime
import os
load_dotenv()


mongodb_uri = os.getenv("MONGO_DB_URI")

# Create a new client and connect to the server
client = MongoClient(
    mongodb_uri,
    server_api=ServerApi('1'),
)

try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)

from datetime import datetime
from bson import ObjectId

# CREATE (already aligned with yours, kept for completeness)
@function_tool
async def create_todo(title: str, description: str = "", due_date: str = "") -> dict:
    """Add a new todo."""
    try:
        db = client["agent_db"]
        todos = db["todos"]

        new_todo = {
            "title": title,
            "description": description,
            "completed": False,
            "dueDate": due_date if due_date else datetime.now().strftime("%Y-%m-%d"),
            "createdAt": datetime.utcnow()
        }

        result = todos.insert_one(new_todo)
        return {"id": str(result.inserted_id), **new_todo}

    except Exception as e:
        raise Exception(f"Failed to create todo: {str(e)}")


# READ – get all todos
@function_tool
async def get_todos(include_completed: bool = True) -> list:
    """Fetch all todos."""
    try:
        db = client["agent_db"]
        todos = db["todos"]

        query = {} if include_completed else {"completed": False}
        results = todos.find(query).sort("createdAt", -1)

        return [
            {
                "id": str(todo["_id"]),
                "title": todo["title"],
                "description": todo.get("description", ""),
                "completed": todo["completed"],
                "dueDate": todo["dueDate"]
            }
            for todo in results
        ]

    except Exception as e:
        raise Exception(f"Failed to fetch todos: {str(e)}")


# READ – get single todo by ID
@function_tool
async def get_todo(todo_id: str) -> dict:
    """Fetch a single todo by ID."""
    try:
        db = client["agent_db"]
        todos = db["todos"]

        todo = todos.find_one({"_id": ObjectId(todo_id)})
        if not todo:
            raise Exception("Todo not found")

        return {
            "id": str(todo["_id"]),
            "title": todo["title"],
            "description": todo.get("description", ""),
            "completed": todo["completed"],
            "dueDate": todo["dueDate"]
        }

    except Exception as e:
        raise Exception(f"Failed to fetch todo: {str(e)}")


# UPDATE
@function_tool
async def update_todo(
    todo_id: str,
    title: str | None = None,
    description: str | None = None,
    completed: bool | None = None,
    due_date: str | None = None
) -> dict:
    """Update an existing todo."""
    try:
        db = client["agent_db"]
        todos = db["todos"]

        update_fields = {}
        if title is not None:
            update_fields["title"] = title
        if description is not None:
            update_fields["description"] = description
        if completed is not None:
            update_fields["completed"] = completed
        if due_date is not None:
            update_fields["dueDate"] = due_date

        if not update_fields:
            raise Exception("No fields provided to update")

        result = todos.update_one(
            {"_id": ObjectId(todo_id)},
            {"$set": update_fields}
        )

        if result.matched_count == 0:
            raise Exception("Todo not found")

        return {"id": todo_id, **update_fields}

    except Exception as e:
        raise Exception(f"Failed to update todo: {str(e)}")


# DELETE
@function_tool
async def delete_todo(todo_id: str) -> dict:
    """Delete a todo."""
    try:
        db = client["agent_db"]
        todos = db["todos"]

        result = todos.delete_one({"title": title})
        if result.deleted_count == 0:
            raise Exception("Todo not found")

        return {"id": todo_id, "deleted": True}

    except Exception as e:
        raise Exception(f"Failed to delete todo: {str(e)}")



agent = Agent(
    name="MongoTodoAgent",
    instructions="""
A MongoDB-backed agent that handles creating, fetching, updating, and deleting TODO items with structured, reliable CRUD operations.
""",
    tools=[
       create_todo,
       get_todos,
       update_todo,
       delete_todo

    ]
)

query = input("Ask your query: ")

result = Runner.run_sync(
    agent,
    query
)


print(result.final_output)