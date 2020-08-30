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
class BuyerProfile():
	"""docstring for BuyerProfile"""
	def __init__(self,Buyer_Email):
		try:
			self.Buyer_Email=Buyer_Email
			# self.csvToSql=path['csvToSql']
			self.csvToSql=config.configDict['csvToSql']
			if(self.csvToSql==1):
				self.DealObject=DBConnect()
			self.getDeals()
		except:
			print("Enter valid Buyer_Email")
			self.total_Deals=0
			

	def getDeals(self):
		try:
			if(self.csvToSql==1):
				#DealObject=DBConnect()
				self.deals=self.DealObject.getDeals()
				# print("Success############################")

			else:
				# self.deals=pd.read_csv(str(path['dealPath']))
				self.deals=pd.read_csv(config.configDict['dealPath'])
				# self.deals=pd.read_csv(str(os.path.dirname(os.path.abspath(""))+"/mapped_deal_customers.csv"))
			self.deals = self.deals.dropna()
			self.getBuyerDeals()
		except:
			print("Cannot open mapped_deal_customers.csv /tbl_master_deals")
			self.total_Deals=0

	def getBuyerDeals(self):
		try:
			if(self.csvToSql==1):
				self.Buyer=self.deals.groupby(('buyer_email'))
				# print("Success1############################")
			else:
				self.Buyer=self.deals.groupby(('Buyer_Email'))
			self.Buyer=self.Buyer.get_group(self.Buyer_Email)
			self.getBuyerIntelligence()
		except:
			print("Buyer_Email not found in mapped_deal_customers.csv/tbl_master_deals")
			self.total_Deals=0
			
			
			
	def getBuyerIntelligence(self):
		try:
			if(self.csvToSql==1):
				self.Buyer['minimum%param'] = self.Buyer['seller_deal_price'] - self.Buyer['buyer_offer']
				self.average_Deal_Price = self.Buyer['seller_deal_price'].mean()
				self.average_Offer_Price = self.Buyer['buyer_offer'].mean()
				# print("Success############################22")

			else:
				self.Buyer['minimum%param'] = self.Buyer['S_Deal_Price'] - self.Buyer['B_offer']
				self.average_Deal_Price = self.Buyer['S_Deal_Price'].mean()
				self.average_Offer_Price = self.Buyer['B_offer'].mean()
			try:
				self.average_percentage_increase = (self.average_Deal_Price-self.average_Offer_Price)\
		                               /self.average_Offer_Price*100
			except ZeroDivisionError:
				self.average_percentage_increase=0
		                               
			self.Buyer = self.Buyer.sort_values(by=['minimum%param'])
			self.Buyer = self.Buyer.reset_index(drop=True)
			try:
				if(self.csvToSql==1):
					self.minimum_percentage_increase=(self.Buyer.iloc[0]['seller_deal_price']-\
			                              self.Buyer.iloc[0]['buyer_offer'])\
									      /self.Buyer.iloc[0]['seller_deal_price']*100
					# print("Success############################33")
				else:
					self.minimum_percentage_increase=(self.Buyer.iloc[0]['S_Deal_Price']-\
			                              self.Buyer.iloc[0]['B_offer'])\
									      /self.Buyer.iloc[0]['S_Deal_Price']*100
			except ZeroDivisionError:
				self.minimum_percentage_increase=0
			try:
				if(self.Buyer.shape[0]>=2):
					if(self.csvToSql==1):
						self.maximum_percentage_increase=(self.Buyer.iloc[(self.Buyer.shape[0]-1)]['seller_deal_price']\
									-self.Buyer.iloc[(self.Buyer.shape[0]-1)]['buyer_offer'])\
									/self.Buyer.iloc[(self.Buyer.shape[0]-1)]['buyer_offer']*100
						# print("Success############################44")
					else:
						self.maximum_percentage_increase=(self.Buyer.iloc[(self.Buyer.shape[0]-1)]['S_Deal_Price']\
									-self.Buyer.iloc[(self.Buyer.shape[0]-1)]['B_offer'])\
									/self.Buyer.iloc[(self.Buyer.shape[0]-1)]['B_offer']*100
			except ZeroDivisionError:
				self.maximum_percentage_increase=0
			except :
				self.maximum_percentage_increase=0
										
			self.total_Deals=self.Buyer.shape[0]
			if(self.csvToSql==1):
				self.NotMatching=self.Buyer[self.Buyer['final_deal_status']==0].shape[0]
				self.FullyMatched=self.Buyer[self.Buyer['final_deal_status']==1].shape[0]
				self.PartialMatched=self.Buyer[self.Buyer['final_deal_status']==2].shape[0]
				self.InNegotiation=self.Buyer[self.Buyer['final_deal_status']==4].shape[0]
				# print("Success############################55")
				print(self.NotMatching,self.FullyMatched,self.PartialMatched,self.InNegotiation)
			else:
				self.NotMatching=self.Buyer[self.Buyer['Negotiation_Status']=='Not Matching'].shape[0]
				self.FullyMatched=self.Buyer[self.Buyer['Negotiation_Status']=='Fully Matched'].shape[0]
				#self.AbortedInMiddle=self.Buyer[self.Buyer['Negotiation_Status']=='Aborted in middle'].shape[0]
				self.PartialMatched=self.Buyer[self.Buyer['Negotiation_Status']=='Partial Matched'].shape[0]
				self.InNegotiation=self.Buyer[self.Buyer['Negotiation_Status']=='In Negotiation'].shape[0]
		except:
			self.total_Deals=0

			

				
