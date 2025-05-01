#!/usr/bin/python3

from prompt import system_role
from dbase import connect_database

db = connect_database()
cur = db.cursor()

query = "UPDATE prompt SET content=\"" + \
    system_role + "\" WHERE label=\"SYSTEM\""

cur.execute(query);
db.commit()

db.close()

