import requests

url = "https://api.jamaibase.com/api/v1/gen_tables/action/rows/add"

payload = {
    "data": [
        {
            "task_name": "Complete report",
            "priority": "High",
            "estimated_time": 2  # Ensure this matches your table schema
        }
    ],
    "table_id": "daily_task_scheduler",
    "stream": False  # Disable streaming
}
headers = {
    "accept": "application/json",
    "content-type": "application/json",
    "authorization": "Bearer jamai_pat_76742d6264753e5f03549a252a41dc9e04fffdd8d9127da2",
    "X-PROJECT-ID": "proj_be0206ceff107d8fa72f040e"
}

response = requests.post(url, json=payload, headers=headers)

if response.status_code == 200:
    print("Row added successfully!")
    try:
        print(response.json())  # Parse JSON response
    except requests.exceptions.JSONDecodeError:
        print("Response is not JSON. Raw response:", response.text)
else:
    print(f"Failed to add row. Error {response.status_code}: {response.text}")
