import os
import csv
from pymongo import MongoClient
from flask import Flask
import urllib.parse

#creates the app
app = Flask(__name__)

#intializes the account for the data base
username = urllib.parse.quote_plus('edward.bottom')
password = urllib.parse.quote_plus('Duckunder195!')

#configues the account
app.config['MONGO_DBNAME'] = 'whiskey_flask'
app.config['MONGO_URI'] = 'mongodb://%s:%s@ds117878.mlab.com:17878/whiskey_flask?authSource=admin'%(username,password)

COLLECTION_NAME = 'whiskeys'

#http://intelligentonlinetools.com/blog/2016/07/30/automating-csv-file-reading-and-writing-with-python/
connection = MongoClient(app.config['MONGO_URI'])
db = connection.app.config['MONGO_DBNAME'][COLLECTION_NAME]
#route to fill the database with values from the csv
@app.route('/fill')
def add():
    with open("whiskey.csv", encoding="utf8" ) as f:
        csv_f = csv.reader(f)
        for i, row in enumerate(csv_f):
            if i > 0 and len(row) > 1 :
                db.insert({'Name': row[0], 'Rating': row[1], 'Country': row[2], 'Category' : row[3], 'Price' : row[4], 'ABV' : row[5], 'Age' : row[6], 'Brand' : row[7]})
                print(row[0] + " was added to the database")

#run main
if __name__ == '__main__':
	app.run(debug=True)