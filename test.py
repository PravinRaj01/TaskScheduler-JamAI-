import requests

# JamAI API Base Credentials
JAMAI_PAT = "jamai_pat_76742d6264753e5f03549a252a41dc9e04fffdd8d9127da2"
PROJECT_ID = "proj_be0206ceff107d8fa72f040e"
BASE_URL = "https://api.jamaibase.com"
TASK_TABLE_ID = "daily_task_scheduler"  # Action table for tasks
CHAT_TABLE_ID = "productivity_chat"  # Chat table for chatbot

headers = {
    "accept": "application/json",
    "content-type": "application/json",
    "authorization": "Bearer jamai_pat_76742d6264753e5f03549a252a41dc9e04fffdd8d9127da2",
    "X-PROJECT-ID": "proj_be0206ceff107d8fa72f040e"
}

url = f"{BASE_URL}/api/v1/models"
response = requests.get(url, headers=headers)

if response.status_code == 200:
    models = response.json()
    print("Available Models:", models)
else:
    print(f"Error: {response.status_code} - {response.text}")
