import sqlite3
import sys

if len(sys.argv)==1:
    print("Please specify database")
    exit(0)
conn = sqlite3.connect(sys.argv[1])
c = conn.cursor()
c.execute("ALTER TABLE rute ADD COLUMN sector VARCHAR;")
c.execute("ALTER TABLE rute ADD COLUMN tag VARCHAR;")

c.execute("ALTER TABLE gym ADD COLUMN admin VARCHAR;")
c.execute("ALTER TABLE gym ADD COLUMN sectors VARCHAR;")
c.execute("ALTER TABLE gym ADD COLUMN tags VARCHAR;")
c.execute("ALTER TABLE gym ADD COLUMN edit TIMESTAMP DEFAULT '2018-02-21 20:55:08.000000'")
c.execute("ALTER TABLE gym ADD COLUMN status INTEGER DEFAULT 0")
conn.commit()


for id, uuid in c.execute('SELECT id,uuid FROM GYM').fetchall():
    # c.execute('INSERT INTO sector (uuid, name, gym) values ("{}","{}","{}")'.format(id, "Uncategorized", uuid))
    c.execute('UPDATE rute SET sector="{}" WHERE gym="{}"'.format(id, uuid))

conn.commit()
conn.close()
