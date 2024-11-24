import streamlit as st
import pandas as pd
from scheduler import add_and_schedule_tasks
import requests
from st_aggrid import AgGrid, GridOptionsBuilder

# JamAI API Base Credentials
JAMAI_PAT = "jamai_pat_76742d6264753e5f03549a252a41dc9e04fffdd8d9127da2"
PROJECT_ID = "proj_be0206ceff107d8fa72f040e"
BASE_URL = "https://api.jamaibase.com"
TASK_TABLE_ID = "daily_task_scheduler"  # Action table for tasks

# API Headers
headers = {
    "Authorization": f"Bearer {JAMAI_PAT}",
    "X-PROJECT-ID": PROJECT_ID,
    "Content-Type": "application/json",
    "Accept": "application/json"
}

# Function to fetch tasks from JamAI
@st.cache_data(show_spinner=False)
def fetch_tasks_from_table():
    """Fetch tasks from JamAI and cache the result."""
    url = f"{BASE_URL}/api/v1/gen_tables/action/{TASK_TABLE_ID}/rows"
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        rows = response.json().get("items", [])
        if rows:
            tasks = [
                {
                    "id": row["ID"],  # Include ID for deletion
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

# Function to delete a task from JamAI
def delete_task_from_table(task_name):
    """Delete a task from JamAI by matching its task name."""
    tasks = fetch_tasks_from_table()
    task_to_delete = next((task for task in tasks if task["task_name"] == task_name), None)
    if not task_to_delete:
        st.error("Task not found.")
        return

    task_id = task_to_delete["id"]
    url = f"{BASE_URL}/api/v1/gen_tables/action/rows/delete"
    payload = {
        "table_id": TASK_TABLE_ID,
        "row_ids": [task_id]  # Specify task ID for deletion
    }
    response = requests.post(url, json=payload, headers=headers)
    if response.status_code == 200:
        st.success(f"Task '{task_name}' removed successfully!")
    else:
        st.error(f"Failed to remove task. Error {response.status_code}: {response.text}")

# Function to delete all tasks
def delete_all_tasks():
    """Delete all tasks from JamAI."""
    tasks = fetch_tasks_from_table()
    if not tasks:
        st.warning("No tasks to delete!")
        return
    task_ids = [task["id"] for task in tasks]
    url = f"{BASE_URL}/api/v1/gen_tables/action/rows/delete"
    payload = {
        "table_id": TASK_TABLE_ID,
        "row_ids": task_ids
    }
    response = requests.post(url, json=payload, headers=headers)
    if response.status_code == 200:
        st.success("All tasks removed successfully!")
    else:
        st.error(f"Failed to remove tasks. Error {response.status_code}: {response.text}")

# Refresh cache function
def refresh_cache():
    """Clears the cached data."""
    fetch_tasks_from_table.clear()

# Page Content
st.title("📅 My Schedule")
st.markdown("Your scheduled tasks are fetched and arranged below.")

# Fetch tasks (either cached or fresh, depending on refresh)
fetched_tasks = fetch_tasks_from_table()

# Display Scheduled Tasks
if fetched_tasks:
    # Arrange tasks using the scheduler
    arranged_tasks = add_and_schedule_tasks(None, None, None, fetched_tasks)
    tasks_df = pd.DataFrame(arranged_tasks)

    # Add Emojis for Priorities
    tasks_df["priority"] = tasks_df["priority"].replace(
        {"High": "🔴 High", "Medium": "🟡 Medium", "Low": "🟢 Low"}
    )

    # Display the table using AgGrid
    gb = GridOptionsBuilder.from_dataframe(tasks_df.drop(columns=["id"]))
    gb.configure_default_column(editable=False, sortable=True, filterable=True)
    gb.configure_pagination(paginationAutoPageSize=True)
    grid_options = gb.build()

    st.write("### Scheduled Tasks (Arranged)")
    AgGrid(
        tasks_df.drop(columns=["id"]),  # Exclude the `id` column from display
        gridOptions=grid_options,
        height=500,
        theme="material"
    )

    # Add a "Download Schedule" Button
    csv = tasks_df.to_csv(index=False)
    st.download_button(
        label="📥 Download Schedule as CSV",
        data=csv,
        file_name="scheduled_tasks.csv",
        mime="text/csv"
    )
else:
    st.warning("No tasks found!")

# Add a refresh button to invalidate the cache
if st.button("🔄 Refresh Schedule"):
    refresh_cache()

# Task Management Section
st.markdown("---")
st.header("🛠️ Task Management")

# Delete Specific Task Section
st.subheader("❌ Delete Specific Task")
if fetched_tasks:
    task_names = [task["task_name"] for task in fetched_tasks]
    selected_task_name = st.selectbox("Select Task to Delete", options=task_names)
    if st.button(f"Delete Task: {selected_task_name}"):
        delete_task_from_table(selected_task_name)
        refresh_cache()
else:
    st.warning("No tasks available for deletion.")

# Delete All Tasks Section
st.subheader("❌ Delete All Tasks")
if st.button("Delete All Tasks"):
    delete_all_tasks()
    refresh_cache()
