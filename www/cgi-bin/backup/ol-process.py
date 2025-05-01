#!/usr/bin/python3

from ollama import chat
import cgi
import json
import sys
import re

# System role message: instructs the LLM to teach a child
SYSTEM_ROLE = "You are a friendly and patient teacher explaining things to a young child in a simple and engaging way."
#MODEL = 'deepseek-r1:1.5b'
MODEL = 'llama3.2:1b'

def get_ai_response(user_message):
    messages = [
      {
        'role': 'system',
        'content': SYSTEM_ROLE
      },
      {
        'role': 'user',
        'content': user_message
      }
    ]

    response = chat(MODEL, messages=messages)
    return response['message']['content']

def old_main():
    response_text = get_ai_response('Why is the sky blue?')
    print(response_text)

def main():
    print("Content-type: text/plain\n")

    # Parse user input
    form = cgi.FieldStorage()
    user_message = form.getvalue("message", "").strip()

    if not user_message:
        print("Error: No message received.")
        sys.exit(1)

    # Get AI-generated response
    response_text = re.sub(r"<think>.*?</think>\n\n", "",
        get_ai_response(user_message), flags=re.DOTALL)

    # Return response to the client
    print(response_text)

if __name__ == "__main__":
    main()
