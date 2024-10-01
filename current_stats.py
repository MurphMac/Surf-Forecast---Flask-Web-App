from datetime import datetime
import pytz
import sqlite3
from collections import defaultdict

def get_current_stats(location_id):
    #Get current date and time (NZST) in correct format
    nzst = pytz.timezone('Pacific/Auckland')
    current_time = datetime.now(nzst)

    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    #Get all data values corresponding to a specific date/time
    cursor.execute("""
        SELECT t.date_time, wind.wind_direction, wind.wind_speed, wind.gust_speed, waves.swell_size, waves.swell_period, tide.tide_height
        FROM tide
        JOIN time t ON t.time_id = tide.time_id
        JOIN location l ON l.location_id = tide.location_id
        JOIN wind ON wind.time_id = tide.time_id AND wind.location_id = l.location_id
        JOIN waves ON waves.time_id = tide.time_id AND waves.location_id = l.location_id
        WHERE l.location_id = ?
    """, (location_id,))

    data = cursor.fetchall()
    data.remove(data[-1])
    conn.close()

    dates = []
    for value in data:
        dates.append(value[0])

    #Dictionary to hold grouped dates
    grouped_dates = defaultdict(list)

    #Group dates by year, month, and day
    for date in dates:
        date_obj = datetime.strptime(date, '%Y-%m-%dT%H:%M:%SZ')
        #Make localised to match up to current_date format
        date_obj = nzst.localize(date_obj)
        key = date_obj.strftime('%Y-%m-%d')  # Group by 'YYYY-MM-DD'
        grouped_dates[key].append(date_obj)
    
    #Convert defaultdict to regular dict for readability
    grouped_dates = dict(grouped_dates)

    #Get current year-month-day
    current_year_month_day = current_time.strftime('%Y-%m-%d')

    #If the data is up to date
    if current_year_month_day in grouped_dates:
        #Get a list of times under the current year-month-day
        times_under_day = []
        for value in grouped_dates[current_year_month_day]:
            times_under_day.append(value)

        #Get a list of the difference between these values and current_date hour
        differences_in_hours = []
        for value in times_under_day:
            differences_in_hours.append(abs((current_time - value).total_seconds() / 3600))

        #Find the smallest difference in hours between dates and current_date
        smallest = min(differences_in_hours)
        closest_index = differences_in_hours.index(smallest)
        
        #Get the closest date based on the index of the smallest difference
        closest_date = times_under_day[closest_index]
   
    #When data is out of date, use last date in data
    else:
        closest_date = datetime.strptime(data[-1][0], '%Y-%m-%dT%H:%M:%SZ')

    #Return the tuple from the database with the date corresponding to the closest_date
    return next((tup for tup in data if tup[0] == closest_date.strftime('%Y-%m-%dT%H:%M:%SZ')), None)