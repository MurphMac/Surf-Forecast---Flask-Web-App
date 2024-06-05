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

    # sample data test
    data = [
        (1, 5),
        (2, 12),
        (3, 22),
        (4, 4),
        (5, 1),
        (6, 23),
        (7, 8),
        (8, 17),
    ]

    # get x and y values from sample data
    labels = [row[0] for row in data]
    values = [row[1] for row in data]
    
    #return html with data
    return render_template('data.html', labels=labels, values=values)


if __name__ == "__main__":
    app.run(debug=True)

