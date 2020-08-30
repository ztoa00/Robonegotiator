import os
import requests
import numpy as np
from bs4 import BeautifulSoup
import csv
from Database.dbscrapper import DBScrapperConnect
import re
import time
from random import randrange

MAX_PAGE = 100#333
base_url = "https://www.truecar.com/used-cars-for-sale/listings/location-"
def urls_scraping(base_url = 'https://www.truecar.com/used-cars-for-sale/listings/location-thousand-oaks-ca/', zip="91360"):
	
	for i in range(1, MAX_PAGE+1):
		pages = (base_url + '?page=' + str(i))
		rand = randrange(30, 120)
		time.sleep(rand)
		page_scraping(pages, zip)

def page_scraping(url, zip):
	db = DBScrapperConnect()
	response = '';
	try:
		response = requests.get(url)
		response.raise_for_status()
	except:
		return
#    root = lxl.fromstring(response.content)
	soup = BeautifulSoup(response.content, "html.parser")  
	cars = soup.find_all("div",{"data-qa":"Listings"})
	
	i = 0
	for dt in cars:
		try:
			url = dt.find("a",{'data-qa':'VehicleCard'}).get('href')
			listing_id = url.split('/')[3]
		except:
			url = ''

		try:
			str_str = dt.find("span",{'class':'vehicle-header-make-model text-truncate'}).text
		except:
			str_str = ''
		
		try:
			print(str_str)
			carinfo = str_str.split(' ');
		except:
			carinfo = ''
		
		try:
			year =  dt.find("span",{'class':'vehicle-card-year font-size-1'}).text
		except:
			year = ''
		
		try:
			make = carinfo[0]
		except:
			make = ''
			make = make.replace("'", "")
		
		try:
			model = carinfo[1]
			model = model.replace("'", "")
		except:
			model = ''
		
		try:
			trim = dt.find("div",{'data-test':'vehicleCardTrim'}).text
			trim = trim.replace("'", "")
		except:
			trim = ''
		
		try:
			miles = dt.find("div",{'data-test':'vehicleMileage'}).text.split(' ')[0]
			miles = miles.replace(",", "")
			if miles == '':
				miles = -1
		except:
			miles = -1
		
		try:
			color = dt.find("div",{'data-test':'vehicleCardColors'}).text.split(' ')[0]
		
		except:
			color = ""

		try:
			price = dt.find("h4",{'data-test':'vehicleCardPricingBlockPrice'}).text
			price = price.replace("$", "")
			price = price.replace(",", "")
		except:
			price = -1
		
		try:
			zipcode = zip
		except:
			zipcode = ''

		upc_product_code = make + '_' + model + '_' + color
		refTable = 'truecar'
		db.insertData(make, model, trim, year, miles, price, url, color, zipcode, upc_product_code, refTable, listing_id)


dbase = DBScrapperConnect()
url = dbase.getURLExtTrueCar()
for i in range(len(url)):
	url_now = base_url+url.iloc[i]['slug'] + '/'
	zipcode = str(url.iloc[i]['zip'])
	urls=urls_scraping(url_now, zipcode)
	print(url_now)
