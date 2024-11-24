import streamlit as st
import requests
import json

# JamAI API Base Credentials
JAMAI_API_KEY = "jamai_pat_76742d6264753e5f03549a252a41dc9e04fffdd8d9127da2"
PROJECT_ID = "proj_be0206ceff107d8fa72f040e"
BASE_URL = "https://api.jamaibase.com"
CHAT_COMPLETIONS_ENDPOINT = f"{BASE_URL}/api/v1/chat/completions"
CHAT_TABLE_ID = "productivity_chat"  # Chat table ID

# API Headers
headers = {
    "Authorization": f"Bearer {JAMAI_API_KEY}",
    "X-PROJECT-ID": PROJECT_ID,
    "Content-Type": "application/json",
    "Accept": "application/json"
}

# Function to fetch existing responses from the chat table
def fetch_response_from_table(user_input):
    url = f"{BASE_URL}/api/v1/gen_tables/chat/{CHAT_TABLE_ID}/rows"
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        rows = response.json().get("items", [])
        print("Fetched Rows:", rows)  # Debugging: Print all rows
        for row in rows:
            user_value = row.get("User", {}).get("value", "").strip().lower()
            if user_value == user_input.strip().lower():
                return row.get("AI", {}).get("value", "No response found.")
    return None

# Function to add a new row to the chat table
def add_response_to_table(user_input, ai_response):
    url = f"{BASE_URL}/api/v1/gen_tables/chat/{CHAT_TABLE_ID}/rows/add"
    payload = {
        "data": [
            {
                "User": {"value": user_input},  # Wrap values in {"value": ...}
                "AI": {"value": ai_response}    # Match the fetched row structure
            }
        ],
        "table_id": CHAT_TABLE_ID
    }
    response = requests.post(url, headers=headers, json=payload)
    if response.status_code == 200:
        print("Response added to table:", response.json())
        return True
    else:
        print("Error adding response:", response.text)
        return False

# Function to interact with the chatbot using the completions endpoint
def get_chat_response_from_model(user_input):
    payload = {
        "messages": [
            {"role": "user", "content": user_input}
        ],
        "model": "ellm/meta-llama/Llama-3.1-8B-Instruct",
        "temperature": 0.7,
        "max_tokens": 150,
        "stream": True  # Enable streaming
    }
    response = requests.post(CHAT_COMPLETIONS_ENDPOINT, headers=headers, json=payload, stream=True)
    if response.status_code == 200:
        full_response = ""
        for chunk in response.iter_lines():
            if chunk:  # Ignore keep-alive chunks
                chunk_data = chunk.decode("utf-8")
                if chunk_data.startswith("data: "):  # Process data chunks
                    chunk_data = chunk_data[6:]  # Remove "data: " prefix
                    if chunk_data.strip() == "[DONE]":
                        break  # End of stream
                    try:
                        json_data = json.loads(chunk_data)
                        if "choices" in json_data and json_data["choices"]:
                            content = json_data["choices"][0]["delta"].get("content", "")
                            full_response += content
                    except json.JSONDecodeError:
                        continue  # Skip invalid JSON chunks
        return full_response.strip()
    else:
        return f"Error: {response.status_code} - {response.text}"

# Main function to handle chatbot responses
def handle_chat(user_input):
    # Fetch from table first
    existing_response = fetch_response_from_table(user_input)
    if existing_response:
        return existing_response

    # Generate a new response if not found
    ai_response = get_chat_response_from_model(user_input)

    # Add new response to the table if generated successfully
    if ai_response and not ai_response.startswith("Error"):
        success = add_response_to_table(user_input, ai_response)
        if not success:
            print("Failed to store the new response in the chat table.")
    return ai_response

# Streamlit Page Configuration
st.set_page_config(page_title="ScheduleAI", page_icon="🤖", layout="wide")

# Chatbot Page Content
st.title("🤖 ScheduleAI Chatbot")

# Input Form
with st.form(key="chat_form"):
    user_input = st.text_input("You:", placeholder="Ask me anything about productivity...")
    submit_button = st.form_submit_button(label="Send")

# Handle User Input and Display AI Response
if submit_button and user_input:
    ai_response = handle_chat(user_input)
    st.markdown(f"**AI:** {ai_response}")
