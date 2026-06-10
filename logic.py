import json
import os
from datetime import datetime, date
import time

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

            # Check if it was already completed today
            # We compare the string date to today's string date
            today_str = today.strftime("%Y-%m-%d")
            already_done_today = task.get("last_completed") == today_str

            if daysDue >= 0 and not already_done_today:
                daily_slice = {
                    "task": f"Daily Slice: {task['task']}",
                    "parent_task": task["task"],
                    "estimated_time": task["pace_time"],
                    "due_date": today.strftime("%Y-%m-%d"),
                    "daysDue": 0,
                    "completed_today": False,
                    "last_completed": task.get("last_completed", ""),
                    "is_slice": True
                }
                updated_tasks["due_now"].append(daily_slice)

        elif daysDue <= DUE_THRESHOLD:
            updated_tasks["due_now"].append(task)
        else:
            updated_tasks["due_later"].append(task)

    return updated_tasks


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


def add_task(task_name, es_time, due_date):
    tasks = load_tasks()

    # Calculate pace time on creation
    parsed_date = datetime.strptime(due_date, "%Y-%m-%d").date()
    today = date.today()
    daysDue = (parsed_date - today).days

    pace_time = int(round(es_time / daysDue, 0)) if daysDue > 0 else es_time
    

    # Build task object
    task_data = {
        "task": task_name,
        "estimated_time": es_time,
        "due_date": due_date,
        "pace_time": pace_time,
        "current_time": 0,
        "completed_today": False,
        "last_completed": "",
        "is_slice": False
    }

    # Temporarily stuff task into "due_later" so that it's there ready for it to be sorted by "refresh()"
    tasks["due_later"].append(task_data)

    # Refresh categories
    final_tasks = refresh(tasks)

    # Save file
    save_tasks(final_tasks)

def remove_task(task_name, is_slice=False, parent_name=None):
    tasks = load_tasks()

    if is_slice and parent_name:
        # Scenario A: User completed a daily slice
        # Hide today's slice
        today_str = date.today().strftime("%Y-%m-%d")
        for category in tasks:
            for task in tasks[category]: 
                if task["task"] == parent_name:
                    task["last_completed"] = today_str # "task" in this case is the parent
                    task["current_time"] += task["pace_time"]
                    if task["current_time"] == task["estimated_time"]:
                        tasks[category] = [t for t in tasks[category] if t["task"] != task["task"]]
    else:
        # Scenario B: User completed a regular task
        # Delete as usual
        for category in tasks:
            tasks[category] = [t for t in tasks[category] if t["task"] != task_name]

    # Save the updated state
    save_tasks(tasks)