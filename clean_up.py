import sqlite3
import sys

if len(sys.argv)==1:
    print("Please specify database")
    exit(0)
conn = sqlite3.connect(sys.argv[1])

# Remove dublicate users
c = conn.cursor()
p = c.execute('SELECT id,name,uuid FROM user GROUP BY uuid HAVING COUNT(*)>1')
dublicates = p.fetchall()
for idd,name,uuid in dublicates:
    p = c.execute('SELECT id FROM user WHERE uuid="{}"'.format(uuid))
    a = p.fetchall()  
    for idd in a[1:]:
        c.execute('DELETE FROM user WHERE id={}'.format(idd[0]))


# Remove dublicate gyms
p = c.execute('SELECT id,name,uuid FROM gym GROUP BY uuid HAVING COUNT(*)>1')
dublicates = p.fetchall()
for idd,name,uuid in dublicates:
    p = c.execute('SELECT id FROM gym WHERE uuid="{}"'.format(uuid))
    a = p.fetchall()  
    for idd in a[1:]:
        c.execute('DELETE FROM gym WHERE id={}'.format(idd[0]))


# Removed unused users
print("\nUnused users")
p = c.execute('SELECT id,name,uuid FROM user WHERE uuid NOT IN (SELECT author FROM rute)')
for idd,name,uuid in p.fetchall():
    if uuid == "admin": 
        continue
    try:    
        s = raw_input('Delete {}? [y/N]'.format(name))
    except UnicodeEncodeError:
        s = raw_input('Delete id={}? [y/N]'.format(idd))
    if "y" in s.lower():
        c.execute('DELETE FROM user WHERE id={}'.format(idd))
        conn.commit()
        try:    
            print("Deleted {}".format(name))
        except UnicodeEncodeError:
            print("Deleted id={}".format(idd))

# Removed unused gyms
print("\nUnused gyms")
p = c.execute('SELECT id,name,uuid FROM gym WHERE uuid NOT IN (SELECT gym FROM rute)')
for idd,name,uuid in p.fetchall():
    if uuid == "UnknowGym": 
        continue

    users = c.execute("SELECT id,COUNT(*) FROM user where gym='{}'".format(uuid)).fetchall()
    try:    
        s = raw_input('Delete {}? It is used by {} users [y/N]'.format(name, len(users)))
    except UnicodeEncodeError:
        s = raw_input('Delete id={}? [y/N]'.format(idd))
    if "y" in s.lower():
        c.execute('DELETE FROM gym WHERE id={}'.format(idd))
        conn.commit()
        try:    
            print("Deleted {}".format(name))
        except UnicodeEncodeError:
            print("Deleted id={}".format(idd))
