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
'''Function to map demographics to scalar values and vise versa'''

def Race_to_Category(df):
	segt_map = {
	r'White': 1,
	r'Asian': 2,
	r'Native Hawaiian and Other Pacific Islander': 3,
	r'Black or African American':4,
	r'Native American and Alaska Native':5,
	r'Latino/Mexican':6,
	}
	df['B_Race']=df['B_Race'].replace(segt_map,regex=True)
	return df

def Race_to_Category_sql(df):
	segt_map = {
	r'WHITE': 1,
	r'ASIAN': 2,
	r'NATIVE HAWAIIAN AND OTHER PACIFIC ISLANDER': 3,
	r'BLACK/AFRICAN AMERICAN':4,
	r'NATIVE AMERICAN AND ALASKA NATIVE':5,
	r'LATINO/MEXICAN':6,
	}
	df['race']=df['race'].replace(segt_map,regex=True)
	return df

def Income_to_Category(df):
	segt_map = {
	r'less than 20000': 1,
	r'20000-44999': 2,
	r'45000-139999': 3,
	r'140000-149999':4,
	r'150000-199999':5,
	r'200000+':6,
	   
	}
	df['B_Ann_Income']=df['B_Ann_Income'].replace(segt_map,regex=True)
	return df

def Income_to_Category_sql(df):
	segt_map = {
	r'less than 20000': 1,
	r'20000-44999': 2,
	r'45000-139999': 3,
	r'140000-149999':4,
	r'150000-199999':5,
	r'200000+':6,
	   
	}
	df['annual_income']=df['annual_income'].replace(segt_map,regex=True)
	return df

def Gender_to_Category(df):
	segt_map = {
	r'Female': 1,
	r'Male': 2,
	
	
	}
	df['B_Sex']=df['B_Sex'].replace(segt_map,regex=True)
	return df

def Gender_to_Category_sql(df):
	segt_map = {
	
	r'FEMALE':1,
	r'MALE':2
	
	}
	df['sex']=df['sex'].replace(segt_map,regex=True)
	return df	

def Age_to_Category(df):
	segt_map = {
	r'0-17': 1,
	r'18-34': 2,
	r'35-49': 3,
	r'50-70':4,
	r'71-100':5,
	
	}
	df['B_Age']=df['B_Age'].replace(segt_map,regex=True)
	return df

def Age_to_Category_sql(df):
	segt_map = {
	r'0-17': 1,
	r'18-34': 2,
	r'35-49': 3,
	r'50-70':4,
	r'71-100':5,
	
	}
	df['age']=df['age'].replace(segt_map,regex=True)
	return df

def Category_to_Gender(param):
	if param==1:
		return "Female"
	if param==2:
		return "Male"
def Category_to_Race(param):
	if param==1:
		return "White"
	if param==2:
		return "Asian"
	if param==3:
		return 'Native Hawaiian and Other Pacific Islander' 
	if param==4:
		return 'Black or African American'
	if param==5:
		return 'Native American and Alaska Native'
	if param==6:
		return 'Latino/Mexican'   
def Category_to_Income(param):
	if param==1:
		return 'less than 20000',
	if param==2:
		return '20000-44999'
	if param==3:
		return '45000-139999'
	if param==4:
		return '140000-149999'
	if param==5:
		return '150000-199999'
	if param==6:
		return '200000+'    
def Category_to_Age(param):
	if param==1:
		return '0-17'
	if param==2:
		return '18-34'
	if param==3:
		return '35-49'
	if param==4:
		return '50-70'
	if param==5:
		return '71-100'

def ageRange(min,max):
	str1=Category_to_Age(min)
	str2=Category_to_Age(max)
	bottom=str1.split("-")[0]
	top=str2.split("-")[1]
	return bottom,top

def incomeRange(min,max):
	if min==1 and max==1:
		bottom='0'
		top='19999'
	if min==1:
		bottom='0'
	if min==6 and max==6:
		bottom='200000'
		top='200000+'
	if max==6:
		top='200000+'
	if min not in[1,6]:
		str1=Category_to_Income(min)
		bottom=str1.split("-")[0]
	if max not in[1,6]:    
		str2=Category_to_Income(max)        
		top=str2.split("-")[1]
	return bottom,top              

class MostCommonDemographics():
	"""docstring for MostCommonDemographics"""
	def __init__(self,UPC_Product_Code):
		try:
			self.UPC_Product_Code = UPC_Product_Code
			# self.csvToSql=path['csvToSql']
			self.csvToSql=config.configDict['csvToSql']
			if(self.csvToSql==1):
				self.DealObject=DBConnect()
			self.getDeals()
		except:
			print("Enter valid UPC_Product_Code")
			self.deals=0				

	def getDeals(self):
		try:
			if(self.csvToSql==1):
				self.deals=self.DealObject.getDeals()
				self.deals.drop(self.deals[self.deals.seller_listed_price <= 0].index, inplace=True)
				self.deals.drop(self.deals[self.deals.buyer_highest_offer <= 0].index, inplace=True)

			else:
				# self.deals=pd.read_csv(str(path['dealPath']))
				self.deals=config.configDict['dealPath']
				# self.deals=pd.read_csv(str(os.path.dirname(os.path.abspath(""))+"/mapped_deal_customers.csv"))
				self.deals.drop(self.deals[self.deals.S_Listed_Price <= 0].index, inplace=True)
				self.deals.drop(self.deals[self.deals.B_Highest_Offer <= 0].index, inplace=True)
			self.getProducts()
		except:
			print("Cannot open mapped_deal_customers.csv")
			self.deals=0


	def getProducts(self):
		try:
			if(self.csvToSql==1):
				self.Products = self.deals.groupby(['upc_product_code'])
				self.Buyer_Email = self.Products[['buyer_email']].get_group((self.UPC_Product_Code))
				
			else:
				self.Products = self.deals.groupby(['UPC_Product_Code'])
				self.Buyer_Email = self.Products[['Buyer_Email']].get_group((self.UPC_Product_Code))
			
			self.getProductBuyerDemographics()
		except:
			print("Invalid UPC_Product_Code")
			self.Products=0			

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
				print(str(os.path.dirname(os.path.abspath(""))+"/testcutomerdata.csv"))
				self.Product_Buyer_Demographics = self.Buyers.loc[self.Buyers['Buyer_Email']\
		        	                          .isin(self.Buyer_Email['Buyer_Email'])  ]
			#print("*********************************************************",self.Product_Buyer_Demographics['annual_income'])
			self.applyModel()
		except:
			print("Cannot open testcustomer.csv")
			self.Product_Buyer_Demographics=0
			self.Buyers=0		

	def applyModel(self):
		try:
			
			
			if(self.csvToSql==1):
				
				self.Product_Buyer_Demographics = Race_to_Category_sql(self.Product_Buyer_Demographics)
				
				self.Product_Buyer_Demographics = Income_to_Category_sql(self.Product_Buyer_Demographics)
				
				self.Product_Buyer_Demographics = Gender_to_Category_sql(self.Product_Buyer_Demographics)
				
				self.Product_Buyer_Demographics = Age_to_Category_sql(self.Product_Buyer_Demographics)
				
				
				self.Product_Buyer_Demographics = self.Product_Buyer_Demographics.reset_index(drop=True)
				self.Product_Buyer_Demographics[['annual_income','age','race']]=self.Product_Buyer_Demographics[['annual_income','age','race']].astype(int)

				'''Top 2 parameters are one with lowest standard devoation
				Since B_Sex can have only two values it is hard coded to be parameter1
				Second parameter is choosed on basis of standard deviation of remaining parameters'''
				#self.df=self.Product_Buyer_Demographics[['annual_income','age','race']]
				#self.df[['age','race']]=self.df[['age','race']].astype(int)
				# print("***************************************************",self.df.dtypes)
				#print("********************************************************dfdfdf",self.df.columns)
				# self.stattable = self.df.describe()
				self.stattable = self.Product_Buyer_Demographics[['annual_income','age','race']].describe()
				#print("********************************************************",self.stattable)
				self.parameter1 = 'sex'
				self.parameter1_value = round(self.Product_Buyer_Demographics['sex'].describe().iloc[1])
				 
				self.sortedstd = self.stattable.sort_values(by='std',axis=1)
				# print(self.sortedstd)
				# print("1",self.sortedstd.iloc[2].keys()[0])
				# print("2",self.sortedstd.iloc[2].keys()[1])
				# print("3",self.sortedstd.iloc[2].keys()[2])
				# print("std of B_Race",self.sortedstd.iloc[2][0])
				if(self.sortedstd.iloc[2].keys()[0]=='race'): #'''B_Race has least standard deviation  '''
					if(self.sortedstd.iloc[2][0]<1.0): #'''Parameter 2 is B_Race with standard deviation less than 1'''
						self.parameter2 = self.sortedstd.iloc[2].keys()[0]
						self.parameter2_value=round(self.sortedstd[self.parameter2].iloc[1])
						self.top_2_param_percentage_distribution=self.Product_Buyer_Demographics\
													[(self.Product_Buyer_Demographics[self.parameter1]\
														==self.parameter1_value) \
													& ((self.Product_Buyer_Demographics[self.parameter2] \
														== self.parameter2_value))]\
													.count()['id']/self.Product_Buyer_Demographics\
													.shape[0]*100\

						self.parameter3=self.sortedstd.iloc[2].keys()[1]
						self.parameter4=self.sortedstd.iloc[2].keys()[2]
						self.temp_df=self.Product_Buyer_Demographics\
								[(self.Product_Buyer_Demographics[self.parameter1]\
								==self.parameter1_value) \
								& ((self.Product_Buyer_Demographics[self.parameter2] \
								== self.parameter2_value))]			

						self.parameter3_min=self.temp_df[self.parameter3].min()
						self.parameter3_max=self.temp_df[self.parameter3].max()

						self.parameter4_min=self.temp_df[self.parameter4].min()
						self.parameter4_max=self.temp_df[self.parameter4].max()	

						if self.parameter2=='race':
							self.parameter2_value=Category_to_Race(round(self.sortedstd[self.parameter2].iloc[1]))

						if self.parameter3=='age':
							bottom,top=ageRange(self.parameter3_min,self.parameter3_max)
							self.parameter3_value=bottom+" - "+top 
						if self.parameter4=='age':
							bottom,top=ageRange(self.parameter4_min,self.parameter4_max)
							self.parameter4_value=bottom+" - "+top 	

						if self.parameter3=='annual_income':
							bottom,top=incomeRange(self.parameter3_min,self.parameter3_max)
							self.parameter3_value=bottom+" - "+top 
						if self.parameter4=='annual_income':
							bottom,top=incomeRange(self.parameter4_min,self.parameter4_max)
							self.parameter4_value=bottom+" - "+top	


					else: #'''Parameter 2 is not B_Race as standard deviation is greater than 1'''
						self.parameter2=self.sortedstd.iloc[2].keys()[1]
						self.parameter3=self.sortedstd.iloc[2].keys()[2]
						self.parameter2_min = self.sortedstd[self.parameter2].iloc[3]
						self.parameter2_max = self.sortedstd[self.parameter2].iloc[7]
						self.top_2_param_percentage_distribution=self.Product_Buyer_Demographics\
													[(self.Product_Buyer_Demographics[self.parameter1]\
														==self.parameter1_value) \
													& ((self.Product_Buyer_Demographics[self.parameter2] \
														<= self.parameter2_max)\
													&(self.Product_Buyer_Demographics[self.parameter2] \
														>=self.parameter2_min))]\
													.count()['id']/self.Product_Buyer_Demographics\
													.shape[0]*100\

						self.temp_df = self.Product_Buyer_Demographics[(self.Product_Buyer_Demographics[self.parameter1]\
															==self.parameter1_value) \
															& ((self.Product_Buyer_Demographics[self.parameter2] \
															<= self.parameter2_max)\
															&(self.Product_Buyer_Demographics[self.parameter2] \
															>=self.parameter2_min))]
						self.parameter3_min=self.temp_df[self.parameter3].min()
						self.parameter3_max=self.temp_df[self.parameter3].max()	

						if self.parameter2=='age':
							bottom,top=ageRange(self.parameter2_min,self.parameter2_max)
							self.parameter2_value=bottom+" - "+top
						if self.parameter3=='age':
							bottom,top=ageRange(self.parameter3_min,self.parameter3_max)
							self.parameter3_value=bottom+" - "+top
						if self.parameter2=='annual_income':
							bottom,top=incomeRange(self.parameter2_min,self.parameter2_max)
							self.parameter2_value=bottom+" - "+top
						if self.parameter3=='annual_income':
							bottom,top=incomeRange(self.parameter3_min,self.parameter3_max)
							self.parameter3_value=bottom+" - "+top	 



				else: #'''B_Race dont have least standard deviation'''
					self.parameter2 = self.sortedstd.iloc[2].keys()[0]
					self.parameter2_max = self.sortedstd[self.parameter2].iloc[7]
					self.parameter2_min = self.sortedstd[self.parameter2].iloc[3]
					if(self.sortedstd.iloc[2].keys()[1]=='race'): #'''B_Race  have second least standard deviation'''
						self.parameter3=self.sortedstd.iloc[2].keys()[2]
					else:
						self.parameter3=self.sortedstd.iloc[2].keys()[1]
					self.top_2_param_percentage_distribution=self.Product_Buyer_Demographics\
													[(self.Product_Buyer_Demographics[self.parameter1]\
														==self.parameter1_value) \
													& ((self.Product_Buyer_Demographics[self.parameter2] \
														<= self.parameter2_max)\
													&(self.Product_Buyer_Demographics[self.parameter2] \
														>=self.parameter2_min))]\
													.count()['id']/self.Product_Buyer_Demographics\
													.shape[0]*100\

					self.temp_df=self.Product_Buyer_Demographics\
															[(self.Product_Buyer_Demographics[self.parameter1]\
															==self.parameter1_value) \
															& ((self.Product_Buyer_Demographics[self.parameter2] \
															<= self.parameter2_max)\
															&(self.Product_Buyer_Demographics[self.parameter2] \
															>=self.parameter2_min))]
					# print("parameter2",self.parameter2,"min",self.parameter2_min,"max",self.parameter2_max)
					# print("TEmporary df",self.temp_df)											
					self.parameter3_min=self.temp_df[self.parameter3].min()
					self.parameter3_max=self.temp_df[self.parameter3].max()																	
						
					if self.parameter2=='age':
						bottom,top=ageRange(self.parameter2_min,self.parameter2_max)
						self.parameter2_value=bottom+" - "+top
					if self.parameter3=='age':
						print("top",self.parameter3_max,"bottom",self.parameter3_min)
						bottom,top=ageRange(self.parameter3_min,self.parameter3_max)
						self.parameter3_value=bottom+" - "+top 

					if self.parameter2=='annual_income':
						bottom,top=incomeRange(self.parameter2_min,self.parameter2_max)
						self.parameter2_value=bottom+" - "+top
					if self.parameter3=='annual_income':
						bottom,top=incomeRange(self.parameter3_min,self.parameter3_max)
						self.parameter3_value=bottom+" - "+top
				













			else:
				self.Product_Buyer_Demographics = Race_to_Category(self.Product_Buyer_Demographics)
				self.Product_Buyer_Demographics = Income_to_Category(self.Product_Buyer_Demographics)
				self.Product_Buyer_Demographics = Gender_to_Category(self.Product_Buyer_Demographics)
				self.Product_Buyer_Demographics = Age_to_Category(self.Product_Buyer_Demographics)

			
				self.Product_Buyer_Demographics = self.Product_Buyer_Demographics.reset_index(drop=True)
				'''Top 2 parameters are one with lowest standard devoation
				Since B_Sex can have only two values it is hard coded to be parameter1
				Second parameter is choosed on basis of standard deviation of remaining parameters'''
				print("#####################################",self.Product_Buyer_Demographics[['B_Ann_Income','B_Age','B_Race']].columns)
				self.stattable = self.Product_Buyer_Demographics[['B_Ann_Income','B_Age','B_Race']].describe()
				self.parameter1 = 'B_Sex'
				self.parameter1_value = round(self.Product_Buyer_Demographics['B_Sex'].describe().iloc[1])
				 
				self.sortedstd = self.stattable.sort_values(by='std',axis=1)
				print(self.sortedstd)
				print("1",self.sortedstd.iloc[2].keys()[0])
				print("2",self.sortedstd.iloc[2].keys()[1])
				print("3",self.sortedstd.iloc[2].keys()[2])
				print("std of B_Race",self.sortedstd.iloc[2][0])
				if(self.sortedstd.iloc[2].keys()[0]=='B_Race'): #'''B_Race has least standard deviation  '''
					if(self.sortedstd.iloc[2][0]<1.0): #'''Parameter 2 is B_Race with standard deviation less than 1'''
						self.parameter2 = self.sortedstd.iloc[2].keys()[0]
						self.parameter2_value=round(self.sortedstd[self.parameter2].iloc[1])
						self.top_2_param_percentage_distribution=self.Product_Buyer_Demographics\
													[(self.Product_Buyer_Demographics[self.parameter1]\
														==self.parameter1_value) \
													& ((self.Product_Buyer_Demographics[self.parameter2] \
														== self.parameter2_value))]\
													.count()['ID']/self.Product_Buyer_Demographics\
													.shape[0]*100\

						self.parameter3=self.sortedstd.iloc[2].keys()[1]
						self.parameter4=self.sortedstd.iloc[2].keys()[2]
						self.temp_df=self.Product_Buyer_Demographics\
								[(self.Product_Buyer_Demographics[self.parameter1]\
								==self.parameter1_value) \
								& ((self.Product_Buyer_Demographics[self.parameter2] \
								== self.parameter2_value))]			

						self.parameter3_min=self.temp_df[self.parameter3].min()
						self.parameter3_max=self.temp_df[self.parameter3].max()

						self.parameter4_min=self.temp_df[self.parameter4].min()
						self.parameter4_max=self.temp_df[self.parameter4].max()	

						if self.parameter2=='B_Race':
							self.parameter2_value=Category_to_Race(round(self.sortedstd[self.parameter2].iloc[1]))

						if self.parameter3=='B_Age':
							bottom,top=ageRange(self.parameter3_min,self.parameter3_max)
							self.parameter3_value=bottom+" - "+top 
						if self.parameter4=='B_Age':
							bottom,top=ageRange(self.parameter4_min,self.parameter4_max)
							self.parameter4_value=bottom+" - "+top 	

						if self.parameter3=='B_Ann_Income':
							bottom,top=incomeRange(self.parameter3_min,self.parameter3_max)
							self.parameter3_value=bottom+" - "+top 
						if self.parameter4=='B_Ann_Income':
							bottom,top=incomeRange(self.parameter4_min,self.parameter4_max)
							self.parameter4_value=bottom+" - "+top	


					else: #'''Parameter 2 is not B_Race as standard deviation is greater than 1'''
						self.parameter2=self.sortedstd.iloc[2].keys()[1]
						self.parameter3=self.sortedstd.iloc[2].keys()[2]
						self.parameter2_min = self.sortedstd[self.parameter2].iloc[3]
						self.parameter2_max = self.sortedstd[self.parameter2].iloc[7]
						self.top_2_param_percentage_distribution=self.Product_Buyer_Demographics\
													[(self.Product_Buyer_Demographics[self.parameter1]\
														==self.parameter1_value) \
													& ((self.Product_Buyer_Demographics[self.parameter2] \
														<= self.parameter2_max)\
													&(self.Product_Buyer_Demographics[self.parameter2] \
														>=self.parameter2_min))]\
													.count()['ID']/self.Product_Buyer_Demographics\
													.shape[0]*100\

						self.temp_df = self.Product_Buyer_Demographics[(self.Product_Buyer_Demographics[self.parameter1]\
															==self.parameter1_value) \
															& ((self.Product_Buyer_Demographics[self.parameter2] \
															<= self.parameter2_max)\
															&(self.Product_Buyer_Demographics[self.parameter2] \
															>=self.parameter2_min))]
						self.parameter3_min=self.temp_df[self.parameter3].min()
						self.parameter3_max=self.temp_df[self.parameter3].max()	

						if self.parameter2=='B_Age':
							bottom,top=ageRange(self.parameter2_min,self.parameter2_max)
							self.parameter2_value=bottom+" - "+top
						if self.parameter3=='B_Age':
							bottom,top=ageRange(self.parameter3_min,self.parameter3_max)
							self.parameter3_value=bottom+" - "+top
						if self.parameter2=='B_Ann_Income':
							bottom,top=incomeRange(self.parameter2_min,self.parameter2_max)
							self.parameter2_value=bottom+" - "+top
						if self.parameter3=='B_Ann_Income':
							bottom,top=incomeRange(self.parameter3_min,self.parameter3_max)
							self.parameter3_value=bottom+" - "+top	 



				else: #'''B_Race dont have least standard deviation'''
					self.parameter2 = self.sortedstd.iloc[2].keys()[0]
					self.parameter2_max = self.sortedstd[self.parameter2].iloc[7]
					self.parameter2_min = self.sortedstd[self.parameter2].iloc[3]
					if(self.sortedstd.iloc[2].keys()[1]=='B_Race'): #'''B_Race  have second least standard deviation'''
						self.parameter3=self.sortedstd.iloc[2].keys()[2]
					else:
						self.parameter3=self.sortedstd.iloc[2].keys()[1]
					self.top_2_param_percentage_distribution=self.Product_Buyer_Demographics\
													[(self.Product_Buyer_Demographics[self.parameter1]\
														==self.parameter1_value) \
													& ((self.Product_Buyer_Demographics[self.parameter2] \
														<= self.parameter2_max)\
													&(self.Product_Buyer_Demographics[self.parameter2] \
														>=self.parameter2_min))]\
													.count()['ID']/self.Product_Buyer_Demographics\
													.shape[0]*100\

					self.temp_df=self.Product_Buyer_Demographics\
															[(self.Product_Buyer_Demographics[self.parameter1]\
															==self.parameter1_value) \
															& ((self.Product_Buyer_Demographics[self.parameter2] \
															<= self.parameter2_max)\
															&(self.Product_Buyer_Demographics[self.parameter2] \
															>=self.parameter2_min))]
					# print("parameter2",self.parameter2,"min",self.parameter2_min,"max",self.parameter2_max)
					# print("TEmporary df",self.temp_df)											
					self.parameter3_min=self.temp_df[self.parameter3].min()
					self.parameter3_max=self.temp_df[self.parameter3].max()																	
						
					if self.parameter2=='B_Age':
						bottom,top=ageRange(self.parameter2_min,self.parameter2_max)
						self.parameter2_value=bottom+" - "+top
					if self.parameter3=='B_Age':
						print("top",self.parameter3_max,"bottom",self.parameter3_min)
						bottom,top=ageRange(self.parameter3_min,self.parameter3_max)
						self.parameter3_value=bottom+" - "+top 

					if self.parameter2=='B_Ann_Income':
						bottom,top=incomeRange(self.parameter2_min,self.parameter2_max)
						self.parameter2_value=bottom+" - "+top
					if self.parameter3=='B_Ann_Income':
						bottom,top=incomeRange(self.parameter3_min,self.parameter3_max)
						self.parameter3_value=bottom+" - "+top 	

			self.parameter1_value=Category_to_Gender(self.parameter1_value) 
		except:
			self.parameter1=0
			self.parameter1_value=0
			self.parameter2=0
			self.parameter2_value=0
			self.parameter3=0
			self.parameter3_value=0
			self.parameter4=0
			self.parameter4_value=0


		 

		