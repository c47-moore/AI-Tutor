#!/usr/bin/python3

from google import genai
from google.genai import types
import cgi
import json
import sys
import re

# System role message: instructs the LLM to respond as if
# it is teaching a child. The extent to which the LLM successfully
# interprets this prompt varies from model to model.
SYSTEM_ROLE = "You are a friendly and patient teacher explaining things to a \
    young child in a simple and engaging way. Use LaTex for any mathematical \
    symbols or equations."

GEMINI_API_KEY = "AIzaSyBXkHJj-9jJjz_PpjK9lZ2rB1S-R0PrQrM"

# open a client connection to Gemini
def stream_ai_response(user_message):
    client = genai.Client(api_key=GEMINI_API_KEY)
    response = client.models.generate_content(
        model="gemini-2.0-flash",
        config=types.GenerateContentConfig(system_instruction=SYSTEM_ROLE),
        contents=[user_message]
    )

    print(response.text)


def main():
    print("Content-type: text/plain\n")

    # Get the user input from the browser client form
    form = cgi.FieldStorage()
    user_message = form.getvalue("message", "").strip()

    if not user_message:
        print("Error: No message received.")
        sys.exit(1)

    stream_ai_response(user_message)

if __name__ == "__main__":
    main()
