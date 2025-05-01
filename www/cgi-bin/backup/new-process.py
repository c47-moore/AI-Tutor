#!/usr/bin/python3

import cgi
import json
import requests
import sys

# Increase timeout to 30 seconds
TIMEOUT = 30

# Ollama API URL
OLLAMA_URL = "http://gpu-pc:11434/api/generate"

# System role message: instructs the LLM to teach a child
SYSTEM_ROLE = "You are a friendly and patient teacher explaining things to a young child in a simple and engaging way."

def get_ai_response(user_message):
    payload = {
        "model": "deepseek-r1:1.5b",
        "prompt": user_message,
        "stream": False
    }

    try:
        response = requests.post(OLLAMA_URL, data=json.dumps(payload), timeout=TIMEOUT)
        response.raise_for_status()
        ai_response = response.json().get("response", "Sorry, I couldn't understand that.")
        return ai_response.strip()
    except requests.exceptions.RequestException as e:
        return f"Error: {str(e)}"

def main():
    """Handles incoming requests and returns AI-generated responses."""
    print("Content-type: text/plain\n")

    # Parse user input
    form = cgi.FieldStorage()
    user_message = form.getvalue("message", "").strip()

    if not user_message:
        print("Error: No message received.")
        sys.exit(1)

    # Get AI-generated response
    response_text = get_ai_response(user_message)

    # Return response to the client
    print(response_text)

if __name__ == "__main__":
    main()
