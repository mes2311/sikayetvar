# -*- coding: utf-8 -*-
"""
Created on Fri Jul 13 12:01:30 2018

@author: Mehmet Sonmez
"""

import csv
import requests
from requests.exceptions import RequestException
from contextlib import closing
from bs4 import BeautifulSoup

def simple_get(url):
    """
    Attempts to get the content at `url` by making an HTTP GET request.
    If the content-type of response is some kind of HTML/XML, return the
    text content, otherwise return None.
    """
    try:
        with closing(requests.get(url, stream=True)) as resp:
            if is_good_response(resp):
                return resp.content
            else:
                return None

    except RequestException as e:
        log_error('Error during requests to {0} : {1}'.format(url, str(e)))
        return None

def is_good_response(resp):
    """
    Returns True if the response seems to be HTML, False otherwise.
    """
    content_type = resp.headers['Content-Type'].lower()
    return (resp.status_code == 200 
            and content_type is not None 
            and content_type.find('html') > -1)


def log_error(e):
    """
    It is always a good idea to log errors. 
    This function just prints them, but you can
    make it do anything.
    """
    print(e)
    
BASE_URL = "http://www.sikayetvar.com"
brand_names = ["brand1","brand2","brand3","brand4"] #The brand names are to be filled in


#List to store all the fetched rows
scraped_data = []

for brand in brand_names:
    BRAND_URL = BASE_URL + "/" + brand
    
    raw_html = simple_get(BRAND_URL)
    soup = BeautifulSoup(raw_html, 'html.parser')
    
    item_pages = []
    for complaint in soup.find_all("a", {"class":"complaint-link-for-ads"}):
        item_pages.append(complaint["href"])

    for page in item_pages:
        my_url = BASE_URL + page
        print("Visiting " + my_url + "...")
        raw_html = simple_get(my_url)
        soup = BeautifulSoup(raw_html, 'html.parser') 
    
        title = soup.find("h1",{"class":"title"}).text.strip('\n')
        description = soup.find("div", {"class":"description"}).text.strip('\n')
        date = soup.find("span",{"class":"date date-tips"})["title"][:-5]
        views = soup.find("span",{"class":"view-count-detail"}).b.text
        hashtags = soup.find_all("a",{"class":"btn btn-bordered green"})
        tags = []
        for tag in hashtags:
            tags.append(tag["title"])
    
        row = [brand,title,description,date,views,tags]
        scraped_data.append(row)
 
    raw_html = simple_get(BRAND_URL)
    soup = BeautifulSoup(raw_html, 'html.parser')
    next_ref = soup.find("a",{"class":"pg-next"})
    if next_ref != None:
        next_page = BRAND_URL + next_ref["href"]
    else:
        next_page = None
    
    #LOOP THROUGH AlL THE NEXT PAGES
    page_num = 1
    while next_page != None:
        page_num += 1
        log = "\n Scraping through page " + str(page_num) + " for " + brand + "\n"
        print(log)
        
        raw_html = simple_get(next_page)
        soup = BeautifulSoup(raw_html, 'html.parser')
    
        item_pages = []
        for complaint in soup.find_all("a", {"class":"complaint-link-for-ads"}):
            item_pages.append(complaint["href"])

        
        for page in item_pages:
            my_url = BASE_URL + page
            print("Visiting " + my_url + "...")
            raw_html = simple_get(my_url)
            soup = BeautifulSoup(raw_html, 'html.parser') 
    
            title = soup.find("h1",{"class":"title"})
            if title != None:
                title = title.text.strip('\n')
                
            description = soup.find("div", {"class":"description"})
            if description != None:
                description = description.text.strip('\n')
                
            date = soup.find("span",{"class":"date date-tips"})
            if date != None:
                date = date["title"][:-5]
                
            views = soup.find("span",{"class":"view-count-detail"})
            if views != None:
                views = views.b.text
            
            hashtags = soup.find_all("a",{"class":"btn btn-bordered green"})
            tags = []
            for tag in hashtags:
                tags.append(tag["title"])
    
            row = [brand,title,description,date,views,tags]
            scraped_data.append(row)
 
        raw_html = simple_get(next_page)
        soup = BeautifulSoup(raw_html, 'html.parser')
        next_ref = soup.find("a",{"class":"pg-next"})
        if next_ref != None:
            next_page = BRAND_URL + next_ref["href"]
        else:
            next_page = None
        
with open("sikayetimVar.csv", "w", encoding="utf8", newline = "") as csvfile:
    print("Writing file!")
    writer = csv.writer(csvfile, delimiter=';', quotechar='"')
    
    headers = ["Brand","Title","Description","Date","# of Views","Tags"]
    writer.writerow(headers)           
                   
    for row in scraped_data:
        writer.writerow(row)
          
    print("Done!")
