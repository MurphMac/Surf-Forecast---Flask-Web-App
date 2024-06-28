from flask import Flask, render_template
import pandas as pd

app = Flask(__name__)

@app.route('/')

def index():
    return render_template("index.html")

@app.route('/data')

def graphs():
    # source data
    df_swell = pd.read_csv('data\swan_gfs_nz-ncanterb_v3.0_rb70bv50.csv')
    # df_wind = pd.read_csv('data\gfs025_sub_v1.0.csv')

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

    for i in range(12):
        labels.pop()

    #return html with data
    return render_template('data.html', labels=labels, values1=values1, values2=values2)

if __name__ == "__main__":
    app.run(debug=True)

