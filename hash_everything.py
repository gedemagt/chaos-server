import sqlite3
import bcrypt
import sys

if len(sys.argv)==1:
    print("Please specify database")
    exit(0)
conn = sqlite3.connect(sys.argv[1])
c = conn.cursor()

users = c.execute('SELECT id,name,password,uuid FROM user').fetchall()
for id, name, password, uuid in users:
    if not password.startswith("$2a$"):
        hash = bcrypt.hashpw(password, bcrypt.gensalt())
        p = c.execute('UPDATE user SET password="{}" WHERE id={}'.format(hash, id))

conn.commit()
conn.close()
