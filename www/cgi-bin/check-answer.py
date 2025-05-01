#!/usr/bin/python3

import cgi
import json
import sys
import re

# We don't want people to be able to WGET details on
# our database or AI config, so we keep these in
# a different location outside the http-accessible domain
sys.path.insert(0, "/home/chaya/shared/aitutor/python/")
from dbase import connect_database
from gemini import gemini_check_answer

PROMPT = "Evaluate my response to a predefined question.\n"\
    "The question was: $QUESTION\n"\
    "My response was: $RESPONSE\n"\
    "The expected answer was: $EXPECTED\n"\
    "My response and the expected answer are not case-sensitive. "\
    "If my response was correct, reply with only the word \"correct\". "\
    "However, if the my response is not correct, explain what is wrong "\
    "with the my response and what I may have misunderstood. "\
    "If I am wrong, do not give me the correct answer, just invite me to try again."

# Update the database to mark a subtopic as mastered
def update_mastery(tid, parent):
    cur = db.cursor()
    sql = "UPDATE progress SET status=2 WHERE uid={} and topic_id={}".format(uid, tid)
    cur.execute(sql)

    # Now check if this has completed the chapter, and if so mark
    # the chapter as 'mastered'. First, get a list of topics in
    # this chapter (i.e. the parent topic)
    sql = "SELECT id FROM topics WHERE parent={}".format(parent)
    cur.execute(sql)
    topics = cur.fetchall()

    # Loop through all the topics to check that there is an entry
    # for each one for this user and, if so, that it has been
    # marked as mastered. If the subtopic does not exist, or hasn't
    # been marked as mastered, we bail without updating the chapter (parent)
    for row in topics:
        # See if this subtopic has an entry in the user's progress
        sql = "SELECT status FROM progress WHERE uid={} AND topic_id={}".format(uid, row[0])
        cur.execute(sql)
        if cur.rowcount == 0:
            # No progress entry for this topic and user
            return

        status = cur.fetchone()
        if status[0] != 2:
            # Progress entry exists, but not completed
            return

    # If we get here, then all the chapter subtopics have an entry
    # in the progress table for this user, and all subtopics have been
    # mastered. We can now mark the chapter as mastered.
    sql = "UPDATE progress SET status=2 WHERE uid={} and topic_id={}".format(uid, parent)
    cur.execute(sql)


def evaluate_answer(qid, user_message):
    global db
    db = connect_database()
    cur = db.cursor()
    sql = "SELECT question,answer,topic,topics.parent from tests "\
        "LEFT JOIN topics ON topics.id=tests.topic WHERE tests.id = {}".format(qid)
    cur.execute(sql)
    if cur.rowcount != 1:
        print("System Error: unable to find question in database!")
        return

    row = cur.fetchone()
    tid = row[2]
    chapter = row[3]
    prompt = PROMPT.replace("$QUESTION", row[0])
    prompt = prompt.replace("$EXPECTED", row[1])
    prompt = prompt.replace("$RESPONSE", user_message)
    response = gemini_check_answer(prompt)

    # Update the database if the user got the answer correct
    if response.strip() == "correct":
        sql = "UPDATE user_tests SET score=2 WHERE uid={} AND qid={}".format(uid, qid)
        cur.execute(sql)

        # Check if the user has passed all the tests, in which case
        # mark the topic as 'mastered'
        sql = "SELECT score FROM user_tests WHERE score!=2 AND uid={} AND tid={}".format(uid, tid)
        cur.execute(sql)
        if cur.rowcount == 0:
            update_mastery(tid, chapter)

    print(response)

    db.commit()
    db.close()

def main():
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

    if re.search("^q[0-9]*:", user_message):
        token = re.split(':', user_message, 1)
        qid = token[0][1:]
        user_message = token[1]
        evaluate_answer(qid, user_message)
    else:
        print("Error: invalid request received.")

if __name__ == "__main__":
    main()
