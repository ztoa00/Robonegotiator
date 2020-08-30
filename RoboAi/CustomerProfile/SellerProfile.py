import pandas as pd
from Database.dbconnect import DBConnect


class SellerProfile:

    def __init__(self, seller_email):

        try:
            self.DbObject = DBConnect()
        except:
            # code to handle local db
            pass

        self.SellerEmail = seller_email
        self.getSellerProfile()

    def getSellerProfile(self):
        deals = self.getSellerDeals(self.SellerEmail)
        if not deals.empty:
            deals['increase'] = deals['seller_listed_price'] - deals['seller_deal_price']
            self.SellerMinimumIncrease = deals['increase'].min()
            self.SellerMaximumIncrease = deals['increase'].max()
            self.SellerAverageIncrease = deals['increase'].mean()

            deals['increase_percent'] = (deals['increase'] / deals['seller_listed_price']) * 100
            self.SellerAverageIncreasePercentage = deals['increase_percent'].mean()
            self.SellerMinimumIncreasePercentage = deals['increase_percent'].min()
            self.SellerMaximumIncreasePercentage = deals['increase_percent'].max()
            self.xx = deals['increase_percent']

        else:
            self.SellerMinimumIncrease = self.SellerMaximumIncrease = self.SellerAverageIncrease = 0
            self.SellerAverageIncreasePercentage = self.SellerMinimumIncreasePercentage = self.SellerMaximumIncreasePercentage = 0

    def getSellerDeals(self, seller_email):
        self.DbObject.cHandler.execute(
            "select id,upc_product_code,seller_deal_price,seller_listed_price from tbl_master_deals where seller_email='" + seller_email + "';")
        self.results = self.DbObject.cHandler.fetchall()
        self.deals = pd.DataFrame(list(self.results), columns=['id', 'upc_product_code',
                                                               'seller_deal_price',
                                                               'seller_listed_price'])
        return self.deals
