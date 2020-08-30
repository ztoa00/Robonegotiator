import pandas as pd
import config
import pymysql


# path = yaml.load(open('config.yml'))
def Age_to_Age_Range(age):
    if age >= 0 and age < 18:
        return '0-17'
    elif age >= 18 and age < 35:
        return '18-34'
    elif age >= 35 and age < 50:
        return '35-49'
    elif age >= 50 and age < 71:
        return '50-70'
    else:
        return '71-100'


def Income_to_Income_Range(income):
    if income < 20000:
        return 'less than 20000'
    elif income >= 20000 and income <= 44999:
        return '20000-44999'
    elif income >= 45000 and income <= 139999:
        return '45000-139999'
    elif income >= 140000 and income <= 149999:
        return '140000-149999'
    elif income >= 150000 and income <= 199999:
        return '150000-199999'
    else:
        return '200000+'


class DBConnect():
    """docstring for DBConnect"""

    def __init__(self):
        self.myDB = pymysql.connect(host=config.configDict['host'], port=int(3306), user=config.configDict['user'],
                                    passwd=config.configDict['passwd'], db=config.configDict['database']);

        self.cHandler = self.myDB.cursor()

    def getDeals(self):
        self.cHandler.execute(
            "select id,upc_product_code,buyer_email,seller_lowest_price,seller_deal_price,seller_listed_price,buyer_offer_price,buyer_highest_offer,final_deal_status from tbl_master_deals")
        self.results = self.cHandler.fetchall()
        self.deals = pd.DataFrame(list(self.results), columns=['id', \
                                                               'upc_product_code', 'buyer_email', 'seller_lowest_price',
                                                               'seller_deal_price', \
                                                               'seller_listed_price', 'buyer_offer',
                                                               'buyer_highest_offer', \
                                                               'final_deal_status', ])
        # print(self.deals)
        return self.deals

    def getBuyers(self):
        self.cHandler.execute("select id,email_id,sex,race,age,annual_income from tbl_buyers")
        self.results = self.cHandler.fetchall()
        self.buyers = pd.DataFrame(list(self.results), columns=['id', 'email_id', 'sex', 'race', 'age', \
                                                                'annual_income'])
        self.buyers['age'] = self.buyers['age'].map(Age_to_Age_Range)
        self.buyers['annual_income'] = self.buyers['annual_income'].map(Income_to_Income_Range)
        return self.buyers

    def getBuyer(self, buyer_email):
        self.cHandler.execute(
            "select id,email_id,sex,race,age,annual_income from tbl_buyers where email_id='" + buyer_email + "'")
        self.results = self.cHandler.fetchall()
        self.buyer = pd.DataFrame(list(self.results), columns=['id', 'email_id', 'sex', 'race', 'age', \
                                                               'annual_income'])
        return self.buyer

    def getHistoricalData(self, upc_product_code):
        self.cHandler.execute(
            "select avg(final_amount), count(*), sum(matched_quantity) from tbl_closed_deals where upc_product_code='" + upc_product_code + "'")

        self.results = self.cHandler.fetchone()
        self.historicalData = {}

        if self.results[1] != 0:
            self.historicalData['AverageClosedDeals'] = self.results[0]
            self.historicalData['TotalCount'] = self.results[1]
            self.historicalData['TotalQuantity'] = float(self.results[2])
        else:
            self.historicalData['AverageClosedDeals'] = 0
            self.historicalData['TotalCount'] = 0
            self.historicalData['TotalQuantity'] = 0

        return self.historicalData;

    def getProductOffersData(db, api_password, seller_email, upc_product_code):
        if api_password != '' and seller_email != '' and upc_product_code != '':
            sql = '''
            Select 
            (tbl_products.id) as id, 
            (tbl_products.upc_product_code) as  upc_product_code, 
            (tbl_products.seller_email) as seller_email, 
            (tbl_products.catalog_id) as catalog_id,
            (title) as title, 
            (description) as description, 
            (category) as category,
            (sub_category) as sub_category, 
            (parameter1) as parameter1, 
            (parameter2) as parameter2, 
            (parameter3) as parameter3, 
            (parameter4) as parameter4, 
            (parameter5) as parameter5, 
            (bulk_or_individual) as bulk_or_individual, 
            (product_status) as product_status, 
            (buyer_offers.created_at) as created_at, 
            (buyer_offers.updated_at) as updated_at, 
            (buyer_offer_price) AS buyer_offer_price,  
            (averagePrice) AS avg_buyer_offer_price,
            (buyer_highest_offer_price) AS buyer_highest_offer_price

            from 
            (select *, (buyer_offer_price + buyer_highest_offer_price)/2 as averagePrice
            from tbl_buyer_offers) buyer_offers

            join tbl_products on (tbl_products.upc_product_code = buyer_offers.upc_product_code)
            join tbl_service_requests on (tbl_service_requests.id = buyer_offers.id)

            where 
            tbl_service_requests.api_password = '{}' and
            tbl_products.seller_email = '{}' and
            tbl_products.upc_product_code = '{}';
            '''.format(api_password, seller_email, upc_product_code)

        elif api_password != '' and seller_email != '' and upc_product_code == '':
            sql = '''
            Select 
            (tbl_products.id) as id, 
            (tbl_products.upc_product_code) as  upc_product_code, 
            (tbl_products.seller_email) as seller_email, 
            (tbl_products.catalog_id) as catalog_id,
            (title) as title, 
            (description) as description, 
            (category) as category,
            (sub_category) as sub_category, 
            (parameter1) as parameter1, 
            (parameter2) as parameter2, 
            (parameter3) as parameter3, 
            (parameter4) as parameter4, 
            (parameter5) as parameter5, 
            (bulk_or_individual) as bulk_or_individual, 
            (product_status) as product_status, 
            (buyer_offers.created_at) as created_at, 
            (buyer_offers.updated_at) as updated_at, 
            (buyer_offer_price) AS buyer_offer_price, 
            (averagePrice) AS avg_buyer_offer_price,
            (buyer_highest_offer_price) AS buyer_highest_offer_price

            from 
            (select *, (buyer_offer_price + buyer_highest_offer_price)/2 as averagePrice
            from tbl_buyer_offers) buyer_offers

            join tbl_products on (tbl_products.upc_product_code = buyer_offers.upc_product_code)
            join tbl_service_requests on (tbl_service_requests.id = buyer_offers.id)

            where 
            tbl_service_requests.api_password = '{}' and
            tbl_products.seller_email = '{}';
            '''.format(api_password, seller_email)

        elif api_password != '' and seller_email == '' and upc_product_code == '':
            sql = '''
            Select 
            (tbl_products.id) as id, 
            (tbl_products.upc_product_code) as  upc_product_code, 
            (tbl_products.seller_email) as seller_email, 
            (tbl_products.catalog_id) as catalog_id,
            (title) as title, 
            (description) as description, 
            (category) as category,
            (sub_category) as sub_category, 
            (parameter1) as parameter1, 
            (parameter2) as parameter2, 
            (parameter3) as parameter3, 
            (parameter4) as parameter4, 
            (parameter5) as parameter5, 
            (bulk_or_individual) as bulk_or_individual, 
            (product_status) as product_status, 
            (buyer_offers.created_at) as created_at, 
            (buyer_offers.updated_at) as updated_at, 
            (buyer_offer_price) AS buyer_offer_price,
            (averagePrice) AS avg_buyer_offer_price,
            (buyer_highest_offer_price) AS buyer_highest_offer_price

            from 
            (select *, (buyer_offer_price + buyer_highest_offer_price)/2 as averagePrice
            from tbl_buyer_offers) buyer_offers

            join tbl_products on (tbl_products.upc_product_code = buyer_offers.upc_product_code)
            join tbl_service_requests on (tbl_service_requests.id = buyer_offers.id)

            where 
            tbl_service_requests.api_password = '{}';
            '''.format(api_password)

        else:
            returnObject = {'success': 'false'}
            return returnObject

        results = pd.read_sql_query(sql, db.myDB)
        results['id'] = results['id'].astype(int)
        results['buyer_offer_price'] = results['buyer_offer_price'].astype(float)
        results['avg_buyer_offer_price'] = results['avg_buyer_offer_price'].astype(float)
        results['buyer_highest_offer_price'] = results['buyer_highest_offer_price'].astype(float)

        returnObject = {'success': 'true', 'total_offers': int(len(results.index)),
                        'min_buyer_offer_price': float(results['buyer_offer_price'].min()),
                        'max_buyer_offer_price': float(results['buyer_offer_price'].max()),
                        'avg_buyer_offer_price': float(results['avg_buyer_offer_price'].mean()),
                        'min_buyer_highest_offer_price': float(results['buyer_highest_offer_price'].min()),
                        'max_buyer_highest_offer_price': float(results['buyer_highest_offer_price'].max()),
                        'avg_buyer_highest_offer_price': float(results['buyer_highest_offer_price'].mean()), 'data': []
                        }

        for i in range(0, len(results)):
            lineObject = {'id': int(results.iloc[i]['id']),
                          'upc_product_code': str(results.iloc[i]['upc_product_code']),
                          'title': str(results.iloc[i]['title']), 'description': str(results.iloc[i]['description']),
                          'category': str(results.iloc[i]['category']),
                          'sub_category': str(results.iloc[i]['sub_category']),
                          'parameter1': str(results.iloc[i]['parameter1']),
                          'parameter2': str(results.iloc[i]['parameter2']),
                          'parameter3': str(results.iloc[i]['parameter3']),
                          'parameter4': str(results.iloc[i]['parameter4']),
                          'parameter5': str(results.iloc[i]['parameter5']),
                          'bulk_or_individual': str(results.iloc[i]['bulk_or_individual']),
                          'product_status': str(results.iloc[i]['product_status']),
                          'seller_email': str(results.iloc[i]['seller_email']),
                          'catalog_id': int(results.iloc[i]['catalog_id']),
                          'created_at': str(results.iloc[i]['created_at']),
                          'updated_at': str(results.iloc[i]['updated_at']),
                          'buyer_offer_price': float(results.iloc[i]['buyer_offer_price']),
                          'avg_buyer_offer_price': float(results.iloc[i]['avg_buyer_offer_price']),
                          'buyer_highest_offer_price': float(results.iloc[i]['buyer_highest_offer_price'])
                          }
            returnObject['data'].append(lineObject)

        return returnObject

    def getMatchedBuyers(self, api_password, seller_email, upc_product_code):
        if api_password != '' and seller_email != '' and upc_product_code != '':
            sql = '''
            select (tbl_closed_deals.id) as id, 
            (type1_request_id) as type1_request_id, 
            (type2_request_id) as type2_request_id, 
            (tbl_closed_deals.upc_product_code) as upc_product_code, 
            (tbl_closed_deals.seller_email) as seller_email, 
            (tbl_closed_deals.buyer_email) as buyer_email, 
            (type1_type) as type1_type, 
            (type2_type) as type2_type, 
            (type2_type) as type2_type, 
            (type1_negotiation_term) as type1_negotiation_term,  
            (type2_negotiation_term) as type2_negotiation_term,  
            (type1_negotiation_mode) as type1_negotiation_mode, 
            (type1_key) as type1_key, 
            (type2_key) as type2_key, 
            (type2_negotiation_mode) as type2_negotiation_mode, 
            (type1_initial_offer) as type1_initial_offer,  
            (type2_initial_offer) as type2_initial_offer, 
            (type1_negotiation_best_offer) as type1_negotiation_best_offer,
            (type2_negotiation_best_offer) as type2_negotiation_best_offer, 
            (final_amount) as final_amount,  
            (type1_final_amount) as type1_final_amount, 
            (type2_final_amount) as type2_final_amount, 
            (matched_quantity) as matched_quantity, 
            (type1_result) as type1_result, 
            (type2_result) as type2_result, 
            (comment) as comment, 
            (tbl_closed_deals.created_at) as created_at,  
            (tbl_closed_deals.updated_at) as updated_at
            
            from tbl_closed_deals
            
            join tbl_products on (tbl_closed_deals.upc_product_code = tbl_products.upc_product_code)
            join tbl_buyer_offers on (tbl_products.upc_product_code = tbl_buyer_offers.upc_product_code)
            join tbl_service_requests on (tbl_service_requests.id = tbl_buyer_offers.id)
            
            where tbl_service_requests.api_password = '{}' and 
            tbl_closed_deals.seller_email = '{}' and
            tbl_products.upc_product_code =  '{}'  
            
            '''.format(api_password, seller_email, upc_product_code)

        elif api_password != '' and seller_email != '' and upc_product_code == '':
            sql = '''
            select (tbl_closed_deals.id) as id, 
            (type1_request_id) as type1_request_id, 
            (type2_request_id) as type2_request_id, 
            (tbl_closed_deals.upc_product_code) as upc_product_code, 
            (tbl_closed_deals.seller_email) as seller_email, 
            (tbl_closed_deals.buyer_email) as buyer_email, 
            (type1_type) as type1_type, 
            (type2_type) as type2_type, 
            (type2_type) as type2_type, 
            (type1_negotiation_term) as type1_negotiation_term,  
            (type2_negotiation_term) as type2_negotiation_term,  
            (type1_negotiation_mode) as type1_negotiation_mode, 
            (type1_key) as type1_key, 
            (type2_key) as type2_key, 
            (type2_negotiation_mode) as type2_negotiation_mode, 
            (type1_initial_offer) as type1_initial_offer,  
            (type2_initial_offer) as type2_initial_offer, 
            (type1_negotiation_best_offer) as type1_negotiation_best_offer,
            (type2_negotiation_best_offer) as type2_negotiation_best_offer, 
            (final_amount) as final_amount,  
            (type1_final_amount) as type1_final_amount, 
            (type2_final_amount) as type2_final_amount, 
            (matched_quantity) as matched_quantity, 
            (type1_result) as type1_result, 
            (type2_result) as type2_result, 
            (comment) as comment, 
            (tbl_closed_deals.created_at) as created_at,  
            (tbl_closed_deals.updated_at) as updated_at

            from tbl_closed_deals

            join tbl_products on (tbl_closed_deals.upc_product_code = tbl_products.upc_product_code)
            join tbl_buyer_offers on (tbl_products.upc_product_code = tbl_buyer_offers.upc_product_code)
            join tbl_service_requests on (tbl_service_requests.id = tbl_buyer_offers.id)

            where tbl_service_requests.api_password = '{}' and
            tbl_closed_deals.seller_email = '{}'
            
            '''.format(api_password, seller_email)

        elif api_password != '' and seller_email == '' and upc_product_code == '':
            sql = '''
            select (tbl_closed_deals.id) as id, 
            (type1_request_id) as type1_request_id, 
            (type2_request_id) as type2_request_id, 
            (tbl_closed_deals.upc_product_code) as upc_product_code, 
            (tbl_closed_deals.seller_email) as seller_email, 
            (tbl_closed_deals.buyer_email) as buyer_email, 
            (type1_type) as type1_type, 
            (type2_type) as type2_type, 
            (type2_type) as type2_type, 
            (type1_negotiation_term) as type1_negotiation_term,  
            (type2_negotiation_term) as type2_negotiation_term,  
            (type1_negotiation_mode) as type1_negotiation_mode, 
            (type1_key) as type1_key, 
            (type2_key) as type2_key, 
            (type2_negotiation_mode) as type2_negotiation_mode, 
            (type1_initial_offer) as type1_initial_offer,  
            (type2_initial_offer) as type2_initial_offer, 
            (type1_negotiation_best_offer) as type1_negotiation_best_offer,
            (type2_negotiation_best_offer) as type2_negotiation_best_offer, 
            (final_amount) as final_amount,  
            (type1_final_amount) as type1_final_amount, 
            (type2_final_amount) as type2_final_amount, 
            (matched_quantity) as matched_quantity, 
            (type1_result) as type1_result, 
            (type2_result) as type2_result, 
            (comment) as comment, 
            (tbl_closed_deals.created_at) as created_at,  
            (tbl_closed_deals.updated_at) as updated_at

            from tbl_closed_deals

            join tbl_products on (tbl_closed_deals.upc_product_code = tbl_products.upc_product_code)
            join tbl_buyer_offers on (tbl_products.upc_product_code = tbl_buyer_offers.upc_product_code)
            join tbl_service_requests on (tbl_service_requests.id = tbl_buyer_offers.id)

            where tbl_service_requests.api_password = '{}'
            
            '''.format(api_password)

        else:
            returnObject = {'success': 'false'}
            return returnObject

        results = pd.read_sql_query(sql, self.myDB)
        returnObject = {
                        'success': 'true',
                        'total_offers': int(len(results.index)),
                        'data': []
                        }

        for i in range(0, len(results)):
            lineObject = {'id': int(results.iloc[i]['id']),
                          'type1_request_id': int(results.iloc[i]['type1_request_id']),
                          'type2_request_id': int(results.iloc[i]['type2_request_id']),
                          'upc_product_code': str(results.iloc[i]['upc_product_code']),
                          'seller_email': str(results.iloc[i]['seller_email']),
                          'buyer_email': str(results.iloc[i]['buyer_email']),
                          'type1_type': str(results.iloc[i]['type1_type']),
                          'type2_type': str(results.iloc[i]['type2_type']),
                          'type1_key': str(results.iloc[i]['type1_key']),
                          'type2_key': str(results.iloc[i]['type2_key']),
                          'type1_negotiation_term': str(results.iloc[i]['type1_negotiation_term']),
                          'type2_negotiation_term': str(results.iloc[i]['type2_negotiation_term']),
                          'type1_negotiation_mode': str(results.iloc[i]['type1_negotiation_mode']),
                          'type2_negotiation_mode': str(results.iloc[i]['type2_negotiation_mode']),
                          'type1_initial_offer': float(results.iloc[i]['type1_initial_offer']),
                          'type2_initial_offer': float(results.iloc[i]['type2_initial_offer']),
                          'type1_negotiation_best_offer': float(results.iloc[i]['type1_negotiation_best_offer']),
                          'type2_negotiation_best_offer': float(results.iloc[i]['type2_negotiation_best_offer']),
                          'final_amount': float(results.iloc[i]['final_amount']),
                          'type1_final_amount': float(results.iloc[i]['type1_final_amount']),
                          'type2_final_amount': float(results.iloc[i]['type2_final_amount']),
                          'matched_quantity': float(results.iloc[i]['matched_quantity']),
                          'type1_result': float(results.iloc[i]['type1_result']),
                          'type2_result': float(results.iloc[i]['type2_result']),
                          'comment': str(results.iloc[i]['comment']), 'created_at': str(results.iloc[i]['created_at']),
                          'updated_at': str(results.iloc[i]['updated_at'])}
            returnObject['data'].append(lineObject)

        return returnObject

    def getMatchedBuyersDetails(self, api_password, seller_email, upc_product_code):
        sql = '''
        SELECT DISTINCT tbl_closed_deals.buyer_email 
        
        FROM tbl_closed_deals
        join tbl_buyer_offers on (tbl_closed_deals.upc_product_code = tbl_buyer_offers.upc_product_code)
        join tbl_service_requests on (tbl_service_requests.id = tbl_buyer_offers.id)
            
        where tbl_service_requests.api_password = '{}' and 
        tbl_closed_deals.seller_email = '{}' and
        tbl_closed_deals.upc_product_code =  '{}'  
            
        '''.format(api_password, seller_email, upc_product_code)
     
        results = pd.read_sql_query(sql, self.myDB)
        buyerEmailList = results['buyer_email'].tolist()
        buyerEmails = tuple(buyerEmailList)

        if not buyerEmails:
            returnObject = {
                            'success': 'false',
                            'total_offers': 0,
                            'data': []
                            }
        else:     
            sql = '''
            SELECT *
            FROM tbl_buyers
            WHERE email_id IN {}
            '''.format(buyerEmails)

            results = pd.read_sql_query(sql, self.myDB)
            returnObject = {
                            'success': 'true',
                            'total_offers': int(len(results.index)),
                            'data': []
                            }
            
            for i in range(0, len(results)):
                lineObject = {'first_name': str(results.iloc[i]['first_name']),
                              'last_name': str(results.iloc[i]['last_name']),
                              'email_id': str(results.iloc[i]['email_id']),
                              'contact_number': str(results.iloc[i]['contact_number']),
                              'annual_income': str(results.iloc[i]['annual_income']),
                              'state': str(results.iloc[i]['state']),
                              'country': str(results.iloc[i]['country']),
                              'zip': str(results.iloc[i]['zip']),
                              }
                returnObject['data'].append(lineObject)

        return returnObject
        
    def getBuyerData(self, buyer_email):
        sql = '''
        SELECT min(buyer_orignal_quantity) as min_qty, max(buyer_orignal_quantity) as max_qty, min(buyer_offer_price) as min_price, max(buyer_offer_price) as max_price, avg(buyer_offer_price) as ave_price, coalesce(min(buyer_highest_offer_price),0) as min_offer, coalesce(max(buyer_highest_offer_price),0) as max_offer , coalesce(avg(buyer_highest_offer_price),0) as ave_offer , month(min(tbl_buyer_offers.created_at)) as month, coalesce(max(final_amount),-1)>0 as closed_deal
        FROM tbl_buyer_offers
        left join tbl_closed_deals on (type2_request_id = tbl_buyer_offers.id)
        where tbl_buyer_offers.buyer_email = "{}"
        group by tbl_buyer_offers.upc_product_code
        '''.format(buyer_email)

        results = pd.read_sql_query(sql, self.myDB)

        return results

    def getSellerData(self, seller_email):
        sql = '''
        SELECT min(seller_orignal_quantity) as min_qty, max(seller_orignal_quantity) as max_qty, min(seller_deal_price) as min_price, max(seller_deal_price) as max_price, coalesce(min(seller_lowest_deal_price),0) as min_deal, coalesce(max(seller_lowest_deal_price),0) as max_deal,coalesce(avg(seller_lowest_deal_price),0) as ave_deal, month(min(tbl_seller_deals.created_at)) as month, coalesce(max(final_amount),-1)>0 as closed_deal 
        FROM tbl_seller_deals 
        left join tbl_closed_deals on (type1_request_id = tbl_seller_deals.id) 
        where tbl_seller_deals.seller_email = "{}"
        group by tbl_seller_deals.upc_product_code
        '''.format(seller_email)

        results = pd.read_sql_query(sql, self.myDB)

        return results

    def getProductData(self):
        sql = '''
        SELECT category, parameter1, parameter2, parameter3, parameter4, parameter5,  coalesce((final_amount),-1)>0 as closed_deal 
        FROM tbl_products
        left join tbl_closed_deals on (tbl_products.upc_product_code = tbl_closed_deals.upc_product_code)
        '''

        results = pd.read_sql_query(sql, self.myDB)

        return results

    def getSellerRequestData(self, seller_email, upc_product_code):
        sql = '''
        SELECT min(seller_orignal_quantity) as min_qty, max(seller_orignal_quantity) as max_qty, min(seller_deal_price) as min_price, max(seller_deal_price) as max_price, coalesce(min(seller_lowest_deal_price),0) as min_deal, coalesce(max(seller_lowest_deal_price),0) as max_deal,coalesce(avg(seller_lowest_deal_price),0) as ave_deal, month(min(tbl_seller_deals.created_at)) as month
        FROM tbl_seller_deals 
        where tbl_seller_deals.seller_email = "{}"  and upc_product_code = "{}"
        group by tbl_seller_deals.upc_product_code
        '''.format(seller_email, upc_product_code)

        results = pd.read_sql_query(sql, self.myDB)

        return results

    def getBuyerRequestData(self, buyer_email, upc_product_code):
        sql = '''
        SELECT min(buyer_orignal_quantity) as min_qty, max(buyer_orignal_quantity) as max_qty, min(buyer_offer_price) as min_price, max(buyer_offer_price) as max_price, avg(buyer_offer_price) as ave_price, coalesce(min(buyer_highest_offer_price),0) as min_offer, coalesce(max(buyer_highest_offer_price),0) as max_offer , coalesce(avg(buyer_highest_offer_price),0) as ave_offer , month(min(tbl_buyer_offers.created_at)) as month
        FROM tbl_buyer_offers
        where tbl_buyer_offers.buyer_email = "{}" and upc_product_code = "{}"
        group by tbl_buyer_offers.upc_product_code
        '''.format(buyer_email, upc_product_code)

        results = pd.read_sql_query(sql, self.myDB)

        return results

    def getProductRequestData(self, upc_product_code):
        sql = '''
        SELECT category, parameter1, parameter2, parameter3, parameter4, parameter5
        FROM tbl_products
        where upc_product_code = "{}"
        '''.format(upc_product_code)

        results = pd.read_sql_query(sql, self.myDB)

        return results

    def query(self, sql_statement):
        sql = sql_statement

        results = pd.read_sql_query(sql, self.myDB)

        return results


if __name__ == '__main__':
    dbObject = DBConnect()
    # dbObject.getDeals()
    dbObject.getBuyer('buyer2@robonegotiator.com')
