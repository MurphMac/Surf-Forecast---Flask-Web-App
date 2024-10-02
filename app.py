from flask import Flask, render_template, url_for, request
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

location_id = None
logged_in = False
account_name = ""
current_skill = ""
favourite_spot = "Tauranga"

insertdata.sourcedata()

def get_days():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('''SELECT date_time FROM time''')
    data = cursor.fetchall()
    dates = [row[0] for row in data]
    conn.close()

    days = []
    for date in dates:
        year, month, day = int(date[0:4]), int(date[5:7]), int(date[8:10])
        weekday = calendar.day_name[calendar.weekday(year, month, day)]
        weekday = str(weekday)[0:3]
        month_name = str(calendar.month_name[month])[0:3]
        days.append(f"{weekday} {day} {month_name}")
    days = list(dict.fromkeys(days))

    return days

def get_ratings():
    global current_skill
    global favourite_spot
    global location_id
    global location_name

    #Get variabe from drop down box
    location_name = request.form.get('location')

    locations_dictionary = {
        "Tauranga": 1,
        "Gisborne": 2,
        "Dunedin": 4,
        "Christchurch": 5
    }

    if location_name == None:
        location_name = favourite_spot

    #Get corresponding ID
    location_id = locations_dictionary.get(location_name)

    #Run rating function
    ratings = surfrating.get_rating(location_id, current_skill)

    return ratings

@app.context_processor

def inject_common_data():
    live_data = current_stats.get_current_stats(location_id)

    current_rating = surfrating.get_current_rating(location_id, live_data, current_skill)

    wind_direction = surfrating.wind_type(location_id, live_data)

    current_date = datetime.now().strftime("%A %d %B %Y")

    return dict(live_data=live_data, current_rating=current_rating, wind_direction=wind_direction, current_date=current_date)

@app.route('/', methods = ['GET', 'POST'])

def home():
    global logged_in
    global location_id
    global current_skill

    #Get days for each day displayed in graphs using function
    days = get_days()
    day1, day2, day3, day4, day5, day6, day7 = days[:7]

    ratings = get_ratings()


    return render_template("home.html", day1=day1, day2=day2, day3=day3, day4=day4, day5=day5, day6=day6, day7=day7, location_name=location_name, logged_in=logged_in, account_name=account_name, ratings=ratings, current_skill=current_skill)

@app.route('/login', methods = ['GET', 'POST'])

def login():
    global logged_in
    global account_name
    global current_skill
    global favourite_spot

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        cursor.execute(f"SELECT * FROM user WHERE username='{username}' AND password='{password}';")
        if not cursor.fetchone():
            return render_template('login.html')
        else:
            logged_in = True
            account_name = username
            #Fetch current user details including the skill level
            cursor.execute("SELECT skill FROM user WHERE username=?", (account_name,))
            current_skill = cursor.fetchone()[0]
            return render_template('account.html', account_name=account_name, logged_in=logged_in, current_skill=current_skill, favourite_spot=favourite_spot)

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
                return render_template('login.html')

    elif request.method == 'GET':
        return render_template('register.html', form=registrationForm)

@app.route('/account', methods=['GET', 'POST'])

def account():
    global logged_in
    global account_name
    global current_skill
    global favourite_spot

    if not logged_in:
        return render_template('login.html')

    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    # Fetch current user details including the skill level and favorite spot
    cursor.execute("SELECT skill, favourite_location FROM user WHERE username=?", (account_name,))
    result = cursor.fetchone()

    current_skill = result[0]
    favourite_spot = result[1]

    if request.method == 'POST':
        new_skill = request.form.get('skill', current_skill)  # Default to current skill if not changed
        new_favourite_spot = request.form.get('favourite_location', favourite_spot)  # Same for favourite spot

        cursor.execute("UPDATE user SET skill=?, favourite_location=? WHERE username=?", (new_skill, new_favourite_spot, account_name))
        conn.commit()

        current_skill = new_skill
        favourite_spot = new_favourite_spot

    conn.close()
    
    return render_template('account.html', account_name=account_name, logged_in=logged_in, current_skill=current_skill, favourite_spot=favourite_spot)

@app.route('/signout')

def signout():
    global favourite_spot
    favourite_spot = "Tauranga"
    #Sign out of account
    global logged_in
    logged_in = False

    #Get days for each day displayed in graphs using function
    days = get_days()
    day1, day2, day3, day4, day5, day6, day7 = days[:7]

    #Get ratings for each day
    ratings = get_ratings()

    return render_template('home.html', day1=day1, day2=day2, day3=day3, day4=day4, day5=day5, day6=day6, day7=day7, logged_in=logged_in, account_name=account_name, ratings=ratings, current_skill=current_skill, favourite_spot=favourite_spot)

@app.route('/delete')

def delete():
    global favourite_spot
    favourite_spot = "Tauranga"
    global logged_in
    global account_name

    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    cursor.execute('DELETE FROM user WHERE username=?', (account_name,))
    conn.commit()
    conn.close()

    logged_in = False
    account_name = ""

    #Get days for each day displayed in graphs using function
    days = get_days()
    day1, day2, day3, day4, day5, day6, day7 = days[:7]

    #Get ratings for each day
    ratings = get_ratings()

    return render_template('home.html', day1=day1, day2=day2, day3=day3, day4=day4, day5=day5, day6=day6, day7=day7, logged_in=logged_in, account_name=account_name, ratings=ratings, current_skill=current_skill, favourite_spot=favourite_spot)

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
    app.run()