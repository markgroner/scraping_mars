from mission_to_mars import scrape
import pymongo
from flask import Flask, render_template, redirect, url_for
from string import Template
import codecs


app = Flask(__name__)
client = pymongo.MongoClient()
db = client.mars_db

'''
* `/scrape`

  * Return a python dictionary of live scraped Mars data and stores it in a
    Mongo database
'''
@app.route('/scrape')
def mars_scrape():
    mars_dict = scrape()
    db.scrapedData.insert_one(mars_dict)
    return redirect(url_for('mars_html'), 302)


'''
* `/`

  * Queries the Mongo database of Mars data and passes the data into an HTML
    template to display in a browser
'''
@app.route('/')
def mars_html():
    mars_data_from_mongo = list(db.scrapedData.find({}))
    if len(mars_data_from_mongo) == 0:
        mars_scrape()
        mars_data_from_mongo = list(db.scrapedData.find({}))
    mars_dict = mars_data_from_mongo[-1:][0]
    return render_template('index.html', **mars_dict)


if __name__ == "__main__":
    app.run(debug=True)
