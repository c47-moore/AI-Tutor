#!/usr/bin/python3

from ollama import Client
import json
import sys
import re

# System role message: instructs the LLM to respond as if
# it is teaching a child
SYSTEM_ROLE = "You are a friendly and patient teacher explaining things to a \
    young child in a simple and engaging way."

# Model to use
#MODEL = 'deepseek-r1:latest'
MODEL = 'llama3.2:3b'

# Ollama host to use (can be localhost or a remote host)
OLLAMA_URL = 'http://gpu-pc:11434'

# open a client connection to the Ollama instance and get a response from the
# specified LLM model
def stream_ai_response(user_message):
    client = Client(host=OLLAMA_URL)
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

    for chunk in client.chat(model=MODEL, messages=messages, stream=True):
        print(chunk['message']['content'], end='', flush=True)


def main():
    user_message = 'Why is the sky blue?'

    # Get AI-generated response. Reasoning LLMs like deepseek
    # can include its thinking process, between <think>...</think> tags.
    # If these exist, strip them out of the response.
    #response_text = re.sub(r"<think>.*?</think>\n\n", "",
    #    get_ai_response(user_message), flags=re.DOTALL)
    stream_ai_response(user_message)

if __name__ == "__main__":
    main()
