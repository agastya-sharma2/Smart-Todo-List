from datetime import datetime, date
import storage
import constants

def refresh(raw):
    updated_tasks = empty_task_groups()

    today = date.today()
    today_str = today.strftime("%Y-%m-%d")

    all_tasks = []
    for category in raw.values():
        all_tasks.extend(category)

    for task in all_tasks:
        daysDue = calculate_days_due(task["due_date"])

        # Inject the updated days left for the frontend template
        task["daysDue"] = daysDue
        est_time = task["estimated_time"]

        # Sort into the correct category based on today's remaining days
        if est_time > constants.TIME_THRESHOLD:
            updated_tasks["due_pace"].append(task)

            # Check if it was already completed today
            # We compare the string date to today's string date
            already_done_today = task.get("last_completed") == today_str

            if daysDue >= 0 and not already_done_today:
                updated_tasks["due_now"].append(create_daily_slice(task, today_str))

        elif daysDue <= constants.DUE_THRESHOLD:
            updated_tasks["due_now"].append(task)
        else:
            updated_tasks["due_later"].append(task)

    return updated_tasks

def add_task(task_name, est_time, due_date):
    tasks = load_tasks()

    # Calculate pace time on creation
    daysDue = calculate_days_due(due_date)

    pace_time = int(round(est_time / daysDue, 0)) if daysDue > 0 else est_time
    

    # Build task object
    task_data = {
        "task": task_name,
        "estimated_time": est_time,
        "due_date": due_date,
        "pace_time": pace_time,
        "current_time": 0,
        "last_completed": "",
        "is_slice": False
    }

    # Add task to any category; refresh() will recategorize it.
    tasks["due_later"].append(task_data)

    final_tasks = refresh(tasks)

    storage.save_tasks(final_tasks)

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
                    if task["current_time"] >= task["estimated_time"]:
                        tasks[category] = [t for t in tasks[category] if t["task"] != task["task"]]
    else:
        # Scenario B: User completed a regular task
        for category in tasks:
            tasks[category] = [t for t in tasks[category] if t["task"] != task_name]

    storage.save_tasks(tasks)

def load_tasks():
    raw = storage.load_raw_tasks()
    return refresh(raw)

def create_daily_slice(task, today_str):
    return {
        "task": f"Daily Slice: {task['task']}",
        "parent_task": task["task"],
        "estimated_time": task["pace_time"],
        "due_date": today_str,
        "daysDue": 0,
        "last_completed": task.get("last_completed", ""),
        "is_slice": True
    }

def empty_task_groups():
    return {
        "due_now": [],
        "due_pace": [],
        "due_later": []
    }

def calculate_days_due(due_date):
    parsed_date = datetime.strptime(due_date, "%Y-%m-%d").date()
    return (parsed_date - date.today()).days