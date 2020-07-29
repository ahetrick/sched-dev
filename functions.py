import sqlite3
import pandas as pd
import csv
import numpy as np
from datetime import datetime, timedelta, date, time

conn = sqlite3.connect('appt_tracker.db')  
conn.execute('''PRAGMA foreign_keys = 1''')
conn.row_factory = sqlite3.Row
cur = conn.cursor()

def daterange(start_date, end_date):
    weekdays = []
    delta = timedelta(days=1)
    d = start_date
    diff = 0
    weekend = set([5, 6])
    while d <= end_date:
        if d.weekday() not in weekend:
            weekdays.append(d)
            diff += 1
        d += delta
    for i in weekdays:
        yield i

def make_shifts(num_locations):
    shifts = []
    hours = [i for i in np.arange(8, 18.5, .5)]
    change_hours = [str(int(i)) + ':00' if float.is_integer(i) else str(int(i)) + ':30' for i in hours]
    make_time = [datetime.strptime(i, '%H:%M').time() for i in change_hours]
    for i in range(1, num_locations):
        start_date = date(2020, 8, 1)
        end_date = date(2020, 9, 1)
        for single_date in daterange(start_date, end_date):
            for single_time in make_time:
                shifts.append((single_date, single_time, single_date.isocalendar()[1], i))
    with open('shifts.csv', 'w', newline='') as f:
        writer = csv.writer(f, delimiter=',')
        writer.writerow(['date', 'time', 'week', 'location'])
        writer.writerows(shifts)

def populate_tables():
    for i in zip(['users','locations','shifts'],['USERS','LOCATIONS','APPOINTMENTS']):
        df = pd.read_csv (r'./{}.csv'.format(i[0]))
        df.to_sql(i[1], conn, if_exists='append', index = False)
        conn.commit() 
    return "DB population complete"

def confirm_populate():
    for i in ['USERS','LOCATIONS','APPOINTMENTS']:
        df = pd.read_sql_query("SELECT * FROM " + i, conn)
        if df.empty:
            print("DB population failed on {} table.".format(i))
        else:
            print("DB population succeeded on {} table.".format(i))

def check_user_appt(person_id, shift_id):
     today = datetime.today()
     #check user and appt ids valid
     cur.execute("SELECT id FROM USERS WHERE id = (?)", (person_id,) )
     user_id = cur.fetchone()
     if not user_id:
          return(print("User not found. Please register to use this app."))
     cur.execute("SELECT * FROM APPOINTMENTS WHERE id = (?)", (shift_id,) )
     appt = cur.fetchone()
     if not appt or datetime.strptime(appt['date'], '%Y-%m-%d').date() < today.date():
          return(print("Appointment not found or exists in the past. Please contact administrator."))
    #count how many times appointment slot has already been claimed
     cur.execute('''
        SELECT COUNT(appointment) as count_appt
        FROM USER_APPOINTMENTS
        WHERE appointment = (?)''', (appt['id'],) )
     count_appt = cur.fetchone()
     #count how many appointments per week per user
     cur.execute('''
        SELECT COUNT(a.week) as count_week
        FROM USER_APPOINTMENTS ua 
        INNER JOIN APPOINTMENTS a 
        ON ua.appointment = a.id
        WHERE ua.user = (?) and a.week = (?)
        GROUP BY ua.user''', (user_id['id'], appt['week'],) )
     count_user_week = cur.fetchone()
     if not count_user_week:
         count_user_week = 0
         return (count_appt['count_appt'], count_user_week)
     else:
         return (count_appt['count_appt'], count_user_week['count_week'])

def show_available_appts():
    cur.execute('''
    SELECT a.id, a.date, a.time, l.name AS location
    FROM APPOINTMENTS a INNER JOIN LOCATIONS l
    ON a.location = l.id
    WHERE (DATE(a.date) >= DATE("now") and TIME(a.time) >= TIME("now","localtime") ) and a.id NOT IN (
    SELECT appointment
    FROM USER_APPOINTMENTS
    GROUP BY
        appointment
    HAVING COUNT(appointment) >= 120)
    ''')
    results = cur.fetchall()
    available = [(row['id'], row['date'], row['time'], row['location']) for row in results]
    with open('available_appts.csv', 'w', newline='') as f:
        writer = csv.writer(f, delimiter=',')
        writer.writerow(['id', 'date', 'time', 'location'])
        writer.writerows(available)

def show_scheduled_appts():
    cur.execute('''SELECT u.fname ||' '|| u.lname as Name, u.phone, l.name as Location, a.date, a.time
    FROM USERS u 
    INNER JOIN USER_APPOINTMENTS ua ON u.id=ua.user 
    INNER JOIN APPOINTMENTS a ON ua.appointment = a.id
    INNER JOIN LOCATIONS l ON a.location = l.id ''')
    results = cur.fetchall()
    claimed = [(row['Name'], row['phone'], row['Location'], row['date'], row['time']) for row in results]
    with open('scheduled_appts.csv', 'w', newline='') as f:
        writer = csv.writer(f, delimiter=',')
        writer.writerow(['name', 'phone', 'location', 'date', 'time'])
        writer.writerows(claimed)

def cancel_appointment(person_id, shift_id):
     cur.execute('''
     DELETE FROM USER_APPOINTMENTS WHERE user = (?)
     and appointment = (?)''', (person_id, shift_id,) )
     conn.commit()
     print('Your appointment has been cancelled.')


