import sqlite3
import build
import pandas as pd
import csv
from functions import make_shifts, populate_tables, confirm_populate, check_user_appt, show_scheduled_appts, show_available_appts, cancel_appointment
from datetime import datetime, timedelta, date, time

conn = sqlite3.connect('appt_tracker.db')  
conn.execute('''PRAGMA foreign_keys = 1''')
conn.row_factory = sqlite3.Row
cur = conn.cursor()

df = pd.read_sql_query("SELECT * FROM USERS", conn)
if df.empty:
     make_shifts(4)
     populate_tables()
else:
     confirm_populate()

#make available_appts.csv
show_available_appts()

#claim appointment; receive these values from session; hard-coded for demo
id_person = 2
id_appt = 165

validate_user_appt = check_user_appt(id_person,id_appt)

#120 is maximum number of users per each block; 2 here for demo
#2 is the maximum number of appointments per user per week
if validate_user_appt[0] == 2:
     print('The appointment block has reached maximum capacity. Please choose another block in a different week.')
elif validate_user_appt[1] == 2: 
     print('You have reached your maximum number of appointments for that week. Please choose another week.')
elif( (validate_user_appt[0] < 2 ) and (validate_user_appt[1] < 2) ):
     cur.execute("INSERT INTO USER_APPOINTMENTS (user, appointment) VALUES (?,?)", (id_person, id_appt) )
     conn.commit() 
else: 
     print('Please contact an administrator for help.')

#show inserted data
df = pd.read_sql_query("SELECT * FROM USER_APPOINTMENTS", conn)
print(df)

#make users_appointments.csv
show_scheduled_appts()

#cancel an appointment; receive these values from session; hard-coded for demo
id_patient = 2
id_claimed = 165
answer = 'No'

cur.execute('''
     SELECT u.fname ||' '|| u.lname as Name, l.name as Location, a.date, a.time
     FROM USER_APPOINTMENTS ua INNER JOIN USERS u ON ua.user=u.id
     INNER JOIN APPOINTMENTS a ON ua.appointment = a.id
     INNER JOIN LOCATIONS l ON a.location = l.id
     WHERE ua.user = (?) and ua.appointment = (?)''', (id_patient, id_claimed,) )
results = cur.fetchone()
print('Cancel this appointment? Appointment details: ' + results['Name'] + ' at ' + results['Location'] + ' on ' + results['date'] + ' at ' + results['time'])
if answer == 'Yes':
     cancel_appointment(id_patient, id_claimed)
else:
     print('Your appointment is not cancelled. Appointment details: ' + results['Name'] + ' at ' + results['Location'] + ' on ' + results['date'] + ' at ' + results['time'])

#make users_appointments.csv after any cancellations
show_scheduled_appts()

conn.close()