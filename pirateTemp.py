
#!/usr/bin/env python3
import subprocess
import json
import sqlite3

class DBmanager(object):

    def __init__(self, db_location):
        self.connection = sqlite3.connect(db_location)
        self.cur = self.connection.cursor()
        self.create_table()

    def close(self):
        """close sqlite3 connection"""
        self.connection.close()

    def execute(self, statement, new_data):
        self.cur.execute(statement, new_data)

    def insertmany(self, data):
        self.cur.executemany('INSERT into temperature VALUES(?, ?, ?, ?, ?)', data)

    def create_table(self):
        """create a database table if it does not exist already"""
        self.cur.execute('''CREATE TABLE IF NOT EXISTS temperature (
                        time text,
                        temperature integer,
                        humidity integer,
                        model text,
                        id integer);''')
        self.commit()

    def query_days(self, days):
        #query last X * 24 H of data from db
        days = 1
        statement = f"SELECT * FROM temperature WHERE time >= Datetime('now', '-{days} days', 'localtime');"
        execute = self.cur.execute(statement)
        query = self.cur.fetchall()
        return query

    def parse_temperature(self, json_data):
        #This could theoretically bulk insert rows
        sqlite_row = [(json_data["time"], json_data["temperature_C"], json_data["humidity"], json_data["model"], json_data["id"])]
        self.insertmany(sqlite_row)
        self.commit()

    def commit(self):
        self.connection.commit()

def execute(cmd):
    popen = subprocess.Popen(cmd, stdout=subprocess.PIPE, bufsize=1, universal_newlines=True)
    for stdout_line in iter(popen.stdout.readline, ""):
        yield stdout_line 
    popen.stdout.close()
    return_code = popen.wait()
    if return_code:
        raise subprocess.CalledProcessError(return_code, cmd)

db = DBmanager("temperature.db")

for output in execute(["rtl_433", "-F", "json", "-R", "19"]):
    print(output, end="")
    try:
        json_object = json.loads(output)
        db.parse_temperature(json_object)
        print(db.query_days(1))
    except ValueError as e:
        print ("Received an object that was not valid json")