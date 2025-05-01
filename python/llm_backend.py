#!/usr/bin/python3

from ollama import Client
from google import genai
from google.genai import types
import cgi
import json
import sys
import re

# We don't want people to be able to WGET the database
# user and password info
sys.path.insert(0, "/home/chaya/shared/aitutor/python/")
from dbase import connect_database 
from prompt import system_role

# Ollama host to use (can be localhost or a remote host)
OLLAMA_URL = 'http://gpu-pc:11434'

# The 'llm' argument selects the model to use in the ollama->client call.
# The model must be installed on the ollama server, of course.
#
# llama3.2 is fast, and produces linguistically acceptable output but
# it makes terrible mistakes with maths.
#
# deepseek-r1 is fairly quick but prone to hallucinations. It also emits
# it's 'reasoning process' between <think>...</think> tags which would need
# to be filtered out of the response.
#
# phi4 is a 9.1 GB LLM model, and produces good quality output but is slower
# as it's at the limit of the GPU VRAM on the server (currently running with
# nVidia RTX 3080 with 10 GB VRAM. This results in a 15% CPU / 85% GPU split.
#
def stream_ai_response(messages, llm):
    llm_response = '';
    client = Client(host=OLLAMA_URL)

    # Stream the LLM output as it comes in
    for chunk in client.chat(model=llm, messages=messages, stream=True):
        llm_response = llm_response + chunk['message']['content']
        print(chunk['message']['content'], end='', flush=True)

    # Store the conversation context so far, but remove the system prompt
    # at the start
    messages.pop(0)
    messages.extend([{'role': 'assistant', 'content': llm_response}])
    context = json.dumps(messages);
    query = """REPLACE INTO context VALUES (%s,%s)"""
    cur = db.cursor()

    try:
        result = cur.execute(query, (uid, context))
        db.commit()
    except MySQLdb.Error as err:
        print("DB error: {}".format(err))

# this is for connecting to the Google/Gemini model as an
# alternate AI
def stream_gemini_response(messages):
    client = genai.Client(api_key=GEMINI_API_KEY)
    response = client.models.generate_content(
        model="gemini-2.0-flash",
        config=types.GenerateContentConfig(system_instruction=SYSTEM_ROLE),
        contents=messages
    )

# Load the existing conversation context for this user
# with the default system prompt as the first entry, but
# also making sure we keep the context under 1000 messages
# in overall length
#
def load_context():
    # First, get the system prompt from the database
    # if one has been stored. This ensures that any
    # update to the system prompt will apply to future
    # interactions.
    cur = db.cursor()
    cur.execute("SELECT content FROM prompt WHERE label='SYSTEM'")
    if cur.rowcount == 1:
        row = cur.fetchone()
        role = row[0];
    else:
        role = system_role

    # append the user's name for personalisation
    role = role + " The user's name is " + user_name + \
        ". Refer to the user by their name."
    messages = [{"role": "system", "content": role}]

    # Now load and append the conversation context (previous
    # exchanges) with this user, so that the LLM can reply
    # within that context
    cur.execute("SELECT messages FROM context WHERE uid=" + uid)
    if cur.rowcount == 1:
        row = cur.fetchone()
        messages.extend(json.loads(row[0]))

        # Just to prevent the conversation context overflowing
        # we trim the oldest exchange if the chain is over 1000
        # tokens long. We keep the very first one, as it's the
        # system prompt.
        if len(messages) > 1000:
            del messages[1:3]

    return messages


# Get the conversation context, add the latest user's message
# and return the result to the caller
#
def build_messages(user_message):
    messages = load_context()
    messages.extend([{'role': 'user', 'content': user_message}])

    return messages


def build_messages2(user_message, llm):
    if (llm == "gemini"):
        this_message = { "role": "user",
            "parts": [{ "text": user_message }]}


def process_command(cmdstr, llm):
    command = cmdstr.split(':')

    # topic id is first argument to command
    cur = db.cursor()
    cur.execute("SELECT * FROM topics WHERE id=" + command[1])
    if cur.rowcount != 1:
        print("Topic id row count != 1: ", cur.rowcount)
    else:
        row = cur.fetchone()
        topic_name = row[2]
        topic_desc = row[3];

    if command[0] == "new":
        messages = load_context()
        cur = db.cursor()
        cur.execute("SELECT content FROM prompt WHERE label='BEGIN'")
        if cur.rowcount == 1:
            row = cur.fetchone()
            prompt = row[0]
        else:
            prompt = 'Teach me how to $TOPIC and use example problems to test my understanding.'

        prompt = prompt.replace('$TOPIC', topic_desc)
        messages.extend([{'role': 'user', 'content': prompt}])
        # DEBUG: print("<pre>messages:\n\n", messages, "</pre>\n")
        stream_ai_response(messages, llm)
    elif command[0] == "resume":
        messages = load_context()
        cur = db.cursor()
        cur.execute("SELECT content FROM prompt WHERE label='RESUME'")
        if cur.rowcount == 1:
            row = cur.fetchone()
            prompt = row[0]
        else:
            prompt = 'Remind me what we discussed on how to $TOPIC, and continue teaching me.'

        prompt = prompt.replace('$TOPIC', topic_name)
        messages.extend([{'role': 'user', 'content': prompt}])
        stream_ai_response(messages, llm)
    else:
        print("<b>command:</b> ", command[0], ", topic = ", topic_name)
        return


def process_message(user_id, user_message, llm):
    global db
    global uid
    global user_name

    uid = user_id
    # Get the user's first name from the database
    db = connect_database()
    cur = db.cursor()
    cur.execute("SELECT firstname FROM users WHERE id=" + uid)
    if cur.rowcount != 1:
        print("User id row count != 1: ", cur.rowcount)
        user_name = "not known"
    else:
        row = cur.fetchone()
        user_name = row[0]

    if user_message.startswith("cmd:"):
        process_command(user_message[4:], llm)
    else:
        messages = build_messages(user_message)
        stream_ai_response(messages, llm)
    db.close()
