
import sys
sys.path.insert(0, "/home/chaya/shared/aitutor/python/")

import json
from google import genai
from google.genai import types,errors
from dbase import connect_database 

system_role = "You are a friendly and patient teacher explaining things "\
    "to a young child in a simple and engaging way."

GEMINI_API_KEY = "<INSERT API KEY HERE>"
ANSWER_ROLE = "You are an AI evaluating a response to a predefined question."

def gemini_check_answer(message):
    client = genai.Client(api_key=GEMINI_API_KEY)
    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            config=types.GenerateContentConfig(system_instruction=ANSWER_ROLE),
            contents=[message]
        )
    except errors.APIError as e:
        return ("AI Error {}: {}".format(e.code, e.message))

    return (response.text)


def gemini_stream_response(messages):
    llm_response = ''
    client = genai.Client(api_key=GEMINI_API_KEY)
    try:
        response = client.models.generate_content_stream(
            model="gemini-2.0-flash",
            config=types.GenerateContentConfig(system_instruction=system_role),
            contents=messages
        )
    except errors.APIerror as e:
        print("Error {}: {}".format(e.code, e.message))
        return

    for chunk in response:
        print(chunk.text, end="")
        llm_response = llm_response + chunk.text

    # Store the conversation context so far along with the LLM's
    # latest response
    messages.extend([{ "role": "model", "parts": [{ "text": llm_response }]}])
    context = json.dumps(messages);
    query = """REPLACE INTO context VALUES (%s,%s)"""
    cur = db.cursor()

    try:
        result = cur.execute(query, (uid, context))
        db.commit()
    except MySQLdb.Error as err:
        print("DB error: {}".format(err))


def load_context(user_message):
    global system_role

    cur = db.cursor()
    cur.execute("SELECT content FROM prompt WHERE label='SYSTEM'")
    if cur.rowcount == 1:
        row = cur.fetchone()
        system_role = row[0];

    system_role = system_role + "The user's name is " + user_name + \
        "Please address the user by name."

    # Now load and append the conversation context (previous
    # exchanges) with this user, so that the LLM can reply
    # within that context
    cur.execute("SELECT messages FROM context WHERE uid=" + uid)
    if cur.rowcount == 1:
        row = cur.fetchone()
        messages = json.loads(row[0])

        # Just to prevent the conversation context overflowing
        # we trim the oldest exchange if the chain is over 1000
        # tokens long.
        if len(messages) > 1000:
            del messages[0:2]
        messages.extend([{ "role": "user", "parts": [{ "text": user_message }]}])
    else:
        messages = [{ "role": "user", "parts": [{ "text": user_message }]}]

    return messages


def process_command(cmdstr):
    command = cmdstr.split(':')

    # topic id is first argument to command
    cur = db.cursor()
    cur.execute("SELECT * FROM topics WHERE id=" + command[1])
    if cur.rowcount != 1:
        print("Error: Topic id row count != 1: ", cur.rowcount)
        return
    else:
        row = cur.fetchone()
        topic_name = row[2]
        topic_desc = row[3];

    if command[0] == "new":
        cur = db.cursor()
        cur.execute("SELECT content FROM prompt WHERE label='BEGIN'")
        if cur.rowcount == 1:
            row = cur.fetchone()
            prompt = row[0]
        else:
            prompt = 'Teach me how to $TOPIC and use example problems to test my understanding.'

        prompt = prompt.replace('$TOPIC', topic_desc)
    elif command[0] == "resume":
        cur = db.cursor()
        cur.execute("SELECT content FROM prompt WHERE label='RESUME'")
        if cur.rowcount == 1:
            row = cur.fetchone()
            prompt = row[0]
        else:
            prompt = 'Remind me what we discussed on how to $TOPIC, and continue teaching me.'
        prompt = prompt.replace('$TOPIC', topic_name)
    else:
        print("<b>command:</b> ", command[0], "not found, topic = ", topic_name)
        return

    messages = load_context(prompt)
    gemini_stream_response(messages)


def gemini_send_message(userid, user_message):
    global db
    global uid
    global user_name

    uid = userid
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
        process_command(user_message[4:])
    else:
        messages = load_context(user_message)
        gemini_stream_response(messages)

    db.close()
