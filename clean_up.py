import sqlite3
import sys

if len(sys.argv)==1:
    print("Please specify database")
    exit(0)
conn = sqlite3.connect(sys.argv[1])
c = conn.cursor()

# Remove dublicate users
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

    users = c.execute("SELECT id,name,COUNT(*) FROM user where gym='{}'".format(uuid)).fetchall()
    try:    
        s = raw_input('Delete {}? It is used by {} users [y/N]'.format(name, users))
    except UnicodeEncodeError:
        s = raw_input('Delete id={}? [y/N]'.format(idd))
    if "y" in s.lower():
        c.execute('DELETE FROM gym WHERE id={}'.format(idd))
        conn.commit()
        try:    
            print("Deleted {}".format(name))
        except UnicodeEncodeError:
            print("Deleted id={}".format(idd))
            
print("\nMerge aaks")
good = '"e1e35b58-502d-4dbb-8632-a9f520c8e7cb"'
bad = '("6efd8f49-2a08-4b9b-a767-a04acc209948","b7d8b40d-e0c0-4579-8768-5aaea657990d")'

print(len(c.execute('SELECT name, uuid FROM rute WHERE gym in {}'.format(bad)).fetchall()))
print(len(c.execute('SELECT name FROM user WHERE gym in {}'.format(bad)).fetchall()))

print(len(c.execute('SELECT name, uuid FROM rute WHERE gym={}'.format(good)).fetchall()))
print(len(c.execute('SELECT name FROM user WHERE gym={}'.format(good)).fetchall()))

c.execute('UPDATE rute SET gym={} WHERE gym in {}'.format(good, bad))
c.execute('UPDATE user SET gym={} WHERE gym in {}'.format(good, bad))

print(len(c.execute('SELECT name, uuid FROM rute WHERE gym in {}'.format(bad)).fetchall()))
print(len(c.execute('SELECT name FROM user WHERE gym in {}'.format(bad)).fetchall()))

print(len(c.execute('SELECT name, uuid FROM rute WHERE gym={}'.format(good)).fetchall()))
print(len(c.execute('SELECT name FROM user WHERE gym={}'.format(good)).fetchall()))

c.execute('DELETE FROM gym WHERE uuid in {}'.format(bad))


conn.commit()
conn.close()
