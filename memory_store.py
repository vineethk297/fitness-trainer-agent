import json
import os

MEMORY_FILE = "user_memory.json"

def load_all_memory():
    """Load the entire memory file. Returns {} if it doesn't exist yet."""
    if not os.path.exists(MEMORY_FILE):
        return {}
    with open(MEMORY_FILE, "r") as f:
        return json.load(f)

def load_memory(user_id):
    """Load one user's memory. Returns None if this user has no history yet."""
    all_memory = load_all_memory()
    return all_memory.get(user_id)

def save_memory(user_id, user_data):
    """Save/update one user's memory, preserving everyone else's."""
    all_memory = load_all_memory()
    all_memory[user_id] = user_data
    with open(MEMORY_FILE, "w") as f:
        json.dump(all_memory, f, indent=2)

def new_user_template():
    """Default shape for a brand-new user with no history."""
    return {
        "profile": {
            "age": None,
            "goal": None,
            "equipment": None,
            "injuries_notes": None,
            "schedule": None
        },
        "current_plan": None,
        "session_log": []
    }