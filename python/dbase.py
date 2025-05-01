import MySQLdb

def connect_database():
    db = MySQLdb.connect(host="localhost", user="chaya", passwd="db242313", db="aitutor")
    return db
