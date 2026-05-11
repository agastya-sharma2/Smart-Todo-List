import json
import os

TIME_THRESHOLD = 60
DUE_THRESHOLD = 3

TASKS_FILE = "tasks.json"


def load_tasks():
    if not os.path.exists(TASKS_FILE):
        return {}

    with open(TASKS_FILE, "r") as file:
        return json.load(file)


def save_tasks(tasks):
    with open(TASKS_FILE, "w") as file:
        json.dump(tasks, file, indent=4)


def add_task(task_name, es_time, due_date):
    tasks = load_tasks()

    tasks[task_name] = {
        "estimated_time": es_time,
        "due_date": due_date
    }

    save_tasks(tasks)


def remove_task(task_name):

    tasks = load_tasks()

    if task_name in tasks:
        del tasks[task_name]

    save_tasks(tasks)


def organize_tasks(tasks):
    due_now = []
    due_later = []
    due_pace = []

    for task, data in tasks.items():

        es_time = data["estimated_time"]
        due_date = data["due_date"]

        paceTime = round(es_time/due_date, 1)

        task_data = {
            "task": task,
            "estimated_time": es_time,
            "due_date": due_date,
            "pace_time": paceTime
        }

        if due_date <= DUE_THRESHOLD:
            due_now.append(task_data)

        elif es_time > TIME_THRESHOLD:
            due_pace.append(task_data)

        else:
            due_later.append(task_data)

    return {
        "due_now": due_now,
        "due_pace": due_pace,
        "due_later": due_later
    }