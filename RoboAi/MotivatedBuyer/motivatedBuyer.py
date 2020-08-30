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
from MostCommonDemographics.mostCommonDemographics import MostCommonDemographics
import requests
import config
# path = yaml.load(open('config.yml'))
class isMotivatedBuyer():
	"""docstring for BuyerProfile"""
	def __init__(self,Buyer_Email,UPC_Product_Code):
		try:
			self.Buyer_Email=Buyer_Email
			self.UPC_Product_Code=UPC_Product_Code
			# self.csvToSql=path['csvToSql']
			self.csvToSql=config.configDict['csvToSql']
			if(self.csvToSql==1):
				self.DBObject=DBConnect()
			self.getBuyerDetails(self.Buyer_Email)
		except:
			#print("Enter valid Buyer_Email/UPC_Product_Code")
			self.total_Deals=0

	def getBuyerDetails(self,Buyer_Email):
		if(self.csvToSql==1):
			self.Buyer=self.DBObject.getBuyer(Buyer_Email)
			# print("**************************",self.Buyer)
			self.getCommonAttributes(self.UPC_Product_Code)

	def getCommonAttributes(self,UPC_Product_Code):
		if(self.csvToSql==1):
			self.common=[]
			data = {'UPC_Product_Code':UPC_Product_Code}
			# self.commonAttributes = requests.post(url = str(path['getMostCommonDemographics']), data = data) 
			self.commonAttributes = requests.post(url = config.configDict['getMostCommonDemographics'], data = data) 
			#self.commonAttributes=redirect(url_for('getMostCommonDemographics',UPC_Product_Code=UPC_Product_Code))
			self.commonAttributes = self.commonAttributes.json()
			# print("$$$$$$$$$#$#$#$#$#$",self.Buyer,"^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^",self.commonAttributes)
			# print('commonAttributes'*5,self.commonAttributes['parameter1_value'],"*"*10)
			# print('buyer'*5,self.Buyer[self.commonAttributes['parameter1']])
			# print('commonAttributes'*5,self.commonAttributes['parameter2_value'],"*"*10)
			# print('buyer'*5,self.Buyer[self.commonAttributes['parameter2']])
			# print('commonAttributes'*5,self.commonAttributes['parameter3_value'],"*"*10)
			# print('buyer'*5,self.Buyer[self.commonAttributes['parameter3']])
			# print('commonAttributes'*5,self.commonAttributes['parameter4_value'],"*"*10)
			# print('buyer'*5,self.Buyer[self.commonAttributes['parameter4']])
			# print("1"*10,str(self.commonAttributes['parameter1_value']).upper())
			# print("2"*10,str(self.Buyer[self.commonAttributes['parameter1']]).upper())
			# print(self.Buyer['age'].tolist()[0])
			if str(self.commonAttributes['parameter1_value']).upper() == str(self.Buyer[self.commonAttributes['parameter1']].tolist()[0]).upper():
				self.common.append(str(self.commonAttributes['parameter1']))
				

			if self.commonAttributes['parameter2']=='race':
				if str(self.commonAttributes['parameter2_value']).upper() == str(self.Buyer[self.commonAttributes['parameter2']].tolist()[0]).upper():
					self.common.append(str(self.commonAttributes['parameter2']))

			if self.commonAttributes['parameter3']=='age':
				if self.Buyer[self.commonAttributes['parameter3']].tolist()[0] in range(int(self.commonAttributes['parameter3_value'].split("-")[0]),1+int(self.commonAttributes['parameter3_value'].split("-")[1])):
					self.common.append(str(self.commonAttributes['parameter3']))


			if self.commonAttributes['parameter4']=='annual_income':
				if self.commonAttributes['parameter4_value'].split("-")[0]==' 200000+':
					if self.Buyer[self.commonAttributes['parameter4']].tolist()[0] >= int(200000):
						self.common.append(str(self.commonAttributes['parameter4']))
				elif self.commonAttributes['parameter4_value'].split("-")[1]==' 200000+':
					if self.Buyer[self.commonAttributes['parameter4']].tolist()[0] >= int(self.commonAttributes['parameter4_value'].split("-")[0]):
						self.common.append(str(self.commonAttributes['parameter4']))
				elif self.Buyer[self.commonAttributes['parameter4']].tolist()[0] in range(int(self.commonAttributes['parameter4_value'].split("-")[0]),1+int(self.commonAttributes['parameter4_value'].split("-")[1])):
					self.common.append(str(self.commonAttributes['parameter4']))

			# print(self.common)	
			# print(self.commonAttributes['parameter4_value'].split("-")[1][1::]=='200000+')
			# print(self.Buyer[self.commonAttributes['parameter4']].tolist()[0])
