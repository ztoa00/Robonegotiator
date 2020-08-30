from flask import *
import os
import time
import ast
import json
import pandas as pd
from io import StringIO
import sys
import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import LabelEncoder
from sklearn.preprocessing import MinMaxScaler
from Database.dbconnect import DBConnect
import os
import config
# path = yaml.load(open('config.yml'))

class DealIntelligence():
	def __init__(self,UPC_Product_Code):
		try:
			self.UPC_Product_Code=UPC_Product_Code
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

			try:
				if(self.csvToSql==1):
					self.deals=self.DealObject.getDeals()
				else:
					# self.deals=pd.read_csv(str(path['dealPath']))
					self.deals=config.configDict['dealPath']
					#self.deals=pd.read_csv(str(os.path.dirname(os.path.abspath(""))+"/mapped_deal_customers.csv"))
			except:
				print("Cannot open mapped_deal_customers.csv/tbl_master_deals")
				self.deals=0
			if(self.csvToSql==1):
				self.deals.drop(self.deals[self.deals.seller_listed_price <= 0].index, inplace=True)
				self.deals.drop(self.deals[self.deals.buyer_highest_offer <= 0].index, inplace=True)
				'''K-Means clustering parameter  where lower parameter values
		 		implies Pro-Seller while higher parameter values implies Pro-Buyer'''
				self.deals['seller_segmentation_parameter'] = self.deals['seller_listed_price'] \
		                                              - self.deals['seller_deal_price']
				self.deals['buyer_segmentation_parameter'] = self.deals['buyer_highest_offer'] \
		                                             - self.deals['seller_deal_price']
			else:
				self.deals.drop(self.deals[self.deals.S_Listed_Price <= 0].index, inplace=True)
				self.deals.drop(self.deals[self.deals.B_Highest_Offer <= 0].index, inplace=True)
				'''K-Means clustering parameter  where lower parameter values
		 		implies Pro-Seller while higher parameter values implies Pro-Buyer'''
				self.deals['seller_segmentation_parameter'] = self.deals['S_Listed_Price'] \
		                                              - self.deals['S_Deal_Price']
				self.deals['buyer_segmentation_parameter'] = self.deals['B_Highest_Offer'] \
		                                             - self.deals['S_Deal_Price']
			self.deals = self.deals.fillna(0)
			self.getProducts()
		except:
			self.deals=0
				

	def getProducts(self):
		try:
			if(self.csvToSql==1):
				self.Products = self.deals.groupby(['upc_product_code'])
				#print("############################",self.Products.first(),"############################")
			else:
				self.Products = self.deals.groupby(['UPC_Product_Code'])
			
			self.getProduct()
		except:
			print("Invalid UPC_Product_Code")
			self.Products=0	

	def getProduct(self):
		try:
			if(self.csvToSql==1):
				self.Product = self.Products[['buyer_email','seller_deal_price','seller_listed_price',\
										'seller_lowest_price','seller_segmentation_parameter',\
										'buyer_offer', 'buyer_highest_offer',\
				                       'buyer_segmentation_parameter']]\
				                       .get_group((self.UPC_Product_Code))
				#print("############################",self.Product,"############################")                       

			else:
				self.Product = self.Products[['Buyer_Email','S_Deal_Price','S_Listed_Price','S_Lowest_Price',\
		                              'seller_segmentation_parameter','B_offer','B_Highest_Offer',\
				                       'buyer_segmentation_parameter']]\
				                       .get_group((self.UPC_Product_Code))	
			self.applyKmeans()
		except:
			print("Invalid UPC_Product_Code")
			self.Product=0					                       
	
	def applyKmeans(self):
		try:
			self.kmeans = KMeans(n_clusters=3,random_state=3425)
			self.x0 = np.array(self.Product.seller_segmentation_parameter).reshape(-1,1)
			# kmeans.fit(x0)
			self.x1 = np.array(self.Product.buyer_segmentation_parameter).reshape(-1,1)
			self.X = np.concatenate((self.x0,self.x1), axis=1)
			self.kmeans.fit(self.X)

			self.labels = self.kmeans.labels_
			self.labels = np.array(self.labels)
			self.labels = self.labels.reshape(self.labels.shape[0],1)
			self.labels = pd.DataFrame(self.labels,columns=['label'])
			self.Product = self.Product.reset_index(drop=True)
			self.Product = self.Product.join(self.labels)

			if(self.csvToSql==1):
				self.pro_seller_label = self.Product['label'][self.Product['seller_deal_price']\
		        	                 == self.Product['seller_deal_price'].max()].values[0]
				self.pro_buyer_label = self.Product['label'][self.Product['seller_deal_price'] \
		                      	   == self.Product['seller_deal_price'].min()].values[0]
				# neutral_label=Product['label'][Product['S_Deal_Price']==Product['S_Deal_Price'].median()].values[0]
			else:
				self.pro_seller_label = self.Product['label'][self.Product['S_Deal_Price']\
		        	                 == self.Product['S_Deal_Price'].max()].values[0]
				self.pro_buyer_label = self.Product['label'][self.Product['S_Deal_Price'] \
		                      	   == self.Product['S_Deal_Price'].min()].values[0]
				# neutral_label=Product['label'][Product['S_Deal_Price']==Product['S_Deal_Price'].median()].values[0]
			self.neutral_label = -1
			if (self.pro_buyer_label == 0 and self.pro_seller_label == 1)\
		   	or(self.pro_buyer_label == 1 and self.pro_seller_label == 0):
				self.neutral_label = 2
			elif (self.pro_buyer_label == 0 and self.pro_seller_label == 2)\
			or(self.pro_buyer_label == 2 and self.pro_seller_label == 0):
				self.neutral_label = 1
			elif (self.pro_buyer_label == 2 and self.pro_seller_label == 1)\
			or(self.pro_buyer_label == 1 and self.pro_seller_label == 2):
				self.neutral_label = 0  
			self.Product.loc[self.Product['label'] == self.neutral_label,'segment'] = 'Neutral'
			self.Product.loc[self.Product['label'] == self.pro_seller_label,'segment'] = 'Pro Seller'
			self.Product.loc[self.Product['label'] == self.pro_buyer_label,'segment'] = 'Pro Buyer'
			#print("############################",self.Product['label'],"############################")
			self.applyModel()
		except:
			print("Failed to apply Kmeans")
			self.Product=0

	def applyModel(self):
		try:
			if(self.csvToSql==1):
				self.lower_bound_parameter = 'buyer_offer'
				self.upper_bound_parameter = 'seller_listed_price'
			else:
				self.lower_bound_parameter = 'B_offer'
				self.upper_bound_parameter = 'S_Listed_Price'
			self.lower_bound = self.Product[[self.lower_bound_parameter]].mean(axis=0)
			self.upper_bound = self.Product[[self.upper_bound_parameter]].mean(axis=0)

			self.neutral = self.Product[self.Product.segment == 'Neutral']
			self.neutral['Pro_seller_deviation_param'] = ((self.upper_bound.values[0]\
			                                          -self.lower_bound.values[0])/2)
			if(self.csvToSql==1):
				self.neutral['pro_seller_deviation'] = self.neutral['seller_deal_price']\
		        	                               -self.neutral['Pro_seller_deviation_param']
				self.neutral_deviation = self.neutral[['pro_seller_deviation']].mean(axis=0)
				self.neutral_mean_S_Deal = self.neutral[['seller_deal_price']].mean(axis=0)


				self.pro_buyer = self.Product[self.Product.segment=='Pro Buyer']
				self.pro_buyer['Pro_buyer_deviation_param'] = ((self.upper_bound.values[0]\
			  	                                        +self.lower_bound.values[0])/2)
				self.pro_buyer['pro_buyer_deviation'] = self.pro_buyer['seller_deal_price']\
		    	                                    -self.pro_buyer['Pro_buyer_deviation_param']
				self.pro_buyer_deviation = self.pro_buyer[['pro_buyer_deviation']].mean(axis=0)
				self.pro_buyer_mean_S_Deal = self.pro_buyer[['seller_deal_price']].mean(axis=0)

				self.pro_buyer_mean_B_offer = self.pro_buyer[['buyer_offer']].mean(axis=0)
				self.pro_buyer_output = (self.pro_buyer_mean_S_Deal.values[0]\
			    	                -self.pro_buyer_mean_B_offer.values[0])\
							/self.pro_buyer_mean_B_offer.values[0]*100
				#print("***********pro_buyer_op****@@@@@@@@@@@@@@",self.pro_buyer_output)				
				self.pro_seller = self.Product[self.Product.segment=='Pro Seller']
				self.pro_seller['Pro_seller_deviation_param'] = ((self.upper_bound.values[0]\
			    	                                         -self.lower_bound.values[0])/2)
				#print("***********Pro_seller_deviation_param****@@@@@@@@@@@@@@",self.pro_seller,self.pro_seller['Pro_seller_deviation_param'])	
				self.pro_seller['pro_seller_deviation'] = self.pro_seller['seller_deal_price']\
												- self.pro_seller['Pro_seller_deviation_param']
				self.pro_seller_deviation = self.pro_seller[['pro_seller_deviation']].mean(axis=0)
				self.pro_seller_mean_S_Deal = self.pro_seller[['seller_deal_price']].mean(axis=0)
				self.pro_seller_mean_S_Listed = self.pro_seller[['seller_listed_price']].mean(axis=0)
				self.pro_seller_output = (self.pro_seller_mean_S_Listed.values[0]\
			    	                 -self.pro_seller_mean_S_Deal.values[0])\
								/self.pro_seller_mean_S_Listed.values[0]*100
								
				self.ProSellerProducts = self.pro_seller.shape[0]
				#print("***********pro_seller_op****@@@@@@@@@@@@@@",self.pro_seller_output)
				if self.ProSellerProducts<1:
					self.pro_seller_output=0
					self.pro_seller_mean_S_Deal=0

				self.ProBuyerProducts = self.pro_buyer.shape[0]
				if self.ProBuyerProducts<1:
					self.pro_buyer_output=0
					self.pro_buyer_mean_S_Deal=0
				self.NeutralProducts = self.neutral.shape[0]
				if self.NeutralProducts<1:
					self.neutral_mean_S_Deal=0
				self.total = self.ProBuyerProducts+self.ProSellerProducts\
		    		        +self.NeutralProducts
				self.master_average = self.Product[['seller_deal_price']].mean(axis=0).values[0]
			else:
				self.neutral['pro_seller_deviation'] = self.neutral['S_Deal_Price']\
		        	                               -self.neutral['Pro_seller_deviation_param']
				self.neutral_deviation = self.neutral[['pro_seller_deviation']].mean(axis=0)
				self.neutral_mean_S_Deal = self.neutral[['S_Deal_Price']].mean(axis=0)

				self.pro_buyer = self.Product[self.Product.segment=='Pro Buyer']
				self.pro_buyer['Pro_buyer_deviation_param'] = ((self.upper_bound.values[0]\
			  	                                        +self.lower_bound.values[0])/2)
				self.pro_buyer['pro_buyer_deviation'] = self.pro_buyer['S_Deal_Price']\
		    	                                    -self.pro_buyer['Pro_buyer_deviation_param']
				self.pro_buyer_deviation = self.pro_buyer[['pro_buyer_deviation']].mean(axis=0)
				self.pro_buyer_mean_S_Deal = self.pro_buyer[['S_Deal_Price']].mean(axis=0)
				self.pro_buyer_mean_B_offer = self.pro_buyer[['B_offer']].mean(axis=0)
				self.pro_buyer_output = (self.pro_buyer_mean_S_Deal.values[0]\
			    	                -self.pro_buyer_mean_B_offer.values[0])\
							/self.pro_buyer_mean_B_offer.values[0]*100

				self.pro_seller = self.Product[self.Product.segment=='Pro Seller']
				self.pro_seller['Pro_seller_deviation_param'] = ((self.upper_bound.values[0]\
			    	                                         -self.lower_bound.values[0])/2)
				self.pro_seller['pro_seller_deviation'] = self.pro_seller['S_Deal_Price']\
												- self.pro_seller['Pro_seller_deviation_param']
				self.pro_seller_deviation = self.pro_seller[['pro_seller_deviation']].mean(axis=0)
				self.pro_seller_mean_S_Deal = self.pro_seller[['S_Deal_Price']].mean(axis=0)
				self.pro_seller_mean_S_Listed = self.pro_seller[['S_Listed_Price']].mean(axis=0)
				self.pro_seller_output = (self.pro_seller_mean_S_Listed.values[0]\
			    	                 -self.pro_seller_mean_S_Deal.values[0])\
								/self.pro_seller_mean_S_Listed.values[0]*100

				self.ProSellerProducts = self.pro_seller.shape[0]
				if self.ProSellerProducts<1:
					self.pro_seller_output=0
					self.pro_seller_mean_S_Deal=0

				self.ProBuyerProducts = self.pro_buyer.shape[0]
				if self.ProBuyerProducts<1:
					self.pro_buyer_output=0
					self.pro_buyer_mean_S_Deal=0
				self.NeutralProducts = self.neutral.shape[0]
				if self.NeutralProducts<1:
					self.neutral_mean_S_Deal=0
				self.total = self.ProBuyerProducts+self.ProSellerProducts\
		    		        +self.NeutralProducts
				self.master_average = self.Product[['S_Deal_Price']].mean(axis=0).values[0]	
		except:
			self.total=0


