import json
from typing import Dict, Any, List
from datetime import datetime
from agents import Agent, Runner, function_tool
from dotenv import load_dotenv
import sqlite3

load_dotenv()

TODO_FILE = "todos.json"  # // JSON file to store todos
DB_FILE = "todos.db"      # // SQLite database file

# // Initialize the SQLite database
def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS todos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            status TEXT DEFAULT 'pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            due_date DATE,
            completed_at TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

init_db()  # // Ensure DB is ready


# // Helper to load todos from JSON
def load_json() -> List[Dict[str, Any]]:
    try:
        with open(TODO_FILE, "r") as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

# // Helper to save todos to JSON
def save_json(todos: List[Dict[str, Any]]):
    with open(TODO_FILE, "w") as file:
        json.dump(todos, file, indent=2)


# // Sync existing JSON todos into DB (one-time sync)
def sync_json_to_db():
    todos = load_json()
    if not todos:
        return  # // Nothing to sync

    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    for todo in todos:
        # // Check if ID exists in DB
        c.execute('SELECT id FROM todos WHERE id = ?', (todo["id"],))
        if not c.fetchone():
            c.execute('''
                INSERT INTO todos (id, title, description, status, created_at, due_date)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                todo["id"],
                todo["title"],
                todo.get("description", ""),
                "completed" if todo.get("completed", False) else "pending",
                todo.get("created_at", datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
                todo.get("dueDate", datetime.now().strftime("%Y-%m-%d"))
            ))
    conn.commit()
    conn.close()


# // Create a new todo
@function_tool
def create_todo(title: str, description: str = "", due_date: str = None) -> Dict[str, Any]:
    if due_date is None:
        due_date = datetime.now().strftime("%Y-%m-%d")  # // Default due date today

    # // Insert into SQLite
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''
        INSERT INTO todos (title, description, due_date)
        VALUES (?, ?, ?)
    ''', (title, description, due_date))
    todo_id = c.lastrowid
    conn.commit()
    conn.close()

    # // Insert into JSON
    todos = load_json()
    new_todo = {
        "id": todo_id,  # // Use DB ID
        "title": title,
        "description": description,
        "completed": False,
        "dueDate": due_date,
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    todos.append(new_todo)
    save_json(todos)

    return new_todo


# // Read all todos
@function_tool
def read_todo() -> List[Dict[str, Any]]:
    return load_json()


# // Update a todo
@function_tool
def update_todos(todo_id: int, title: str = None, description: str = None,
                 completed: bool = None, due_date: str = None) -> Dict[str, Any]:
    # // Update in SQLite
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('SELECT * FROM todos WHERE id = ?', (todo_id,))
    if not c.fetchone():
        conn.close()
        raise ValueError(f"Todo with id {todo_id} not found in DB.")

    updates = []
    params = []
    if title: updates.append("title = ?"); params.append(title)
    if description: updates.append("description = ?"); params.append(description)
    if due_date: updates.append("due_date = ?"); params.append(due_date)
    if completed is not None:
        updates.append("status = ?"); params.append("completed" if completed else "pending")
        if completed:
            updates.append("completed_at = ?"); params.append(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        else:
            updates.append("completed_at = NULL")
    if updates:
        query = f"UPDATE todos SET {', '.join(updates)} WHERE id = ?"
        params.append(todo_id)
        c.execute(query, tuple(params))
        conn.commit()
    conn.close()

    # // Update in JSON
    todos = load_json()
    for todo in todos:
        if todo["id"] == todo_id:
            if title: todo["title"] = title
            if description: todo["description"] = description
            if due_date: todo["dueDate"] = due_date
            if completed is not None: todo["completed"] = completed
            save_json(todos)
            return todo

    raise ValueError(f"Todo with id {todo_id} not found in JSON.")


# // Delete a todo
@function_tool
def delete_todos(todo_id: int) -> Dict[str, Any]:
    # // Delete from SQLite
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('SELECT * FROM todos WHERE id = ?', (todo_id,))
    if not c.fetchone():
        conn.close()
        raise ValueError(f"Todo with id {todo_id} not found in DB.")
    c.execute('DELETE FROM todos WHERE id = ?', (todo_id,))
    conn.commit()
    conn.close()

    # // Delete from JSON
    todos = load_json()
    updated_todos = [todo for todo in todos if todo["id"] != todo_id]
    if len(updated_todos) == len(todos):
        raise ValueError(f"Todo with id {todo_id} not found in JSON.")
    save_json(updated_todos)

    return {"deleted_id": todo_id, "remaining": updated_todos}


# // Sync JSON to DB at startup
sync_json_to_db()

# // Setup the Agent
agent = Agent(
    name="Todos Assistant",
    instructions="You are an expert of todos. You can add, list, update, and delete todos.",
    tools=[create_todo, read_todo, update_todos, delete_todos],
)

# // Run the agent
query = input("Enter the query: ")
result = Runner.run_sync(agent, query)
print(result.final_output)
