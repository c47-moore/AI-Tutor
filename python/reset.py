#!/usr/bin/python3

from dbase import connect_database

db = connect_database()
cur = db.cursor()

cur.execute("DELETE FROM context WHERE uid=1")
cur.execute("DELETE FROM progress WHERE uid=1")
cur.execute("DELETE FROM user_tests WHERE uid=1")
db.commit()

db.close()

