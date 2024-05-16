from flask import Flask, render_template, url_for
import pandas as pd

app = Flask(__name__)

@app.route('/')

def index():
    return render_template("index.html")

@app.route('/test')
def hello():
    df = pd.read_csv('C:\\Users\\cuteb\\Downloads\\mov-line-graph-data (4).zip\\swan_gfs_nz-ncanterb_v3.0_rb70bv50.csv')
    return df.to_html()

if __name__ == "__main__":
    app.run(debug=True)

