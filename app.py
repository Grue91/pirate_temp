#!/usr/bin/env python3
import subprocess
from flask import Flask, render_template, jsonify
import sqlite3

app = Flask(__name__)

@app.route('/')
def hello():
    return render_template('index.html')

@app.route("/query/", defaults={'days': 1 }, methods=['GET'])
@app.route("/query/<days>")
def get_data(days):
    conn = sqlite3.connect('temperature.db')
    c = conn.cursor()
    statement = f"SELECT * FROM temperature WHERE time >= Datetime('now', '-{days} days', 'localtime');"
    execute = c.execute(statement)
    conn.commit()
    query = c.fetchall()
    conn.close()
    return jsonify(query)

if __name__ == '__main__':
    #initiate the data-collection from the SDR - dongle
    collector = subprocess.Popen(["python3", "pirateTemp.py"])
    #Run the flask app
    app.run(debug=True, host='0.0.0.0')