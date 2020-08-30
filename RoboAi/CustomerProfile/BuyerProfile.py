import pandas as pd
from Database.dbconnect import DBConnect


class BuyerProfile:

    def __init__(self, buyer_email):
        try:
            self.DbObject = DBConnect()
        except:
            # code to handle local db
            pass

        self.BuyerEmail = buyer_email
        self.getBuyerProfile()

    def getBuyerProfile(self):
        deals = self.getBuyerDeals(self.BuyerEmail)
        if not deals.empty:
            deals['decrease'] = deals['buyer_highest_offer'] - deals['seller_deal_price']
            self.BuyerAverageDecrease = deals['decrease'].mean()
            self.BuyerMinimumDecrease = deals['decrease'].min()
            self.BuyerMaximumDecrease = deals['decrease'].max()

            deals['decrease_percent'] = (deals['decrease'] / deals['buyer_highest_offer']) * 100
            self.BuyerAverageDecreasePercentage = deals['decrease_percent'].mean()
            self.BuyerMinimumDecreasePercentage = deals['decrease_percent'].min()
            self.BuyerMaximumDecreasePercentage = deals['decrease_percent'].max()

        else:
            self.BuyerAverageDecrease = self.BuyerMinimumDecrease = self.BuyerMaximumDecrease = 0
            self.BuyerAverageDecreasePercentage = self.BuyerMinimumDecreasePercentage = self.BuyerMaximumDecreasePercentage = 0

    def getBuyerDeals(self, buyer_email):
        self.DbObject.cHandler.execute(
            "select id,upc_product_code,seller_deal_price,buyer_highest_offer from tbl_master_deals where buyer_email='" + buyer_email + "';")
        self.results = self.DbObject.cHandler.fetchall()
        self.deals = pd.DataFrame(list(self.results), columns=['id', 'upc_product_code',
                                                               'seller_deal_price',
                                                               'buyer_highest_offer'])
        return self.deals
