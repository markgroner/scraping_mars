from mission_to_mars import scrape
import pymongo
from flask import Flask, redirect, url_for
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
    html_template = codecs.open('index.html', 'r').read()
    mars_data_from_mongo = list(db.scrapedData.find({}))
    if len(mars_data_from_mongo) == 0:
        mars_scrape()
        mars_data_from_mongo = list(db.scrapedData.find({}))
    mars_dict = mars_data_from_mongo[-1:][0]
    article_title = mars_dict['articleTitle']
    article_paragraph = mars_dict['articleParagraph']
    featured_image_url = mars_dict['featuredImageUrl']
    mars_weather_tweet = mars_dict['marsWeatherTweet']
    mars_facts_html = mars_dict['marsFactsHtml']
    date_time_string = mars_dict['dateTimeString']
    html = Template(html_template).safe_substitute(articleTitle=article_title)
    html = Template(html).safe_substitute(articleParagraph=article_paragraph)
    html = Template(html).safe_substitute(featuredImageUrl=featured_image_url)
    html = Template(html).safe_substitute(marsWeatherTweet=mars_weather_tweet)
    html = Template(html).safe_substitute(marsFactsHtml=mars_facts_html)
    html = Template(html).safe_substitute(dateTimeString=date_time_string)
    return html


if __name__ == "__main__":
    app.run()
