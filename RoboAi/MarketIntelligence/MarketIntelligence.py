import pandas as pd
import config
import pymysql
from datetime import datetime
from Database.dbscrapper import DBScrapperConnect

class MarketIntelligence():
	def __init__(self,UPC_Product_Code, zip_code):
		self.marketDB = DBScrapperConnect()
		self.myMarketDB = self.marketDB.myDB
		self.UPC_Product_Code = UPC_Product_Code
		self.zip_code = zip_code

	def getAverageDuration(self):
		sql = '''
   		select upc_product_code, avg(duration) as duration
		from (SELECT max(upc_product_code) as upc_product_code, max(added)-min(added) as duration
		from scrapeData
		where zip_code = {} and upc_product_code = "{}"
		group by listing_id)t
		group by upc_product_code
		'''.format(self.zip_code, self.UPC_Product_Code )
		

		results = pd.read_sql_query(sql, self.myMarketDB)


		return results
	def getAveragePrice(self):
		#Nested SQL Query to avoid influencing the average price because a listing has been posted for a long time.
		sql = '''
		SELECT upc_product_code,avg(price) as ave_price, round(avg(year)) as ave_year
		from (select max(make) as make, max(model) as model, max(trim) as trim, max(year) as year, max(miles) as miles, max(price) as price, url, max(added) as added, max(color) as color, max(upc_product_code) as upc_product_code, max(zip_code) as zip_code, max(refTable) as refTable
		from scrapeData
		where price >0 and zip_code = {} and upc_product_code = "{}"
		group by url) t
		group by upc_product_code
		'''.format(self.zip_code, self.UPC_Product_Code )


		results = pd.read_sql_query(sql, self.myMarketDB)


		return results

		
	def getAverageDepreciation(self):
		sql='''
		select upc_product_code, added, avg(price)
		from scrapeData
		where zip_code = {} and upc_product_code= "{}"
		group by upc_product_code, added
		'''.format(self.zip_code, self.UPC_Product_Code)

		market = pd.read_sql_query(sql, self.myMarketDB)

		maxDate = max(market['added'])
		minDate = min(market['added'])
		maxDatePrice = market[market['added']==maxDate].mean()
		minDatePrice = market[market['added']==minDate].mean()
		dateDiff = 1

		if ((maxDate-minDate).days==0):
			dateDiff = 1
		else:
			dateDiff = (maxDate - minDate).days

		depreciation = (minDatePrice-maxDatePrice) / dateDiff

		return depreciation['avg(price)']
	
	def getMarketStatistic(self):
		response = {};
		response['success']  = 'true'

		try:
			response['listing_Age'] = float(self.getAverageDuration()['duration'][0])
		except:
			response['listing_Age'] = 0

		try:
			response['ave_price'] = float(self.getAveragePrice()['ave_price'][0])
		except:
			response['ave_price'] = 0
		
		try:
			response['ave_year'] = int(self.getAveragePrice()['ave_year'][0])
		except:
			response['ave_year'] = 0
		
		try:
			response['ave_Market_Change'] = float(self.getAverageDepreciation())
		except:
			response['ave_Market_Change'] = 0

		return response