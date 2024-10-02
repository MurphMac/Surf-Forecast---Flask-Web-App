from flask import Flask, render_template, url_for, request, session, redirect
from flask_sqlalchemy import SQLAlchemy
import calendar
import sqlite3
import insertdata
import surfrating
import current_stats
from form import RegistrationForm
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SECRET_KEY'] = 'testkey'

db = SQLAlchemy(app)

insertdata.sourcedata()

@app.context_processor

#Variables accessed by all routes
def inject_common_data():
    live_data = current_stats.get_current_stats(session.get('location_id'))

    current_rating = surfrating.get_current_rating(session.get('location_id'), live_data, session.get('current_skill', ""))

    wind_direction = surfrating.wind_type(session.get('location_id'), live_data)

    current_date = datetime.now().strftime("%A %d %B %Y")

    return dict(live_data=live_data, current_rating=current_rating, wind_direction=wind_direction, current_date=current_date)

@app.route('/', methods=['GET', 'POST'])

def home():
    #Access session to get user info
    logged_in = session.get('logged_in', False)
    account_name = session.get('account_name', "")
    
    # Set default values if keys don't exist
    current_skill = session.get('current_skill', "")
    favourite_spot = session.get('favourite_spot', 'Tauranga')

    # Get day titles for surf forecast
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('''SELECT date_time FROM time''')
    data = cursor.fetchall()
    dates = [row[0] for row in data]
    conn.close()

    #Get days for each day of data displayed
    days = []
    for date in dates:
        year, month, day = int(date[0:4]), int(date[5:7]), int(date[8:10])
        weekday = calendar.day_name[calendar.weekday(year, month, day)]
        weekday = str(weekday)[0:3]
        month_name = str(calendar.month_name[month])[0:3]
        days.append(f"{weekday} {day} {month_name}")
    days = list(dict.fromkeys(days))
    day1, day2, day3, day4, day5, day6, day7 = days[:7]

    #Option for user to change location
    location_name = request.form.get('location')
    #If they have selected
    if location_name:
        session['location_name'] = location_name
    else:
        #Set it to favourite spot
        location_name = session.get('location_name', favourite_spot)
        session['location_name'] = location_name

    locations_dictionary = {
        "Tauranga": 1,
        "Gisborne": 2,
        "Dunedin": 4,
        "Christchurch": 5
    }
    
    #Get ID corresponding to location
    location_id = locations_dictionary.get(location_name)
    session['location_id'] = location_id

    #Get the ratings from the rating function according to the location
    ratings = surfrating.get_rating(location_id, current_skill)

    location_name = session.get('location_name')
    
    return render_template("home.html", day1=day1, day2=day2, day3=day3, day4=day4, day5=day5, day6=day6, day7=day7, location_name=location_name, logged_in=logged_in, account_name=account_name, ratings=ratings, current_skill=current_skill, favourite_spot=favourite_spot)

@app.route('/login', methods=['GET', 'POST'])

def login():
    if request.method == 'POST':
        #Form for user information
        username = request.form['username']
        password = request.form['password']
        
        #Connect to db
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        #Get stored information corresponding to what they entered
        cursor.execute("SELECT * FROM user WHERE username=? AND password=?", (username, password))
        user = cursor.fetchone()
        
        #If it cannot be found
        if user is None:
            return render_template('login.html', error="Invalid credentials")
        
        #Set session variables
        session['logged_in'] = True
        session['account_name'] = username
        
        #Fetch current user details including the skill level
        cursor.execute("SELECT skill, favourite_location FROM user WHERE username=?", (username,))
        result = cursor.fetchone()
        session['current_skill'] = result[0]
        session['favourite_spot'] = result[1]
        conn.close()
        
        return redirect(url_for('account'))

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
            favourite_location = request.form['favourite_location']
            cursor.execute(f"SELECT * FROM user WHERE username='{username}' AND password='{password}';")
            data = cursor.fetchone()
            #Check if it matches other in db
            if data:
                return render_template("error.html")
            else:
                if not data:
                    #Insert into db
                    cursor.execute("INSERT INTO user (username, password, skill, favourite_location) VALUES (?,?,?,?)", (username, password, skill, favourite_location))
                    conn.commit()
                    conn.close()
                return redirect(url_for('login'))

    elif request.method == 'GET':
        return render_template('register.html', form=registrationForm)

@app.route('/account', methods=['GET', 'POST'])

def account():
    #They cannot access accound if they are not logged in
    if not session.get('logged_in'):
        return render_template('login.html')

    #Connect to db
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    # Fetch current user details
    cursor.execute("SELECT skill, favourite_location FROM user WHERE username=?", (session['account_name'],))
    result = cursor.fetchone()

    # Initialize
    session['current_skill'] = result[0]
    session['favourite_spot'] = result[1]

    if request.method == 'POST':
        form_type = request.form.get('form_type')

        #If they choose to update their skill, update the database
        if form_type == 'update_skill':
            new_skill = request.form.get('skill', session['current_skill'])
            cursor.execute("UPDATE user SET skill=? WHERE username=?", (new_skill, session['account_name']))
            session['current_skill'] = new_skill
        
        #If they choose to update their location, update the database
        elif form_type == 'update_location':
            new_favourite_spot = request.form.get('favourite_location', session['favourite_spot'])
            cursor.execute("UPDATE user SET favourite_location=? WHERE username=?", (new_favourite_spot, session['account_name']))
            session['favourite_spot'] = new_favourite_spot
            session['location_name'] = new_favourite_spot

        conn.commit()

    conn.close()

    return render_template('account.html', account_name=session['account_name'], logged_in=session['logged_in'], current_skill=session['current_skill'], favourite_spot=session['favourite_spot'])

@app.route('/signout')

def signout():
    #Clear the session data
    session.clear()

    return redirect(url_for('home'))

@app.route('/delete')

def delete():
    #Connect to database
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    #Remove the data corresponding to their username
    cursor.execute('DELETE FROM user WHERE username=?', (session['account_name'],))
    conn.commit()
    conn.close()

    #Clear the session data
    session.clear()

    return redirect(url_for('home'))

@app.route('/graph1')

def graphs1():
    #Access location_id
    location_id = session['location_id']
    
    #Open database
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    #Execute query and fetch all data
    cursor.execute('''
        SELECT w.wind_speed, w.gust_speed, w.wind_direction, t.date_time
        FROM wind w
        JOIN time t ON t.time_id = w.time_id
        JOIN location l ON w.location_id = l.location_id
        WHERE l.location_id = ?
    ''', (location_id,))

    data = cursor.fetchall()
    conn.close()

    #Extract values
    values1 = [row[0] for row in data]
    values2 = [row[1] for row in data]
    labels = [row[3][11:16] for row in data]

    return render_template('graph1.html', labels=labels, values1=values1, values2=values2)

@app.route('/graph2')

def graphs2():
    #Access location_id
    location_id = session['location_id']

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
    location_id = session['location_id']

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
    app.run()