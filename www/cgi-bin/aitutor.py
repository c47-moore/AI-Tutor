#!/usr/bin/python3

import cgi
import sys

# We don't want people to be able to WGET the database
# user and password info
sys.path.insert(0, "/home/chaya/shared/aitutor/python/")
from gemini import gemini_send_message

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
    gemini_send_message(uid, user_message)

if __name__ == "__main__":
    main()
