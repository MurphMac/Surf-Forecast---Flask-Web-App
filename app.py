from flask import Flask, render_template, url_for
from flask_sqlalchemy import SQLAlchemy
#from flask_login import UserMixin
import pandas as pd
from datetime import datetime, timedelta
import calendar
import sqlite3
import insertdata

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SECRET_KEY'] = 'testkey'

db = SQLAlchemy(app)

insertdata.sourcedata()

@app.route('/')

def home():
    #Open database
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    #Get dates and times
    cursor.execute('''SELECT date_time FROM time''')
    data = cursor.fetchall()
    #Make into list
    dates = [row[0] for row in data]
    conn.close()

    # Variables for weekdays
    days = []
    for date in dates:
        #Grab year, month, day of each row
        year, month, day = int(date[0:4]), int(date[5:7]), int(date[8:10])
        #Add weekday value to list
        weekday = calendar.day_name[calendar.weekday(year, month, day)]
        weekday = str(weekday)[0:3]
        #Get name of month
        month_name = str(calendar.month_name[month])[0:3]
        days.append(f"{weekday} {day} {month_name}")
        #Remove duplicates
        days = list(dict.fromkeys(days))


    #Assign value to each day on the graph
    day1=(days[0])
    day2=(days[1])
    day3=(days[2])
    day4=(days[3])
    day5=(days[4])
    day6=(days[5])
    day7=(days[6])

    return render_template("home.html", day1=day1, day2=day2, day3=day3, day4=day4, day5=day5, day6=day6, day7=day7)

@app.route('/login')

def login():
    return render_template('login.html')

@app.route('/register')

def register():
    return render_template('register.html')

@app.route('/graph1')

def graphs1():
    #Open database
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    #Execute query and fetch all data
    cursor.execute('''
        SELECT w.wind_speed, w.gust_speed, w.wind_direction, t.date_time
        FROM wind w
        JOIN time t ON t.time_id = w.time_id
        JOIN location l ON w.location_id = l.location_id
        WHERE l.location_id = 5
    ''')

    data = cursor.fetchall()
    conn.close()

    # Extract values
    values1 = [row[0] for row in data]
    values2 = [row[1] for row in data]
    labels = [row[3][11:16] for row in data]

    return render_template('graph1.html', labels=labels, values1=values1, values2=values2)

"""

@app.route('/graph2')

def graphs2():
    # source data
    df_swell = pd.read_csv(r'data\swan_gfs_nz-ncanterb_v3.0_rb70bv50.csv')
    #Drop last 12 rows
    df_swell.drop(index=df_swell.index[-12:], axis=0, inplace=True)

    # Create a list of tuples containing time and swell size
    swell_data = list(zip(df_swell['time:Pacific/Auckland'], df_swell['hs:m']))
    # List of wave period data
    values2 = list(df_swell['tp:s'])

    dates = [row[0] for row in swell_data]
    values1 = [row[1] for row in swell_data]
    labels = []

    for times in dates:
        #Add only time of day to labels
        labels.append(times[11:16])

    #return html with data
    return render_template('graph2.html', labels=labels, values1=values1, values2=values2)

@app.route('/graph3')

def graphs3():
    values1 = [row[1] for row in tide_data]
    labels = []

    for times in dates:
        #Add only time of day to labels
        labels.append(times[11:16])

    return render_template('graph3.html', labels=labels, values1=values1)

"""

if __name__ == "__main__":
    app.run(debug=True)

