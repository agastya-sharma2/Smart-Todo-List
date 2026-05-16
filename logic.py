import json
import os

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
        return json.load(file)


def save_tasks(tasks):
    # Sorts tasks by due date then estimated time
    sort_logic = lambda x: (x["due_date"], x["estimated_time"])
    for category in tasks:
        tasks[category].sort(key=sort_logic)

    with open(TASKS_FILE, "w") as file:
        json.dump(tasks, file, indent=4)


def add_task(task_name, es_time, due_date):
    tasks = load_tasks()

    # Calculate the pace time
    pace_time = round(es_time / due_date, 1) if due_date > 0 else es_time

    # Build task object
    task_data = {
        "task": task_name,
        "estimated_time": es_time,
        "due_date": due_date,
        "pace_time": pace_time
    }

    # Categorize which list it should go into
    if due_date <= DUE_THRESHOLD:
        tasks["due_now"].append(task_data)
    elif es_time > TIME_THRESHOLD:
        tasks["due_pace"].append(task_data)
    else:
        tasks["due_later"].append(task_data)

    # Save file
    save_tasks(tasks)

def remove_task(task_name):
    tasks = load_tasks()

    # Looks through each category
    for category in tasks:
        # Essentially makes a copy of tasks.json except for the task we want to delete
        tasks[category] = [t for t in tasks[category] if t["task"] != task_name]

    # Replaces tasks.json with this new copy
    save_tasks(tasks)