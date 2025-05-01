#!/usr/bin/python3

import cgi
import json
import sys
import re

# We don't want people to be able to WGET the database
# user and password info
sys.path.insert(0, "/home/chaya/shared/aitutor/python/")
from llm_backend import process_message

def main():
    print("Content-type: text/plain\n")

    # Get the user input from the browser client form
    form = cgi.FieldStorage()
    user_message = form.getvalue("message", "").strip()
    llm = form.getvalue("model", "").strip()
    if not user_message:
        print("Error: No message received.")
        sys.exit(1)

    # The form data should contain our logged in user
    # ID from the session. We'll keep 'uid' global so that
    # we can use it for future database queries
    uid = form.getvalue("uid", "").strip()
    process_message(uid, user_message, llm)

if __name__ == "__main__":
    main()
