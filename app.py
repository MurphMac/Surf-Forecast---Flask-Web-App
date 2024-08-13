from flask import Flask, render_template
import pandas as pd
import calendar

app = Flask(__name__)

# source data
df_wind = pd.read_csv('data\gfs025_sub_v1.0.csv')
#Drop last 12 rows
df_wind.drop(index=df_wind.index[-12:], axis=0, inplace=True)
#Get dates
dates = df_wind['time:Pacific/Auckland']

@app.route('/')

def index():
    # Variables for weekdays
    days = []
    for date in dates:
        #Grab year, month, day of each row
        year, month, day = int(date[0:4]), int(date[5:7]), int(date[8:10])
        #Add weekday value to list
        weekday = calendar.day_name[calendar.weekday(year, month, day)]
        days.append(weekday)
        #Remove duplicates
        days = list(dict.fromkeys(days))

    #Assign value to each day on the graph
    day1=(days[0])[0:3]
    day2=(days[1])[0:3]
    day3=(days[2])[0:3]
    day4=(days[3])[0:3]
    day5=(days[4])[0:3]
    day6=(days[5])[0:3]
    day7=(days[6])[0:3]

    return render_template("index.html", day1=day1, day2=day2, day3=day3, day4=day4, day5=day5, day6=day6, day7=day7)

@app.route('/graph1')

def graphs1():
    #Get Wind speed
    values1 = list(round(x, 2) for x in df_wind['wind_speed_at_10m_above_ground_level:kt'])

    #Get Gust speed
    values2 = list(round(x, 2) for x in df_wind['wind_speed_of_gust_at_10m_above_ground_level:kt'])
    
    #Get Labels
    labels = []
    #dates = df_wind['time:Pacific/Auckland']
    for times in dates:
        labels.append(times[11:16])

    return render_template('graph1.html', labels=labels, values1=values1, values2=values2)

@app.route('/graph2')

def graphs2():
    # source data
    df_swell = pd.read_csv('data\swan_gfs_nz-ncanterb_v3.0_rb70bv50.csv')
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

if __name__ == "__main__":
    app.run(debug=True)

