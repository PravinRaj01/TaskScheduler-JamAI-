from datetime import datetime, timedelta

# Function to manage and calculate sequential scheduled times
def calculate_schedule(tasks):
    # Sort tasks by priority (High > Medium > Low)
    priority_order = {"High": 1, "Medium": 2, "Low": 3}

    # Validate tasks and filter out invalid entries
    valid_tasks = [
        task for task in tasks
        if "priority" in task and "estimated_time" in task and task["priority"] in priority_order
    ]

    # Sort valid tasks by priority
    valid_tasks = sorted(valid_tasks, key=lambda x: priority_order[x["priority"]])

    # Initialize the start time
    start_time = datetime.strptime("08:00", "%H:%M")

    # Calculate scheduled times
    for task in valid_tasks:
        end_time = start_time + timedelta(hours=task["estimated_time"])
        task["scheduled_time"] = f"{start_time.strftime('%H:%M')}-{end_time.strftime('%H:%M')}"
        start_time = end_time  # Update start time for the next task

    return valid_tasks

# Function to add tasks and calculate schedule
def add_and_schedule_tasks(task_name, priority, estimated_time, existing_tasks):
    # Add the new task to the list
    new_task = {"task_name": task_name, "priority": priority, "estimated_time": estimated_time}
    existing_tasks.append(new_task)

    # Calculate schedule
    scheduled_tasks = calculate_schedule(existing_tasks)

    # Print the updated schedule
    return scheduled_tasks
