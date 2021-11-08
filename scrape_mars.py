#Import dependencies
from bs4 import BeautifulSoup as bs
import requests
import pymongo
from splinter import Browser
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
from flask import Flask, render_template, redirect
from flask_pymongo import PyMongo

#Define function
def webdriver():
    executable_path = {'executable_path': 'chromedriver'}
    return Browser('chrome', **executable_path, headless=False)

def scrape():
    browser = webdriver()
    #Set up beautiful soup requests for Mars mission
    news_url = 'https://redplanetscience.com/'

    #Retrieve page with the requests module and create bs object
    browser.visit(news_url)
    news_html = browser.html
    soup = bs(news_html, 'html.parser')

    #Find the div.content_title for news title
    title_results = soup.find_all('div', class_='content_title')
    title = title_results[0].text

    #Scrape for image
    featured_scrape_url = 'https://spaceimages-mars.com/'

    #Retrieve page with the requests module and create bs object
    browser.visit(featured_scrape_url)
    news_html = browser.html
    soup = bs(news_html, 'html.parser')
    #Find div.article_teaser_body for paragraph
    article_results = soup.find_all('div', class_="article_teaser_body")
    news_article = article_results[0].text

    #Find img tag in html
    img = soup.find_all('img')

    #Select source for image jpg
    img_src = img[1]['src']

    #Construct featured_image_url
    featured_image_url = featured_scrape_url + img_src

    #Scrape table for mars facts
    facts_url='https://galaxyfacts-mars.com/'
    facts_table = pd.read_html(facts_url)

    #Select correct table
    facts_table_df = facts_table[0]
    facts_table_df = facts_table_df.rename(columns={0:"Description",1:"Mars",2:"Earth"})
    facts_table_df.set_index("Description", inplace=True)

    #Convert to hmtl table
    facts_html = facts_table_df.to_html()
    facts_html.replace('\n','')

    main_hempisphere_url = 'https://marshemispheres.com/'
    browser.visit(main_hempisphere_url)
    main_hemisphere_html = browser.html
    soup = bs(main_hemisphere_html, 'html.parser')

    #Get titles and png src of the hemisphere images
    image_section = soup.find('div',class_="collapsible results")
    image_information = image_section.find_all('div', class_="item")
    hemisphere_dict = []
   


    #Get titles and png src of the hemisphere images
    
    for image in image_information:
        try:
            image_title = image.find('h3')
            title = str.strip(image_title.text)
            #titles.append(title)
            href = image.a['href']
            full_url = main_hempisphere_url + href
            #print(full_url)
            browser.visit(full_url)
            html = browser.html
            soup = bs(html,'html.parser')
            image_source = soup.find('img', class_="wide-image")['src']
            image_url = main_hempisphere_url + image_source
            print(image_url)
            #image_url_list.append(image_url)
            hemisphere_dict.append({"title": title, "url": image_url})

        except Exception as e:
            print(e)

    #Final dictionary
    final_dict = {"title": title,
    "article": news_article,
    "featured_image": featured_image_url,
    "data_table" : facts_html,
    "hemispheres" : hemisphere_dict}

    browser.quit()
    return final_dict

#Import into mongodb
def mongodb():
    conn = 'mongodb://localhost:27017'
    client = pymongo.MongoClient(conn)
    db = client.mars_db
    db.mars_data.drop()
    db.mars_data.insert_one(final_dict)
