import pandas as pd
from datetime import datetime, timedelta
import sqlite3

def sourcedata():
    # source tide data
    df_tide = pd.read_csv(r'data\results.csv', header=7)
    # Create a list of tuples containing time and tide height
    tide_data = list(zip(df_tide['TIME'], df_tide['VALUE']))

    # source wind data
    df_wind = pd.read_csv(r'data\gfs025_sub_v1.0.csv')
    #Drop last 12 rows
    df_wind.drop(index=df_wind.index[-12:], axis=0, inplace=True)

    dates = [row[0] for row in tide_data]

    # Convert dates into correct format and order
    for i in range(len(dates)):
        #Convert to datetime object
        dt = datetime.strptime(dates[i], "%Y-%m-%dT%H:%M:%SZ")
        #Subtract 12 hours
        dt -= timedelta(hours=12)
        #Convert back to string
        dates[i] = dt.strftime("%Y-%m-%dT%H:%M:%SZ")

    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    # Clear table
    cursor.execute("DELETE FROM time")
    cursor.execute("DELETE FROM wind")
    cursor.execute("DELETE FROM waves")
    cursor.execute("DELETE FROM tide")

    for date in dates:
        cursor.execute("INSERT INTO time (date_time) VALUES (?)", (date,))

    #Get Wind speed
    wind_speed = list(round(x, 2) for x in df_wind['wind_speed_at_10m_above_ground_level:kt'])
    #Get Gust speed
    gust_speed = list(round(x, 2) for x in df_wind['wind_speed_of_gust_at_10m_above_ground_level:kt'])
    #Get Wind direction
    wind_direction = list(df_wind['wind_from_direction_at_10m_above_ground_level:deg'])

    values = list(zip(wind_speed, gust_speed, wind_direction))

    #Insert into wind table
    time_id = 1
    for value in values:
        cursor.execute("INSERT INTO wind (location_id, wind_speed, gust_speed, wind_direction, time_id) VALUES (?, ?, ?, ?, ?)", (5, value[0], value[1], value[2], time_id))
        time_id = time_id+3

    conn.commit()
    conn.close()