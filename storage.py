import json
import os
from constants import *

def save_tasks(tasks):
    # Sorts tasks by due date then estimated time
    sort_logic = lambda x: (x["due_date"], x["estimated_time"])
    
    # 1. Filter out the temporary "is_slice" tasks so they don't save to JSON
    cleaned_tasks = {
        "due_now": [t for t in tasks["due_now"] if not t.get("is_slice")],
        "due_pace": [t for t in tasks["due_pace"] if not t.get("is_slice")],
        "due_later": [t for t in tasks["due_later"] if not t.get("is_slice")]
    }

    # 2. Strip out 'daysDue' if you want to keep the JSON perfectly pristine, 
    # though filtering the slices alone fixes your ghost bug.
    for category in cleaned_tasks:
        cleaned_tasks[category].sort(key=sort_logic)

    with open(TASKS_FILE, "w") as file:
        json.dump(cleaned_tasks, file, indent=4)

def load_raw_tasks():
    if not os.path.exists(TASKS_FILE) or os.path.getsize(TASKS_FILE) == 0:
        return {
            "due_now": [],
            "due_pace": [],
            "due_later": []
        }

    with open(TASKS_FILE, "r") as file:
        return json.load(file)