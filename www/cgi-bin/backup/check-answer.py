#!/usr/bin/python3

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

GEMINI_API_KEY = "AIzaSyBXkHJj-9jJjz_PpjK9lZ2rB1S-R0PrQrM"
SYSTEM_ROLE = "You are an AI evaluating a response to a predefined question."
PROMPT = "Evaluate my response to a predefined question.\n"\
    "The question was: $QUESTION\n"\
    "My response was: $RESPONSE\n"\
    "The expected answer was: $EXPECTED\n"\
    "If my response was correct, reply with only the word \"correct\". "\
    "However, if the my response is not correct, explain what is wrong "\
    "with the my response and what I may have misunderstood. "\
    "If I am wrong, do not give me the correct answer, just invite me to try again."

def gemini_response(message):
    client = genai.Client(api_key=GEMINI_API_KEY)

    response = client.models.generate_content(
        model="gemini-2.0-flash",
        config=types.GenerateContentConfig(system_instruction=SYSTEM_ROLE),
        contents=[message]
    )

    return (response.text)


def evaluate_answer(qid, user_message):
    db = connect_database()
    cur = db.cursor()
    sql = "SELECT question,answer FROM tests WHERE id = {}".format(qid)
    cur.execute(sql)
    if cur.rowcount != 1:
        print("Error: unable to find question in database!")
    else:
        row = cur.fetchone()

    prompt = PROMPT.replace("$QUESTION", row[0])
    prompt = prompt.replace("$EXPECTED", row[1])
    prompt = prompt.replace("$RESPONSE", user_message)
    response = gemini_response(prompt)
    print(response)

    db.close()

def main():
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

    if re.search("^q[0-9]*:", user_message):
        token = re.split(':', user_message, 1)
        qid = token[0][1:]
        user_message = token[1]
        evaluate_answer(qid, user_message)
    else:
        print("Error: invalid request received.")

if __name__ == "__main__":
    main()
