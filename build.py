#libraries
import sqlite3

#connection
conn = sqlite3.connect('appt_tracker.db') 
cur = conn.cursor()

# Create table - USERS
cur.execute('''CREATE TABLE IF NOT EXISTS USERS
             (id INTEGER PRIMARY KEY NOT NULL,
             netid text,
             fname text, 
             lname text,
             email text,
             uin int,
             phone text)
             ''')
          
# Create table - LOCATIONS
cur.execute('''CREATE TABLE IF NOT EXISTS LOCATIONS
             (id INTEGER PRIMARY KEY NOT NULL, 
             name text, 
             address text, 
             contact text, 
             email text) 
             ''')
        
# Create table - APPOINTMENTS
cur.execute('''CREATE TABLE IF NOT EXISTS APPOINTMENTS
             (id INTEGER PRIMARY KEY NOT NULL, 
             date date, 
             time string,
             week INTEGER,
             location INTEGER,
             FOREIGN KEY (location) REFERENCES LOCATIONS (id))
             ''')
             
# Create table - USER_APPOINTMENTS
cur.execute('''CREATE TABLE IF NOT EXISTS USER_APPOINTMENTS
             (user INTEGER, 
             appointment INTEGER,
             PRIMARY KEY(user, appointment),
             FOREIGN KEY (user) REFERENCES USERS (id),
             FOREIGN KEY (appointment) REFERENCES APPOINTMENTS (id))
             ''')
                 
conn.commit()

#drop tables
# for i in ['USERS', 'LOCATIONS', 'APPOINTMENTS', 'USER_APPOINTMENTS']:
# 	c.execute('''DROP TABLE ''' + i)

#print('db created')
conn.close()