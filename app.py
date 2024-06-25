from flask import Flask, render_template
import pandas as pd

app = Flask(__name__)

@app.route('/')

def index():
    return render_template("index.html")

@app.route('/data')

def graphs():
    # source data
    df = pd.read_csv('data\swan_gfs_nz-ncanterb_v3.0_rb70bv50.csv')

    # Create a list of tuples containing time and swell size
    data = list(zip(df['time:Pacific/Auckland'], df['hs:m']))

    dates = [row[0] for row in data]
    values = [row[1] for row in data]
    labels = []

    for times in dates:
        #Add only time of day to labels
        labels.append(times[11:16])

    for i in range(12):
        labels.pop()

    #return html with data
    return render_template('data.html', labels=labels, values=values)


if __name__ == "__main__":
    app.run(debug=True)

