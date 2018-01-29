import pandas as pd
import time
from bs4 import BeautifulSoup
from splinter import Browser
from datetime import datetime
import os


'''
Initiates chrome browser used to scrape pages.
'''
def init_browser():
    ##chrome_path = os.path.join(os.getcwd(), 'chromedriver.exe')
    ##executable_path = {'executable_path': chrome_path}
    ##browser = Browser('chrome', **executable_path, headless=True)
    browser = Browser('chrome', headless=True)
    return browser

'''
This function uses Splinter chromedriver to visit webpages and return either
the raw html as a string or a BeautifulSoup object.
'''
def scrape_html_soup(browser, seed_url, soup=True, click_css=''):
    # Visit the seed url
    browser.visit(seed_url)
    time.sleep(1)
    if click_css != '':
        browser.find_by_css(click_css).first.click()
        time.sleep(1)
    html = browser.html
    if soup: ## Scrape page into soup
        return BeautifulSoup(html, 'html.parser')
    else:
        return html


'''
This function scrapes the latest article title and summary paragraph from
'https://mars.nasa.gov/news/'
It returns the title and summary paragraph as strings in a python dictionary.
'''
def scrape_mars_news(browser):
    seed_url = 'https://mars.nasa.gov/news/'
    soup = scrape_html_soup(browser, seed_url)
    article_title = soup.find('div', class_='content_title').text
    article_paragraph = soup.find('div', class_='article_teaser_body').text
    return {'articleTitle': article_title, 'articleParagraph': article_paragraph}


'''
This function scrapes the featured image from
'https://www.jpl.nasa.gov/spaceimages/?search=&category=Mars/'
It returns the url of the image in a python dictionary.
'''
def scrape_featured_mars_image(browser):
    seed_url = 'https://www.jpl.nasa.gov/spaceimages/?search=&category=Mars/'
    soup = scrape_html_soup(browser, seed_url, click_css='div.carousel_container div.carousel_items a.button')
    landing_page_url = seed_url[:seed_url.find('/',8)]
    featured_image_url = soup.find('img', class_='fancybox-image')['src']
    featured_image_url = f'{landing_page_url}{featured_image_url}'
    featured_image_url = featured_image_url.replace('medium', 'large').replace('ip', 'hires')
    return {'featuredImageUrl': featured_image_url}


'''
This function scrapes the most recent mars weather tweet from
'https://twitter.com/marswxreport?lang=en'
It returns the text of the tweet as a string in a python dictionary.
'''
def scrape_mars_weather_tweet(browser):
    seed_url = 'https://twitter.com/marswxreport?lang=en'
    soup = scrape_html_soup(browser, seed_url)
    mars_weather_tweet = soup.find('div', attrs={'class': 'tweet', 'data-name': 'Mars Weather'})\
        .find('p', attrs={'class': 'tweet-text'}).text
    return {'marsWeatherTweet': mars_weather_tweet}


'''
This function scrapes the mars facts table from 'http://space-facts.com/mars/'
It returns the table as an html string in a python dictionary.
'''
def scrape_mars_facts_html(browser):
    seed_url = 'http://space-facts.com/mars/'
    html = scrape_html_soup(browser, seed_url, soup=False)
    mars_facts_df = pd.read_html(html, attrs = {'id': 'tablepress-mars'})[0]
    mars_facts_df.columns = ['Measurement', 'Value']
    mars_facts_df['Measurement'] = [measurement[:-1] for measurement in mars_facts_df['Measurement']]
    mars_facts_html = mars_facts_df.to_html(index=False)
    mars_facts_html = mars_facts_html.replace('\n','')\
        .replace('class="dataframe"', 'class="table table-bordered table-hover"')
    return {'marsFactsHtml': mars_facts_html}


'''
Gets time of last scrape and put it in a dictionary
'''
def get_time():
    date_time_string = datetime.now().strftime('%Y-%m-%d %I:%M %p')
    return {'dateTimeString': date_time_string}


'''
This function concatenates the dictionaries from these four functions:
    1. scrape_mars_news
    2. scrape_featured_mars_image
    3. scrape_mars_weather_tweet
    4. scrape_mars_facts_html
    5. get_time
The return dictionary has 5 elements with the following keys:
    1. articleTitle
    2. articleParagraph
    3. featuredImageUrl
    4. marsWeatherTweet
    5. marsFactsHtml
    6. dateTimeString
'''
def scrape():
    browser = init_browser()
    scraped_data_dict = scrape_mars_news(browser)
    scraped_data_dict.update(scrape_featured_mars_image(browser))
    scraped_data_dict.update(scrape_mars_weather_tweet(browser))
    scraped_data_dict.update(scrape_mars_facts_html(browser))
    browser.quit()
    scraped_data_dict.update(get_time())
    return scraped_data_dict
