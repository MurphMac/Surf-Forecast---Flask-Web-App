import pandas as pd
from datetime import datetime, timedelta
import sqlite3

#Process tide data
def process_tide_data(cursor, file_path, location_id):
    df_tide = pd.read_csv(file_path, header=7)
    df_tide = df_tide.iloc[:169]
    
    #Create a list of tuples containing time and tide height
    tide_data = list(zip(df_tide['TIME'], df_tide['VALUE']))

    #Convert dates into correct format and order
    dates = [datetime.strptime(row[0], "%Y-%m-%dT%H:%M:%SZ") - timedelta(hours=12) for row in tide_data]
    formatted_dates = [dt.strftime("%Y-%m-%dT%H:%M:%SZ") for dt in dates]

    tide_height = [round(x, 2) for x in df_tide['VALUE']]

    #Insert date and time
    for date in formatted_dates:
        cursor.execute("INSERT INTO time (date_time) VALUES (?)", (date,))

    #Insert tide data
    time_id = 1
    for value in tide_height:
        cursor.execute("INSERT INTO tide (location_id, tide_height, time_id) VALUES (?, ?, ?)", (location_id, value, time_id))
        time_id += 1

#Process wind data
def process_wind_data(cursor, file_path, location_id):
    df_wind = pd.read_csv(file_path)
    #Make it 57 rows of data (7 days)
    df_wind = df_wind.iloc[:57]

    wind_speed = [round(x, 2) for x in df_wind['wind_speed_at_10m_above_ground_level:kt']]
    gust_speed = [round(x, 2) for x in df_wind['wind_speed_of_gust_at_10m_above_ground_level:kt']]
    wind_direction = list(df_wind['wind_from_direction_at_10m_above_ground_level:deg'])

    wind_values = list(zip(wind_speed, gust_speed, wind_direction))

    #Insert wind data
    time_id = 1
    for value in wind_values:
        cursor.execute("INSERT INTO wind (location_id, wind_speed, gust_speed, wind_direction, time_id) VALUES (?, ?, ?, ?, ?)", (location_id, value[0], value[1], value[2], time_id))
        time_id += 3

#Process swell data
def process_swell_data(cursor, file_path, location_id):
    df_swell = pd.read_csv(file_path)
    df_swell = df_swell.iloc[:169]

    swell_size = [round(x, 2) for x in df_swell['hs:m']]
    swell_period = list(df_swell['tp:s'])

    swell_values = list(zip(swell_size, swell_period))

    #Insert swell data
    time_id = 1
    for value in swell_values:
        cursor.execute("INSERT INTO waves (location_id, swell_size, swell_period, time_id) VALUES (?, ?, ?, ?)", (location_id, value[0], value[1], time_id))
        time_id += 1

#Main function to call all processing functions
def sourcedata():
    #Connection to the database
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    #Clear tables
    cursor.execute("DELETE FROM time")
    cursor.execute("DELETE FROM wind")
    cursor.execute("DELETE FROM waves")
    cursor.execute("DELETE FROM tide")
    conn.commit()

    #Process all data
    process_tide_data(cursor, r'data/TAU_results.csv', location_id=1)
    process_wind_data(cursor, r'data/TAU_gfs025_sub_v1.0.csv', location_id=1)
    process_swell_data(cursor, r'data/TAU_swan_gfs_nz-bop_v3.0_rcm61szc.csv', location_id=1)

    process_tide_data(cursor, r'data/GIS_results.csv', location_id=2)
    process_wind_data(cursor, r'data/GIS_gfs025_sub_v1.0.csv', location_id=2)
    process_swell_data(cursor, r'data/GIS_swan_gfs_nz-pbay_v3.0_rcneem8r.csv', location_id=2)

    process_tide_data(cursor, r'data/DUN_results.csv', location_id=4)
    process_wind_data(cursor, r'data/DUN_gfs025_sub_v1.0.csv', location_id=4)
    process_swell_data(cursor, r'data/DUN_swan_gfs_nz-dnd_v3.0_pzc7zrrh.csv', location_id=4)

    process_tide_data(cursor, r'data/CHR_results.csv', location_id=5)
    process_wind_data(cursor, r'data/CHR_gfs025_sub_v1.0.csv', location_id=5)
    process_swell_data(cursor, r'data/CHR_swan_gfs_nz-ncanterb_v3.0_rb70bv50.csv', location_id=5)

    cursor.execute("""DELETE FROM time
        WHERE time_id NOT IN (
            SELECT time_id FROM time
            ORDER BY time_id ASC
            LIMIT 169
        )
    """)

    conn.commit()
    conn.close()
