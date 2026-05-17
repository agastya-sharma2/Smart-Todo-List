import json
import os
from datetime import datetime, date

TIME_THRESHOLD = 60
DUE_THRESHOLD = 3
TASKS_FILE = "tasks.json"

def load_tasks():
    if not os.path.exists(TASKS_FILE) or os.path.getsize(TASKS_FILE) == 0:
        return {
            "due_now": [],
            "due_pace": [],
            "due_later": []
        }

    with open(TASKS_FILE, "r") as file:
        raw = json.load(file)
    
    return refresh(raw)

def refresh(raw):
    updated_tasks = {
        "due_now": [],
        "due_pace": [],
        "due_later": []
    }

    today = date.today()

    # Gather every single task
    all_tasks = []
    for category in raw.values():
        all_tasks.extend(category)

    for task in all_tasks:
        parsed_date = datetime.strptime(task["due_date"], "%Y-%m-%d").date()
        daysDue = (parsed_date - today).days

        # Inject the updated days left for the frontend template
        task["daysDue"] = daysDue
        es_time = task["estimated_time"]

        # Sort into the correct category based on today's remaining days
        if es_time > TIME_THRESHOLD:
            updated_tasks["due_pace"].append(task)
        elif daysDue <= DUE_THRESHOLD:
            updated_tasks["due_now"].append(task)
        else:
            updated_tasks["due_later"].append(task)

    return updated_tasks


def save_tasks(tasks):
    # Sorts tasks by due date then estimated time
    sort_logic = lambda x: (x["due_date"], x["estimated_time"])
    for category in tasks:
        tasks[category].sort(key=sort_logic)

    with open(TASKS_FILE, "w") as file:
        json.dump(tasks, file, indent=4)


def add_task(task_name, es_time, due_date):
    tasks = load_tasks()

    # Calculate pace time on creation
    parsed_date = datetime.strptime(due_date, "%Y-%m-%d").date()
    today = date.today()
    daysDue = (parsed_date - today).days

    pace_time = round(es_time / daysDue, 1) if daysDue > 0 else es_time

    # Build task object
    task_data = {
        "task": task_name,
        "estimated_time": es_time,
        "due_date": due_date,
        "pace_time": pace_time
    }

    # Temporarily stuff task into "due_later" so that it's there ready for it to be sorted by "refresh()"
    tasks["due_later"].append(task_data)

    # Refresh categories
    final_tasks = refresh(tasks)

    # Save file
    save_tasks(final_tasks)

def remove_task(task_name):
    tasks = load_tasks()

    # Looks through each category
    for category in tasks:
        # Essentially makes a copy of tasks.json except for the task we want to delete
        tasks[category] = [t for t in tasks[category] if t["task"] != task_name]

    # Replaces tasks.json with this new copy
    save_tasks(tasks)