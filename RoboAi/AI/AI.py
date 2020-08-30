import pandas as pd
from Database.dbconnect import DBConnect
from sklearn.linear_model import LogisticRegression


class AI():
	def __init__(self,UPC_Product_Code, Seller_Email, Buyer_Email, API_password, weights=[.34,.33,.33]):
		'''
        Weights for buyer, seller and product.

        '''
		self.weights = weights
		self.db = DBConnect()
		self.upc = UPC_Product_Code
		self.seller = Seller_Email
		self.buyer = Buyer_Email
		self.api_password = API_password
    
	def createBuyerModel(self):
	
        #Get the data and hot encode categorial features
		self.buyerData = self.db.getBuyerData(self.buyer)
		months_encoded = pd.get_dummies(self.buyerData.month, prefix='month')
		self.buyerData = self.buyerData.drop(columns=['month'])
		self.buyerData = self.buyerData.join(months_encoded)

        #prepare the data for training
		y_train = self.buyerData['closed_deal']
		self.buyerData = self.buyerData.drop(columns=['closed_deal'])
		X_train = self.buyerData.fillna(value=0)

        #model the data
		self.buyerModel = LogisticRegression()
		self.buyerModel = self.buyerModel.fit(X_train, y_train)
        
        #create the prediction function
	def predictionBuyer(self, dataframe):

		'''
    min_qty, max_qty, min_price, max_price, ave_price, min_offer, max_offer, ave_offer,month_1, month_2, month_3, month_4, month_5, month_6, month_7, month_8, month_9, month_10, month_11, month_12

		data ={ 'min_qty' : [min_qty],
                'max_qty' : [max_qty],
                'min_price' : [min_price],
                'max_price' : [max_price],
                'ave_price' : [ave_price],
                'min_offer' : [min_offer],
                'max_offer' : [max_offer],
                'ave_offer' : [ave_offer],
                'month_1' : [month_1],
                'month_2' : [month_2],
                'month_3' : [month_3],
                'month_4' : [month_4],
                'month_5' : [month_5],
                'month_6' : [month_6],
                'month_7': [month_7],
                'month_8': [month_8],
                'month_9': [month_9],
                'month_10': [month_10],
                'month_11': [month_11],
                'month_12': [month_12] }
            
		dataf = pd.DataFrame(data, columns=self.buyerData.columns)
        '''
		dataf = dataframe.drop(columns=[col for col in dataframe if col not in self.buyerData.columns])

		return self.buyerModel.predict_proba(dataf)[0][1]*100


	def createSellerModel(self):
		self.sellerData = self.db.getSellerData(self.seller)

        #Get the data and hot encode categorial features

		months_encoded = pd.get_dummies(self.sellerData.month, prefix='month')
		self.sellerData = self.sellerData.drop(columns=['month'])
		self.sellerData = self.sellerData.join(months_encoded)

        #prepare the data for training
		y_train = self.sellerData['closed_deal']
		self.sellerData = self.sellerData.drop(columns=['closed_deal'])
		X_train = self.sellerData.fillna(value=0)

        #model the data
		sellerModel = LogisticRegression()
		self.sellerModel = sellerModel.fit(X_train, y_train)

	def predictionSeller(self, dataframe):
    
		'''
    min_qty, max_qty, min_price, max_price, ave_price, min_deal, max_deal, ave_deal,month_1, month_2, month_3, month_4, month_5, month_6, month_7, month_8, month_9, month_10, month_11, month_12

		data ={ 'min_qty' : [min_qty],
                'max_qty' : [max_qty],
                'min_price' : [min_price],
                'max_price' : [max_price],
                'ave_price' : [ave_price],
                'min_deal' : [min_deal],
                'max_deal' : [max_deal],
                'ave_deal' : [ave_deal],
                'month_1' : [month_1],
                'month_2' : [month_2],
                'month_3' : [month_3],
                'month_4' : [month_4],
                'month_5' : [month_5],
                'month_6' : [month_6],
                'month_7': [month_7],
                'month_8': [month_8],
                'month_9': [month_9],
                'month_10': [month_10],
                'month_11': [month_11],
                'month_12': [month_12] }


		dataf = pd.DataFrame(data, columns=self.sellerData.columns).fillna(value=0)
        '''
		dataf = dataframe.drop(columns=[col for col in dataframe if col not in self.sellerData.columns])

		return self.sellerModel.predict_proba(dataf)[0][1]*100

	def createProductModel(self):
		self.productData = self.db.getProductData()

        #Get the data and hot encode categorial features
		parameter1_encoded = pd.get_dummies(self.productData.parameter1, prefix='parameter1')
		parameter2_encoded = pd.get_dummies(self.productData.parameter2, prefix='parameter2')
		parameter3_encoded = pd.get_dummies(self.productData.parameter3, prefix='parameter3')
		parameter4_encoded = pd.get_dummies(self.productData.parameter4, prefix='parameter4')
		parameter5_encoded = pd.get_dummies(self.productData.parameter5, prefix='parameter5')
		category_encoded = pd.get_dummies(self.productData.category, prefix='category')
        
        
		self.productData = self.productData.drop(columns=['parameter1','parameter2','parameter3', 'parameter4', 'parameter5', 'category'])

		self.productData = self.productData.join(parameter1_encoded)
		self.productData = self.productData.join(parameter2_encoded)
		self.productData = self.productData.join(parameter3_encoded)
		self.productData = self.productData.join(parameter4_encoded)
		self.productData = self.productData.join(parameter5_encoded)
		self.productData = self.productData.join(category_encoded)

        #prepare the data for training
		y_train = self.productData['closed_deal']
		self.productData = self.productData.drop(columns=['closed_deal'])
		X_train = self.productData

        #model the data
		self.productModel = LogisticRegression()
		self.productModel = self.productModel.fit(X_train, y_train)

	def predictionProduct(self, dictionary):
		'''
        Input list of object with category and list of boolean values as attributes. The category is the concatenation of column name and column value. 
        For example, dictionary = {'category_automobile':[1]}
        '''
		dataf = pd.DataFrame(dictionary, columns=self.productData.columns).fillna(value=0)

		return self.productModel.predict_proba(dataf)[0][1]*100

	def predict(self):
		self.createBuyerModel()
		self.createSellerModel()
		self.createProductModel()

        #Request for the data
		sellerRequestData = self.db.getSellerRequestData(self.seller,self.upc)
		buyerRequestData = self.db.getBuyerRequestData(self.buyer, self.upc)
		productRequestData = self.db.getProductRequestData(self.upc)

        #Clean up the data and one hot encode the categorical features
		buyer_months_encoded = pd.get_dummies(buyerRequestData.month, prefix='month')
		self.buyerRequestData = buyerRequestData.drop(columns=['month'])
		self.buyerRequestData = self.buyerRequestData.join(buyer_months_encoded)


		seller_months_encoded = pd.get_dummies(sellerRequestData.month, prefix='month')
		self.sellerRequestData = sellerRequestData.drop(columns=['month'])
		self.sellerRequestData = self.sellerRequestData.join(seller_months_encoded)

		parameter1_encoded = pd.get_dummies(productRequestData.parameter1, prefix='parameter1')
		parameter2_encoded = pd.get_dummies(productRequestData.parameter2, prefix='parameter2')
		parameter3_encoded = pd.get_dummies(productRequestData.parameter3, prefix='parameter3')
		parameter4_encoded = pd.get_dummies(productRequestData.parameter4, prefix='parameter4')
		parameter5_encoded = pd.get_dummies(productRequestData.parameter5, prefix='parameter5')
		category_encoded = pd.get_dummies(productRequestData.category, prefix='category')
        
        
		self.productRequestData = productRequestData.drop(columns=['parameter1','parameter2','parameter3', 'parameter4', 'parameter5', 'category'])

		self.productRequestData = self.productRequestData.join(parameter1_encoded)
		self.productRequestData = self.productRequestData.join(parameter2_encoded)
		self.productRequestData = self.productRequestData.join(parameter3_encoded)
		self.productRequestData = self.productRequestData.join(parameter4_encoded)
		self.productRequestData = self.productRequestData.join(parameter5_encoded)


        #Predict probabilities
		try:
			self.buyerProability = self.predictionBuyer(self.buyerRequestData)
		except:
			self.buyerProability = 0
			self.weights[1] = self.weights[1] + self.weights[0]/2
			self.weights[2] = self.weights[1] + self.weights[0]/2
			self.weights[0] = 0

		try:
			self.sellerProbability = self.predictionSeller(self.sellerRequestData)
		except:
			self.sellerProbability = 0
			if self.weights[0] == 0:
				self.weights[2] = self.weights[1] + self.weights[2]
			else:
				self.weights[0] = self.weights[0] + self.weights[1]/2
				self.weights[2] = self.weights[2] + self.weights[1]/2
				self.weights[1] = 0
		
		try:
			self.productProbability = self.predictionProduct(self.productRequestData)
		except:
			self.weights[0] = 0
			self.weights[2] = 0
			self.weights[1] = 0
			self.productProbability = 0

		prediction = [self.buyerProability,self.sellerProbability,self.productProbability]

		return sum(x * y for x, y in zip(prediction, self.weights))
