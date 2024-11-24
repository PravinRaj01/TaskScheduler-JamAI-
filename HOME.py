import streamlit as st
import requests
import pandas as pd
from scheduler import add_and_schedule_tasks

# JamAI API Base Credentials
JAMAI_PAT = "jamai_pat_76742d6264753e5f03549a252a41dc9e04fffdd8d9127da2"
PROJECT_ID = "proj_be0206ceff107d8fa72f040e"
BASE_URL = "https://api.jamaibase.com"
TASK_TABLE_ID = "daily_task_scheduler"  # Action table for tasks
TIP_TABLE_ID = "productivity_tips"  # Action table for motivational tips

# API Headers
headers = {
    "Authorization": f"Bearer {JAMAI_PAT}",
    "X-PROJECT-ID": PROJECT_ID,
    "Content-Type": "application/json",
    "Accept": "application/json"
}


# Function to add a task to JamAI
def add_task_to_table(task_name, priority, estimated_time):
    url = f"{BASE_URL}/api/v1/gen_tables/action/rows/add"
    payload = {
        "data": [
            {
                "task_name": task_name,
                "priority": priority,
                "estimated_time": estimated_time
            }
        ],
        "table_id": TASK_TABLE_ID,
        "stream": False
    }
    response = requests.post(url, json=payload, headers=headers)
    if response.status_code == 200:
        st.success("Task added successfully!")
    else:
        st.error(f"Failed to add task. Error {response.status_code}: {response.text}")


# Function to fetch tasks from JamAI
def fetch_tasks_from_table():
    url = f"{BASE_URL}/api/v1/gen_tables/action/{TASK_TABLE_ID}/rows"
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        rows = response.json().get("items", [])
        if rows:
            tasks = [
                {
                    "task_name": row["task_name"]["value"],
                    "priority": row["priority"]["value"],
                    "estimated_time": row["estimated_time"]["value"]
                }
                for row in rows
            ]
            return tasks
        else:
            return []
    else:
        st.error(f"Failed to fetch tasks. Error {response.status_code}: {response.text}")
        return []


# Function to fetch motivation from the productivity_tips action table
def fetch_motivation_from_table(task_count):
    url = f"{BASE_URL}/api/v1/gen_tables/action/{TIP_TABLE_ID}/rows"
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        rows = response.json().get("items", [])
        if not rows:
            return "No motivational tips available in the database."

        # Find the appropriate motivation based on task count
        for row in rows:
            table_task_count = row.get("task_count", {}).get("value", "").strip()
            motivation = row.get("motivation", {}).get("value", "Motivational text not found.")

            # Handle exact matches
            if table_task_count.isdigit() and int(table_task_count) == task_count:
                return motivation

            # Handle ranges (e.g., "2-3")
            if "-" in table_task_count:
                lower, upper = map(int, table_task_count.split("-"))
                if lower <= task_count <= upper:
                    return motivation

            # Handle "6+" or similar
            if "+" in table_task_count:
                lower = int(table_task_count.rstrip("+"))
                if task_count >= lower:
                    return motivation

        return "No matching motivational tip found."
    else:
        st.error(f"Failed to fetch motivational tips. Error {response.status_code}: {response.text}")
        return "Error fetching motivational tips."


# Set up page configuration
st.set_page_config(page_title="Productivity Manager", page_icon="📋", layout="wide")

# Add content to the main page
st.title("🏠 Welcome to Productivity Manager!")
st.markdown(
    """
    **Features:**
    - Add and manage tasks with a smart scheduler.
    - Get motivational quotes to stay productive.
    - Use the chatbot to get productivity advice.
    """
)

# Task Submission Section
st.subheader("Add a New Task")
with st.form(key="add_task_form"):
    task_name = st.text_input("Task Name", placeholder="E.g., Complete report")
    priority = st.selectbox("Priority", ["High", "Medium", "Low"])
    estimated_time = st.number_input("Estimated Time (hours)", min_value=0, value=1)
    submit_task = st.form_submit_button("Add Task")

    if submit_task:
        if task_name:
            add_task_to_table(task_name, priority, estimated_time)
        else:
            st.warning("Please provide a task name.")

# Fetch tasks to calculate the count
fetched_tasks = fetch_tasks_from_table()
task_count = len(fetched_tasks)

# Fetch motivation based on the task count
motivation_of_the_day = fetch_motivation_from_table(task_count)

# Display Motivation of the Day
st.subheader("Motivation of the Day")
st.write(f"💡 {motivation_of_the_day}")
