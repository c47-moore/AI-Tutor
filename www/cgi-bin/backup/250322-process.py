#!/usr/bin/python3

from ollama import Client
import cgi
import json
import sys
import re

# We don't want people to be able to WGET the database
# user and password info
sys.path.insert(0, "/home/chaya/shared/aitutor/python/")
from dbase import connect_database 
from prompt import system_role

topic_query = 'SELECT id,parent,name FROM topics ORDER BY COALESCE(if(parent=0,NULL,parent), id), parent IS NOT NULL, id'

# This selects the model to use in the ollama->client call. The model must
# be installed on the ollama server, of course.
#
# llama3.2 is fast, and produces acceptable output.
#
# deepseek-r1 is fairly quick but prone to hallucinations. It also emits
# it's 'reasoning process' between <think>...</think> tags which would need
# to be filtered out of the response.
#
# phi4 is a 9.1 GB LLM model, and produces good quality output but is slower
# as it's at the limit of the GPU VRAM on the server (currently running with
# nVidia RTX 3080 with 10 GB VRAM. This results in a 15% CPU / 85% GPU split.
#
MODEL = 'llama3.2:3b'
#MODEL = 'deepseek-r1:1.5b'
#MODEL = 'phi4'

# Ollama host to use (can be localhost or a remote host)
OLLAMA_URL = 'http://gpu-pc:11434'

# open a client connection to the Ollama instance and get a response from the
# specified LLM model
def stream_ai_response(messages):
    llm_response = '';
    client = Client(host=OLLAMA_URL)

    # Stream the LLM output as it comes in
    for chunk in client.chat(model=MODEL, messages=messages, stream=True):
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


def build_messages(user_name, user_message):
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
    # debug use only: print("<b>role</b><p>", role, "</p>")
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

    messages.extend([{'role': 'user', 'content': user_message}])

    return messages


def main():
    global system_role
    global db
    global uid
    print("Content-type: text/plain\n")

    # Get the user input from the browser client form
    form = cgi.FieldStorage()
    user_message = form.getvalue("message", "").strip()
    if not user_message:
        print("Error: No message received.")
        sys.exit(1)

    # The form data should contain our logged in user
    # ID from the session. We'll keep 'uid' global so that
    # we can use it for future database queries
    uid = form.getvalue("uid", "").strip()

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

    db = connect_database()

    messages = build_messages(user_name, user_message)
    stream_ai_response(messages)
    db.close()

if __name__ == "__main__":
    main()
