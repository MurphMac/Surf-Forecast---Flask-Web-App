from flask import Flask, render_template, url_for
import pandas as pd
import matplotlib.pyplot as plt
import io
import base64

app = Flask(__name__)

@app.route('/')

def index():
    return render_template("index.html")

@app.route('/data')

def data():
    df = pd.read_csv('data\swan_gfs_nz-ncanterb_v3.0_rb70bv50.csv')

    #return df.to_html()

    #set up image
    img = io.BytesIO()
    #plot data
    df.plot()
    plt.savefig(img, format='png')
    plt.close()
    img.seek(0)
    plot_url = base64.b64encode(img.getvalue()).decode('utf8')
    return render_template("data.html", plot_url=plot_url)


if __name__ == "__main__":
    app.run(debug=True)

