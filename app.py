from flask import Flask, render_template
import pandas as pd

app = Flask(__name__)

@app.route('/')

def index():
    return render_template("index.html")

@app.route('/graph1')

def graphs1():
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
    return render_template('graph1.html', labels=labels, values1=values1, values2=values2)

@app.route('/graph2')

def graphs2():
    # source data
    df_wind = pd.read_csv('data\gfs025_sub_v1.0.csv')
    #Drop last 12 rows
    df_wind.drop(index=df_wind.index[-12:], axis=0, inplace=True)

    #Get Wind speed
    values1 = list(df_wind['wind_speed_at_10m_above_ground_level:kt'])

    #Get Gust speed
    values2 = list(df_wind['wind_speed_of_gust_at_10m_above_ground_level:kt'])
    
    labels = []
    dates = df_wind['time:Pacific/Auckland']
    for times in dates:
        labels.append(times[11:16])

    return render_template('graph2.html', labels=labels, values1=values1, values2=values2)


if __name__ == "__main__":
    app.run(debug=True)

