import pandas as pd
import config
import pymysql
from datetime import datetime

class DBScrapperConnect():
	"""docstring for DBConnect"""

	def __init__(self):
		self.myDB = pymysql.connect(host=config.configScrapperDict['host'], port=int(3306), user=config.configScrapperDict['user'], passwd=config.configScrapperDict['passwd'], db=config.configScrapperDict['database'],
		autocommit=True);

		self.cHandler = self.myDB.cursor()
    
	def insertData(self, make, model, trim, year, miles, price, url, color, zip_code, upc_product_code, refTable, listing_id):
		added = datetime.date(datetime.now())
		sql = '''
			insert into scrapeData (make, model, trim, year, miles, price, url, added, color, zip_code, upc_product_code,refTable,  listing_id)
            values ('{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}','{}','{}', '{}')
			'''.format(make, model, trim, year, miles, price, url, added, color, zip_code, upc_product_code, refTable, listing_id)

		try:
			self.cHandler.execute(sql)
		except Exception as e: 
			print(e)

	def insertZipTrueCar(self, zip, city,state ,county ,lon ,lat, timezone, slug):
		sql = '''
		insert into truecar ( zip, city,state ,county ,lon ,lat, timezone, slug)
            values ('{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}')
			'''.format(zip, city,state ,county ,lon ,lat, timezone, slug)
		
		try:
			self.cHandler.execute(sql)
		except Exception as e: 
			print(e)

	def getURLExtTrueCar(self):
		sql = '''
			SELECT slug, max(zip) as zip FROM truecar group by slug
			'''
		results = pd.read_sql_query(sql, self.myDB)

		return results

	def getValidZipCodes(self):
		sql = '''
			SELECT zip FROM truecar
			'''
		results = pd.read_sql_query(sql, self.myDB)

		return results

	def getMakeAndModel(self, upc_product_code):
		sql = '''
			SELECT make, model FROM scrapeData where upc_product_code = "{}"
			'''.format(upc_product_code)

		self.cHandler.execute(sql)

		results = self.cHandler.fetchone()

		return results[0], results[1]
