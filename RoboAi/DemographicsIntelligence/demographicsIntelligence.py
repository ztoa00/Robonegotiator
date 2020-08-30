from flask import *
import os
import time
import ast
import json
import pandas as pd
from io import StringIO
import sys
import numpy as np
from Database.dbconnect import DBConnect
import os
import config
# path = yaml.load(open('config.yml'))
class DemographicsIntelligence():
	"""docstring for DemographicsIntelligence"""
	def __init__(self,UPC_Product_Code):
		try:
			self.UPC_Product_Codemake=UPC_Product_Code
			# self.csvToSql=path['csvToSql']
			self.csvToSql=config.configDict['csvToSql']
			if(self.csvToSql==1):
				self.DealObject=DBConnect()
			self.getDeals()
		except:
			self.deals=0	

	def getDeals(self):
		try:
			if(self.csvToSql==1):
				self.deals=self.DealObject.getDeals()
				
			else:
				# self.deals=pd.read_csv(str(path['dealPath']))
				self.deals=config.configDict['dealPath']
				# self.deals=pd.read_csv(str(os.path.dirname(os.path.abspath(""))+"/mapped_deal_customers.csv"))
			self.getProducts()
		except:
			print("Cannot open mapped_deal_customers.csv")
			self.deals=0
		
	def getProducts(self):
		try:
					
			if(self.csvToSql==1):
				self.Products = self.deals.groupby(['upc_product_code'])
				self.Buyer_Email = self.Products[['buyer_email']].get_group((self.UPC_Product_Codemake))
				
			else:
				self.Products = self.deals.groupby(['UPC_Product_Code'])
				self.Buyer_Email = self.Products[['Buyer_Email']].get_group((self.UPC_Product_Codemake))
			self.getProductBuyerDemographics()
		except:
			print("Invalid UPC_Product_Code")
			self.Products=0
			self.Buyer_Email=0	

	def getProductBuyerDemographics(self):
		try:
			self.Product_Buyer_Demographics = pd.DataFrame()
			if(self.csvToSql==1):
				self.Buyers = self.DealObject.getBuyers()
				self.Product_Buyer_Demographics = self.Buyers.loc[self.Buyers['email_id']\
		        	                          .isin(self.Buyer_Email['buyer_email'])  ]
			else:
				# self.Buyers = pd.read_csv(str(path['customerPath']))
				self.Buyers=config.configDict['customerPath']
				# self.Buyers=pd.read_csv(str(os.path.dirname(os.path.abspath(""))+"/testcutomerdata.csv"))
				self.Product_Buyer_Demographics = self.Buyers.loc[self.Buyers['Buyer_Email']\
		        	                          .isin(self.Buyer_Email['Buyer_Email'])  ]
			# print("#####################1$$$$$$$$$$$$$$$$$$$$$$$",self.Product_Buyer_Demographics['email_id'],self.Product_Buyer_Demographics['email_id'].dtypes)    	                              
			# print("#####################1$$$$$$$$$$$$$$$$$$$$$$$",self.Buyer_Email,self.Buyer_Email.dtypes)
			# print("###################################",self.Buyers)
			self.setParameters()#pass parameters here in future
		except:
			print("Cannot read testcutomerdata.csv or customer not present in database")
			self.Buyers=0
			self.Product_Buyer_Demographics=0

	'''Can pass parameter and set accordingly in future'''
	def setParameters(self):
		try:
			if(self.csvToSql==1):
				self.parameter1 = 'sex'
				self.parameter2 = 'race'
				self.parameter3 = 'age'
				self.parameter4 = 'annual_income'
			else:
				self.parameter1 = 'B_Sex'
				self.parameter2 = 'B_Race'
				self.parameter3 = 'B_Age'
				self.parameter4 = 'B_Ann_Income'

			self.distinct_parameter1 = self.Product_Buyer_Demographics[self.parameter1].unique()
			self.distinct_parameter2 = self.Product_Buyer_Demographics[self.parameter2].unique()
			self.distinct_parameter3 = self.Product_Buyer_Demographics[self.parameter3].unique()
			self.distinct_parameter4 = self.Product_Buyer_Demographics[self.parameter4].unique()
		
			self.max_param1 = 'none'
			self.max_param1_count = 0
			self.max_param2 = 'none'
			self.max_param2_count = 0
			self.max_param3 = 'none'
			self.max_param3_count = 0
			self.max_param4 = 'none'
			self.max_param4_count = 0
			self.demographics={}
			self.getHighestInParameter1()
		except:
			print("Error in setting parameters")
			self.demographics=0	

	def getHighestInParameter1(self):
		try:
			for parameter in self.distinct_parameter1:
				self.demographics[parameter] = int(self.Product_Buyer_Demographics[self.parameter1]\
					                          .loc[self.Product_Buyer_Demographics[self.parameter1]\
					                          ==parameter].count())
				if self.max_param1_count<self.Product_Buyer_Demographics[self.parameter1]\
				.loc[self.Product_Buyer_Demographics[self.parameter1]==parameter].count():
					self.max_param1_count = self.Product_Buyer_Demographics[self.parameter1]\
					                        .loc[self.Product_Buyer_Demographics[self.parameter1]\
					                        ==parameter].count()
					self.max_param1 = parameter
			self.getHighestInParameter2()
		except:
			self.demographics[parameter]=0
			self.max_param1_count=0
			self.max_param1=0
	       	
	def getHighestInParameter2(self):
		try:
			for parameter in self.distinct_parameter2:
				self.demographics[parameter] = int(self.Product_Buyer_Demographics[self.parameter2]\
					                          .loc[self.Product_Buyer_Demographics[self.parameter2]\
					                          ==parameter].count())
				if self.max_param2_count<self.Product_Buyer_Demographics[self.parameter2]\
				.loc[self.Product_Buyer_Demographics[self.parameter2]==parameter].count():
					self.max_param2_count = self.Product_Buyer_Demographics[self.parameter2]\
					                       .loc[self.Product_Buyer_Demographics[self.parameter2]\
					                       ==parameter].count()
					self.max_param2 = parameter
			self.getHighestInParameter3()
		except:
			self.demographics[parameter]=0
			self.max_param2_count =0
			self.max_param2=0	
	    
	def getHighestInParameter3(self):
		try:
			for parameter in self.distinct_parameter3:
				self.demographics[parameter] = int(self.Product_Buyer_Demographics[self.parameter3]\
					                          .loc[self.Product_Buyer_Demographics[self.parameter3]\
					                          ==parameter].count())
				if self.max_param3_count<self.Product_Buyer_Demographics[self.parameter3]\
				.loc[self.Product_Buyer_Demographics[self.parameter3]==parameter].count():
					self.max_param3_count = self.Product_Buyer_Demographics[self.parameter3]\
					                        .loc[self.Product_Buyer_Demographics[self.parameter3]\
					                        ==parameter].count()
					self.max_param3 = parameter
			self.getHighestInParameter4()
		except:
			self.demographics[parameter]=0
			self.max_param3_count =0
			self.max_param3=0	

	def getHighestInParameter4(self):
		try:
			for parameter in self.distinct_parameter4:
				self.demographics[parameter] = int(self.Product_Buyer_Demographics[self.parameter4]\
					                           .loc[self.Product_Buyer_Demographics[self.parameter4]\
					                           ==parameter].count())
				if self.max_param4_count<self.Product_Buyer_Demographics[self.parameter4]\
				.loc[self.Product_Buyer_Demographics[self.parameter4]==parameter].count():
					self.max_param4_count = self.Product_Buyer_Demographics[self.parameter4]\
					                        .loc[self.Product_Buyer_Demographics[self.parameter4]\
					                        ==parameter].count()
					self.max_param4 = parameter
		except:
			self.demographics[parameter]=0
			self.max_param4_count =0
			self.max_param4=0	
			

	        		        	
	       	

						
						
		