from flask import Flask, render_template, url_for, request
from flask_sqlalchemy import SQLAlchemy
import pandas as pd
from datetime import datetime, timedelta
import calendar
import sqlite3
import insertdata
from form import RegistrationForm

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SECRET_KEY'] = 'testkey'

db = SQLAlchemy(app)

location_id = None
logged_in = False
account_name = "Login"

insertdata.sourcedata()

@app.route('/', methods = ['GET', 'POST'])

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

    global location_id

    #Get variale from drop down box
    location_name = request.form.get('location')

    locations_dictionary = {
        "christchurch": 5,
        "tauranga": 1
    }

    #Get corresponding ID
    location_id = locations_dictionary.get(location_name)

    global logged_in
    global account_name

    return render_template("home.html", day1=day1, day2=day2, day3=day3, day4=day4, day5=day5, day6=day6, day7=day7, location_name=location_name, logged_in=logged_in, account_name=account_name)

@app.route('/login', methods = ['GET', 'POST'])

def login():
    global account_name
    global logged_in
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        cursor.execute(f"SELECT * FROM user WHERE username='{username}' AND password='{password}';")
        if not cursor.fetchone():
            return render_template('login.html')
        else:
            account_name = "Account - "+username
            logged_in = True
            return render_template('account.html', username=username)

    else:
        request.method == 'GET'
        return render_template('login.html')

@app.route('/register', methods = ['GET', 'POST'])

def register():
    #Run registration form from form.py
    registrationForm = RegistrationForm()
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    if request.method == 'POST':
        #If username and password is not null
        if (request.form['username'] != "" and request.form['password'] != ""):
            username = request.form['username']
            password = request.form['password']
            skill = request.form['skill']
            cursor.execute(f"SELECT * FROM user WHERE username='{username}' AND password='{password}';")
            data = cursor.fetchone()
            #Check if it matches other in db
            if data:
                return render_template("error.html")
            else:
                if not data:
                    #Insert into db
                    cursor.execute("INSERT INTO user (username, password, skill) VALUES (?,?,?)", (username, password, skill))
                    conn.commit()
                    conn.close()
                return render_template('login.html')

    elif request.method == 'GET':
        return render_template('register.html', form=registrationForm)

@app.route('/account')

def account():
    global account_name
    # Ensure logged_in is available
    global logged_in
    if not logged_in:
        return render_template('login.html')
    return render_template('account.html', account_name=account_name)

@app.route('/graph1')
def graphs1():

    #Access location_id
    global location_id
    
    # Open database
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    # Execute query and fetch all data
    cursor.execute('''
        SELECT w.wind_speed, w.gust_speed, w.wind_direction, t.date_time
        FROM wind w
        JOIN time t ON t.time_id = w.time_id
        JOIN location l ON w.location_id = l.location_id
        WHERE l.location_id = ?
    ''', (location_id,))

    data = cursor.fetchall()
    conn.close()

    # Extract values
    values1 = [row[0] for row in data]
    values2 = [row[1] for row in data]
    labels = [row[3][11:16] for row in data]

    return render_template('graph1.html', labels=labels, values1=values1, values2=values2)

@app.route('/graph2')

def graphs2():

    #Access location_id
    global location_id

    #Open database
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    #Execute query and fetch all data
    cursor.execute('''
        SELECT w.swell_size,swell_period,t.date_time 
        FROM waves w
        JOIN time t ON t.time_id = w.time_id
        JOIN location l ON w.location_id = l.location_id
        WHERE l.location_id = ?
    ''', (location_id,))

    data = cursor.fetchall()
    conn.close()

    #Extract values
    values1 = [row[0] for row in data]
    values2 = [row[1] for row in data]
    labels = [row[2][11:16] for row in data]

    #return html with data
    return render_template('graph2.html', labels=labels, values1=values1, values2=values2)

@app.route('/graph3')

def graphs3():

    #Access location_id
    global location_id

    #Open database
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    #Execute query and fetch all data
    cursor.execute('''
        SELECT tide.tide_height,t.date_time 
        FROM tide 
        JOIN time t ON t.time_id = tide.time_id
        JOIN location l ON tide.location_id = l.location_id
        WHERE l.location_id = ?
    ''', (location_id,))

    data = cursor.fetchall()
    conn.close()

    #Extract values
    values1 = [row[0] for row in data]
    labels = [row[1][11:16] for row in data]

    return render_template('graph3.html', labels=labels, values1=values1)

if __name__ == "__main__":
    app.run(debug=True)