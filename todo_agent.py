from openai import AsyncOpenAI
import os
from dotenv import load_dotenv
import sqlite3
from datetime import datetime
from typing import List, Dict, Any
import asyncio

# Load environment variables
load_dotenv()

# Initialize OpenAI client
client = AsyncOpenAI(
    api_key=os.getenv('OPENAI_API_KEY'),
)

# Database setup
def init_db():
    conn = sqlite3.connect('todos.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS todos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            status TEXT DEFAULT 'pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            completed_at TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

# Tool implementations
def add_todo(title: str, description: str = "") -> Dict[str, Any]:
    """Add a new todo item to the database."""
    conn = sqlite3.connect('todos.db')
    c = conn.cursor()
    c.execute(
        'INSERT INTO todos (title, description) VALUES (?, ?)',
        (title, description)
    )
    conn.commit()
    todo_id = c.lastrowid
    conn.close()
    return {"id": todo_id, "title": title, "description": description, "status": "pending"}

def list_todos(status: str = None) -> List[Dict[str, Any]]:
    """List all todos, optionally filtered by status."""
    conn = sqlite3.connect('todos.db')
    c = conn.cursor()
    
    if status:
        c.execute('SELECT * FROM todos WHERE status = ?', (status,))
    else:
        c.execute('SELECT * FROM todos')
    
    todos = []
    for row in c.fetchall():
        todos.append({
            "id": row[0],
            "title": row[1],
            "description": row[2],
            "status": row[3],
            "created_at": row[4],
            "completed_at": row[5]
        })
    conn.close()
    return todos

def complete_todo(todo_id: int) -> Dict[str, Any]:
    """Mark a todo as completed."""
    conn = sqlite3.connect('todos.db')
    c = conn.cursor()
    now = datetime.now().isoformat()
    c.execute(
        'UPDATE todos SET status = ?, completed_at = ? WHERE id = ?',
        ('completed', now, todo_id)
    )
    conn.commit()
    
    c.execute('SELECT * FROM todos WHERE id = ?', (todo_id,))
    todo = c.fetchone()
    conn.close()
    
    if todo:
        return {
            "id": todo[0],
            "title": todo[1],
            "description": todo[2],
            "status": "completed",
            "created_at": todo[4],
            "completed_at": now
        }
    return {"error": "Todo not found"}

def delete_todo(todo_id: int) -> Dict[str, Any]:
    """Delete a todo item."""
    conn = sqlite3.connect('todos.db')
    c = conn.cursor()
    c.execute('DELETE FROM todos WHERE id = ?', (todo_id,))
    conn.commit()
    success = c.rowcount > 0
    conn.close()
    return {"success": success, "message": f"Todo {todo_id} deleted" if success else "Todo not found"}

# Initialize database
init_db()

# Define tools for OpenAI function calling
tools = [
    {
        "type": "function",
        "function": {
            "name": "add_todo",
            "description": "Add a new todo item with a title and optional description",
            "parameters": {
                "type": "object",
                "properties": {
                    "title": {
                        "type": "string",
                        "description": "The title of the todo item"
                    },
                    "description": {
                        "type": "string",
                        "description": "Optional description of the todo item"
                    }
                },
                "required": ["title"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "list_todos",
            "description": "List all todos, optionally filtered by status (pending/completed)",
            "parameters": {
                "type": "object",
                "properties": {
                    "status": {
                        "type": "string",
                        "description": "Optional status filter (pending/completed)",
                        "enum": ["pending", "completed"]
                    }
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "complete_todo",
            "description": "Mark a todo item as completed",
            "parameters": {
                "type": "object",
                "properties": {
                    "todo_id": {
                        "type": "integer",
                        "description": "The ID of the todo item to complete"
                    }
                },
                "required": ["todo_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "delete_todo",
            "description": "Delete a todo item",
            "parameters": {
                "type": "object",
                "properties": {
                    "todo_id": {
                        "type": "integer",
                        "description": "The ID of the todo item to delete"
                    }
                },
                "required": ["todo_id"]
            }
        }
    }
]

# Function mapping
available_functions = {
    "add_todo": add_todo,
    "list_todos": list_todos,
    "complete_todo": complete_todo,
    "delete_todo": delete_todo
}

async def run_agent(user_query: str):
    """Run the agent with function calling."""
    messages = [
        {
            "role": "system",
            "content": """You are a helpful Todo management assistant. You can:
1. Add new todo items
2. List all todos or filter by status
3. Mark todos as completed
4. Delete todos
Always be clear and concise in your responses. When listing todos, format them nicely."""
        },
        {"role": "user", "content": user_query}
    ]
    
    # First API call
    response = await client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=messages,
        tools=tools,
        tool_choice="auto"
    )
    
    response_message = response.choices[0].message
    tool_calls = response_message.tool_calls
    
    # If there are no tool calls, return the response
    if not tool_calls:
        return response_message.content
    
    # Add assistant's response to messages
    messages.append(response_message)
    
    # Execute function calls
    for tool_call in tool_calls:
        function_name = tool_call.function.name
        function_to_call = available_functions[function_name]
        function_args = eval(tool_call.function.arguments)
        
        # Call the function
        function_response = function_to_call(**function_args)
        
        # Add function response to messages
        messages.append({
            "role": "tool",
            "tool_call_id": tool_call.id,
            "name": function_name,
            "content": str(function_response)
        })
    
    # Get final response from the model
    final_response = await client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=messages
    )
    
    return final_response.choices[0].message.content

async def main():
    print("Welcome to the Todo Assistant!")
    print("Type 'quit' to exit")
    print("\nYou can ask me to:")
    print("- Add a new todo (e.g., 'Add a todo to buy groceries')")
    print("- List all todos (e.g., 'Show me all todos')")
    print("- Complete a todo (e.g., 'Mark todo #1 as completed')")
    print("- Delete a todo (e.g., 'Delete todo #1')")
    
    while True:
        query = input("\nWhat would you like to do? ")
        
        if query.lower() == 'quit':
            print("Goodbye!")
            break
        
        try:
            result = await run_agent(query)
            print("\nAssistant:", result)
        except Exception as e:
            print(f"\nError: {str(e)}")

if __name__ == "__main__":
    asyncio.run(main())