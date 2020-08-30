from flask import *
import io
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

sys.path.append(os.getcwd())  # there is a bug in the werkzeug reloader
from CustomerProfile.SellerProfile import SellerProfile as SP
from CustomerProfile.BuyerProfile import BuyerProfile as BP
from DealIntelligence.dealIntelligence import DealIntelligence
from DemographicsIntelligence.demographicsIntelligence import DemographicsIntelligence
from MostCommonDemographics.mostCommonDemographics import MostCommonDemographics
from BuyerProfile.buyerProfile import BuyerProfile
from MotivatedBuyer.motivatedBuyer import isMotivatedBuyer
from flask_restplus import Api, Resource, reqparse
from flasgger import Swagger
from Database.dbconnect import DBConnect
from MarketIntelligence.MarketIntelligence import MarketIntelligence
from AI.AI import AI
from ReportService.ReportService import ReportService
import logging
from datetime import datetime

# from flask_bootstrap import Bootstrap

# from scipy.cluster.hierarchy import ward, fcluster, leaders,leaves_list,median, maxdists,dendrogram, linkage
# from scipy.spatial.distance import pdist

application = Flask(__name__)

application.secret_key = "super secret key"
application.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

Swagger(application)

if __name__ != '__main__':
    gunicorn_logger = logging.getLogger('gunicorn.error')
    application.logger.handlers = gunicorn_logger.handlers
    application.logger.setLevel(gunicorn_logger.level)


@application.route('/', methods=['GET'])
def index():
    return "AI Server Is Up"


@application.route('/api/getSellerProfile', methods=['POST'])
def getSellerProfile():
    """

    Call this api passing the seller_email to get back statistics of that seller like how average, minimum, maximum and
    all its percentage increase rate from listed price to deal price.If seller_email does not exist return an object
    with 0 values as output.

    ---
    tags:
    - Seller Profile
    parameters:
    - name: seller_email
      in: formData
    type: string
    required: true
    description: Unique key for seller
    responses:
    500:
      description: Error seller_email not found!
    200:
      description: Success!

    """

    try:
        seller_email = request.form['seller_email']
        try:
            sp = SP(seller_email)
            return jsonify(
                email_id=sp.SellerEmail,
                seller_minimum_increase=int(sp.SellerMinimumIncrease),
                seller_maximum_increase=int(sp.SellerMaximumIncrease),
                seller_average_increase=int(sp.SellerAverageIncrease),
                seller_minimum_increase_percentage=int(sp.SellerMinimumIncreasePercentage),
                seller_maximum_increase_percentage=int(sp.SellerMaximumIncreasePercentage),
                seller_average_increase_percentage=int(sp.SellerAverageIncreasePercentage)
            ), 200
        except:
            return jsonify(
                email_id=seller_email,
                seller_minimum_increase=0,
                seller_maximum_increase=0,
                seller_average_increase=0,
                seller_minimum_increase_percentage=0,
                seller_maximum_increase_percentage=0,
                seller_average_increase_percentage=0
            ), 500
    except:
        return jsonify(
            seller_minimum_increase=0,
            seller_maximum_increase=0,
            seller_average_increase=0,
            seller_minimum_increase_percentage=0,
            seller_maximum_increase_percentage=0,
            seller_average_increase_percentage=0
        ), 500


@application.route('/api/getBuyerProfile', methods=['POST'])
def getBuyerProfile():
    """

    Call this api passing the buyer_email to get back statistics of that buyer like how average, minimum, maximum
    and its percentage decrease rate from highest price to deal price. If buyer email not exist return an object
    with 0 values as output.

    ---
    tags:
    - Buyer Profile
    parameters:
    - name:buyer_email
     in: formData
    type: string
    required: true
    description: Unique key for buyer
    responses:
    500:
     description: Error buyer_email not found!
    200:
     description: Success!

    """

    try:
        buyer_email = request.form['buyer_email']
        try:
            bp = BP(buyer_email)
            return jsonify(
                email_id=bp.BuyerEmail,
                buyer_minimum_decrease=int(bp.BuyerMinimumDecrease),
                buyer_maximum_decrease=int(bp.BuyerMaximumDecrease),
                buyer_average_decrease=int(bp.BuyerAverageDecrease),
                buyer_minimum_decrease_percentage=int(bp.BuyerMinimumDecreasePercentage),
                buyer_maximum_decrease_percentage=int(bp.BuyerMaximumDecreasePercentage),
                buyer_average_decrease_percentage=int(bp.BuyerAverageDecreasePercentage)
            ), 200
        except:
            return jsonify(
                email_id=buyer_email,
                buyer_minimum_increase=0,
                buyer_maximum_increase=0,
                buyer_average_increase=0,
                buyer_minimum_decrease_percentage=0,
                buyer_maximum_decrease_percentage=0,
                buyer_average_decrease_percentage=0
            ), 500
    except:
        return jsonify(
            buyer_minimum_increase=0,
            buyer_maximum_increase=0,
            buyer_average_increase=0,
            buyer_minimum_decrease_percentage=0,
            buyer_maximum_decrease_percentage=0,
            buyer_average_decrease_percentage=0
        ), 500


@application.route('/api/getMatchedBuyersDetails', methods=['POST'])
def getMatchedBuyersDetails():
    """

    Call this api passing the api_password, seller_email, upc_product_code to get back details of buyers
    whose offers deals have fully matched and partially matched. 
    
    ---
    tags:
     - Buyers Details
    parameters:
      - name: seller_email
        in: formData
        type: string
        required: true
        description: Unique key for seller
      - name: UPC_Product_Code
        in: formData
        type: string
        required: true
        description: Unique key for product
      - name: api_password
        in: formData
        type: string
        required: true
        description: Unique key for every Client
    responses:
     500:
       description: Error!
     200:
       description: Success!

    """
    if request.method == 'POST':
        if request.form.get('api_password'):
            api_password = request.form['api_password']
            upc_product_code = str(request.form['upc_product_code'])
            seller_email = str(request.form['seller_email'])

            try:
                dbConnect = DBConnect()
                matchedBuyers = dbConnect.getMatchedBuyersDetails(api_password=api_password,
                                                                  seller_email=seller_email,
                                                                  upc_product_code=upc_product_code)
                return matchedBuyers, 200

            except:
                matchedBuyers = {'success': 'false', 'data': []}
                return matchedBuyers, 500

        else:
            matchedBuyers = {'success': 'false', 'data': []}
            return matchedBuyers, 500


@application.route('/inputToDealIntelligence', methods=['GET'])
def inputToDealIntelligence():
    return render_template('sellerConfigurationDealSegments.html')


'''Module for deal intelligence'''


@application.route('/api/getDealIntelligence', methods=['POST'])
def getDealIntelligence():
    """
    This is the Robonegotiator AI modules API
    Call this api passing  upc_product_code and get back its historical deal intelligence.
    K-means is used for deal segmentation in order to classify deal as Pro-buyer,Neutral
    or Pro-seller.In this case value of K is set as 3 and input features are: 
    1.seller_segmentation_parameter = seller_listed_price - seller_deal_price
    2.buyer_segmentation_parameter = buyer_highest_offer - seller_deal_price
    Lower values of these parameters indicates Pro-Seller deals while higher values indicates
    Pro-buyer deals
    If upc_product_code doesnt exist total deals=0 is given as output
    ---
    tags:
      - Historical Deal Intelligence
    parameters:
      - name: UPC_Product_Code
        in: formData
        type: string
        required: true
        description: Unique key for product
    responses:
      500:
        description: Error upc_product_code not found!
      200:
        description: Success!
        
    """

    if request.method == 'POST':
        if (request.form.get('UPC_Product_Code')):
            UPC_Product_Code = request.form['UPC_Product_Code']

    try:
        DealIntelligenceObject = DealIntelligence(str(UPC_Product_Code))
        return jsonify(ProSellerProducts=int(DealIntelligenceObject.ProSellerProducts), \
                       ProBuyerProducts=int(DealIntelligenceObject.ProBuyerProducts), \
                       NeutralProducts=int(DealIntelligenceObject.NeutralProducts), \
                       total=int(DealIntelligenceObject.total),
                       UPC_Product_Code=DealIntelligenceObject.UPC_Product_Code, \
                       pro_buyer_mean_S_Deal=float(DealIntelligenceObject.pro_buyer_mean_S_Deal), \
                       pro_buyer_output=float(DealIntelligenceObject.pro_buyer_output), \
                       pro_seller_mean_S_Deal=float(DealIntelligenceObject.pro_seller_mean_S_Deal), \
                       pro_seller_output=float(DealIntelligenceObject.pro_seller_output), \
                       neutral_mean_S_Deal=float(DealIntelligenceObject.neutral_mean_S_Deal), \
                       master_average=float(DealIntelligenceObject.master_average)), 200
    except:
        return jsonify(total_Deals=0), 500


@application.route('/inputToGetHighestInEachDemographics', methods=['GET'])
def inputToGetHighestInEachDemographics():
    return render_template('sellerConfigurationCustomerSegments.html')


'''Module for getting attribute highest in each demographic parameter'''


@application.route('/api/getHighestInEachDemographics', methods=['POST'])
def getHighestInEachDemographics():
    """
    This is the Robonegotiator AI modules API
    Call this api passing upc_product_code and get back highest demographic attribute value for 
    each demographic parameter from historical deals.For given upc_product_code get all deals from
    tbl_master_deals .Get demographics details of corresponding buyers for all the deals from
    tbl_buyers.Find maximum common value for each demographic attribute(race,age,annual_income,sex)
    for fetched demographic details.If upc_product_code doesnt exist total deals=0 is given as 
    output
    
    ---
    tags:
      - Highest in each demographic attribute
    parameters:
      - name: UPC_Product_Code
        in: formData
        type: string
        required: true
        description: Unique key for product
    responses:
      500:
        description: Error upc_product_code not found!
      200:
        description: Success!
        
    """

    if request.method == 'POST':
        if (request.form.get('UPC_Product_Code')):
            UPC_Product_Code = request.form['UPC_Product_Code']

    try:
        HighestInEachDemographics = DemographicsIntelligence(UPC_Product_Code)

        return jsonify(parameter1=HighestInEachDemographics.parameter1, \
                       max_param1=HighestInEachDemographics.max_param1, \
                       max_param1_count=int(HighestInEachDemographics.max_param1_count), \
                       parameter2=HighestInEachDemographics.parameter2, \
                       max_param2=HighestInEachDemographics.max_param2, \
                       max_param2_count=int(HighestInEachDemographics.max_param2_count), \
                       parameter3=HighestInEachDemographics.parameter3, \
                       max_param3=HighestInEachDemographics.max_param3, \
                       max_param3_count=int(HighestInEachDemographics.max_param3_count), \
                       parameter4=HighestInEachDemographics.parameter4, \
                       max_param4=HighestInEachDemographics.max_param4, \
                       max_param4_count=int(HighestInEachDemographics.max_param4_count), \
                       total=int(HighestInEachDemographics.Buyer_Email.shape[0]), \
                       demographics=HighestInEachDemographics.demographics), 200
    except:
        return jsonify(total_Deals=0), 500


@application.route('/inputToGetMostCommonDemographics', methods=['GET'])
def inputToGetMostCommonDemographics():
    return render_template('mostCommonDemographicsInput.html')


'''Module for most getting top two common demographics'''


@application.route('/api/getMostCommonDemographics', methods=['POST'])
def getMostCommonDemographics():
    """
    This is the Robonegotiator AI modules API
    Call this api passing upc_product_code and get back most common demographic attribute value/value range
    for demographic parameters from historical deals.For given upc_product_code get all deals from 
    tbl_master_deals .Get demographics details of corresponding buyers
    (mapplicationing:buyer_email in tbl_master_deals is equivalent to email_id in tbl_buyers) for all the 
    deals from tbl_buyers.Map race,annual_income,age to numeric values .Sort  demographics parameters
    according to standard deviation of numeric values of race,annual_income,age .Get two parameters/
    (three parameters if race has least standard deviation in comparision to annual_income and age) 
    ith values having least standard deviation. Find minimum and maximum values for those parameters .
    Map those values back to original form. Return count of records with values matching the range 
    specified by minimum and maximum values of two/three parameters with least standard deviation and
    calculate percentage for same.If upc_product_code doesnt exist total deals=0 is given as output.
    
    ---
    tags:
      - Most common demographic attributes
    parameters:
      - name: UPC_Product_Code
        in: formData
        type: string
        required: true
        description: Unique key for product
    responses:
      500:
        description: Error upc_product_code not found!
      200:
        description: Success!
        
    """
    if request.method == 'POST':
        if (request.form.get('UPC_Product_Code')):
            UPC_Product_Code = request.form['UPC_Product_Code']

    try:
        mostCommonDemographicsObject = MostCommonDemographics(str(UPC_Product_Code))

        if hasattr(mostCommonDemographicsObject, 'parameter4_value'):
            # print("parameter4_value",mostCommonDemographics.parameter4_value,"parameter4",mostCommonDemographics.parameter4)
            return jsonify(UPC_Product_Code=mostCommonDemographicsObject.UPC_Product_Code, \
                           top_2_param_percentage_distribution=float(
                               mostCommonDemographicsObject.top_2_param_percentage_distribution), \
                           parameter1=mostCommonDemographicsObject.parameter1, \
                           parameter1_value=mostCommonDemographicsObject.parameter1_value, \
                           parameter2=mostCommonDemographicsObject.parameter2, \
                           parameter2_value=mostCommonDemographicsObject.parameter2_value,
                           parameter3=mostCommonDemographicsObject.parameter3, \
                           parameter3_value=mostCommonDemographicsObject.parameter3_value, \
                           parameter4=mostCommonDemographicsObject.parameter4, \
                           parameter4_value=mostCommonDemographicsObject.parameter4_value), 200

        return jsonify(UPC_Product_Code=mostCommonDemographicsObject.UPC_Product_Code, \
                       top_2_param_percentage_distribution=float(
                           mostCommonDemographicsObject.top_2_param_percentage_distribution), \
                       parameter1=mostCommonDemographicsObject.parameter1, \
                       parameter1_value=mostCommonDemographicsObject.parameter1_value, \
                       parameter2=mostCommonDemographicsObject.parameter2, \
                       parameter2_value=mostCommonDemographicsObject.parameter2_value,
                       parameter3=mostCommonDemographicsObject.parameter3, \
                       parameter3_value=mostCommonDemographicsObject.parameter3_value), 200
    except:
        return jsonify(total_Deals=0), 500


@application.route('/customerProfile', methods=['GET'])
def customerProfile():
    return render_template('customerProfile.html')


'''Module for buyer profile'''


@application.route('/api/getCustomerProfile', methods=['POST'])
def getCustomerProfile():
    """
    This is the Robonegotiator AI modules API
    Call this api passing buyer_email and get back how much on average,minimum and maximum the 
    buyer has gone up while negotiations in past.Also get the distribution of final_deal_status from
    past deals of buyer.For given buyer specified by Buyer_Email=buyer_email in tbl_master_deals
    find all the deals he is involved in .Sort  deals on difference between seller_deal_price and
    buyer_offer. Minimum percentage is given by difference between seller_deal_price and buyer_offer
    divided by seller_deal_price of the first record,maximum percentage is given by seller_deal_price 
    and buyer_offer  divided by buyer_offer  of the last record,average percentage is given by 
    difference between mean seller_deal_price and mean buyer_offer divided by mean buyer_offer 
    calculated through all records for that buyer.If buyer is involved only in one deal then 
    average_percentage_increase,maximum_percentage_increase and minimum_percentage_increase is
    not shown.If buyer_email does not exist total deals=0 is given as output.

    ---
    tags:
      - Buyer Profile
    parameters:
      - name: Buyer_Email
        in: formData
        type: string
        required: true
        description: Unique key for buyer
    responses:
      500:
        description: Error upc_product_code not found!
      200:
        description: Success!
        
    """
    if request.method == 'POST':
        if (request.form.get('Buyer_Email')):
            Buyer_Email = request.form['Buyer_Email']
            # Buyer_Id=float(Buyer_Id)
    try:
        customerProfileObject = BuyerProfile(str(Buyer_Email))
        if customerProfileObject.total_Deals == 1:
            return jsonify(total_Deals=customerProfileObject.total_Deals, \
                           NotMatching=customerProfileObject.NotMatching, \
                           FullyMatched=customerProfileObject.FullyMatched, \
                           # AbortedInMiddle=customerProfileObject.AbortedInMiddle)
                           PartialMatched=customerProfileObject.PartialMatched, \
                           InNegotiation=customerProfileObject.InNegotiation), 200
        else:
            return jsonify(average_percentage_increase=float(customerProfileObject.average_percentage_increase), \
                           minimum_percentage_increase=float(customerProfileObject.minimum_percentage_increase), \
                           Buyer_Email=customerProfileObject.Buyer_Email, \
                           maximum_percentage_increase=float(customerProfileObject.maximum_percentage_increase), \
                           total_Deals=customerProfileObject.total_Deals, \
                           NotMatching=customerProfileObject.NotMatching, \
                           FullyMatched=customerProfileObject.FullyMatched, \
                           # AbortedInMiddle=customerProfileObject.AbortedInMiddle)
                           PartialMatched=customerProfileObject.PartialMatched, \
                           InNegotiation=customerProfileObject.InNegotiation), 200
    except:
        return jsonify(total_Deals=0), 500


@application.route('/motivated', methods=['GET'])
def motivated():
    return render_template('motivated.html')


@application.route('/api/getMotivatedMatchingParameters', methods=['POST'])
def getMotivatedMatchingParameters():
    """
    This is the Robonegotiator AI modules API
    Call this api passing buyer_email and upc_product_code to get back number of most common demographic attributes
    that are matching for given buyer.This module makes implicit call to /getMostCommonDemographics and compares the
    demographics  with that of given buyer.If buyer_email or upc_product_code does not exist total deals=0 is given
    as output.

    ---
    tags:
      - Motivated Buyer
    parameters:
      - name: Buyer_Email
        in: formData
        type: string
        required: true
        description: Unique key for buyer
      - name: UPC_Product_Code
        in: formData
        type: string
        required: true
        description: Unique key for product  
    responses:
      500:
        description: Error upc_product_code/buyer_email not found!
      200:
        description: Success!
        
    """
    if request.method == 'POST':
        if (request.form.get('Buyer_Email')):
            Buyer_Email = request.form['Buyer_Email']
            # Buyer_Id=float(Buyer_Id)
        if (request.form.get('UPC_Product_Code')):
            UPC_Product_Code = request.form['UPC_Product_Code']
        # print(Buyer_Email,UPC_Product_Code)

    try:
        motivatedBuyerObject = isMotivatedBuyer(Buyer_Email, UPC_Product_Code)
        motivatedBuyerObject.getCommonAttributes(UPC_Product_Code)
        # print(motivatedBuyerObject.__dict__)
        return jsonify(commonParameters=motivatedBuyerObject.common), 200
    except:
        return jsonify(total_Deals=0), 500


@application.route('/inputToGetHistoricalData', methods=['GET'])
def historical():
    return render_template('historicalData.html')


@application.route('/api/getHistoricalData', methods=['POST'])
def getHistoricalData():
    """
    This is the Robonegotiator ML modules API
    Call this api passing the upc_product_code to get back statistics on closed deals.
    that are matching for given buyer.If buyer_email or upc_product_code does not exist return an object with 0 values.
    as output.

    ---
    tags:
      - Closed Deals
    parameters:
      - name: UPC_Product_Code
        in: formData
        type: string
        required: true
        description: Unique key for product
    responses:
      500:
        description: Error upc_product_code not found!
      200:
        description: Success!

    """
    if request.method == 'POST':
        if (request.form.get('UPC_Product_Code')):
            UPC_Product_Code = request.form['UPC_Product_Code']
        # print(Buyer_Email,UPC_Product_Code)

    try:
        dbConnect = DBConnect()
        historicalData = dbConnect.getHistoricalData(upc_product_code=UPC_Product_Code)
        # print(motivatedBuyerObject.__dict__)
        return historicalData, 200

    except:
        historicalData = {}
        historicalData['AverageClosedDeals'] = 0
        historicalData['TotalCount'] = 0
        historicalData['TotalQuantity'] = 0
        return historicalData, 500


@application.route('/inputToProductOffersData', methods=['GET'])
def productOffers():
    return render_template('productOffersData.html')


@application.route('/business/analytic/products/offers', methods=['POST'])
def getProductOfferslData():
    if request.method == 'POST':
        if request.form.get('api_password'):
            api_password = str(request.form['api_password'])
            seller_email = str(request.form['seller_email'])
            upc_product_code = str(request.form['upc_product_code'])

            try:
                dbConnect = DBConnect()
                productOffers = dbConnect.getProductOffersData(api_password=api_password,
                                                               seller_email=seller_email,
                                                               upc_product_code=upc_product_code)
                return productOffers, 200

            except:
                productOffers = {'success': 'false', 'data': []}
                return productOffers, 500

        else:
            productOffers = {'success': 'false', 'data': []}
            return productOffers, 500


@application.route('/inputToMatchedBuyers', methods=['GET'])
def matchedBuyers():
    return render_template('matchedBuyers.html')


@application.route('/api/business/analytic/products/matched/buyers', methods=['POST'])
def getMatchedBuyers():
    if request.method == 'POST':
        if request.form.get('api_password'):
            api_password = request.form['api_password']
            upc_product_code = str(request.form['upc_product_code'])
            seller_email = str(request.form['seller_email'])

            try:
                dbConnect = DBConnect()
                matchedBuyers = dbConnect.getMatchedBuyers(api_password=api_password,
                                                           seller_email=seller_email,
                                                           upc_product_code=upc_product_code)
                return matchedBuyers, 200

            except:
                matchedBuyers = {'success': 'false', 'data': []}
                return matchedBuyers, 500

        else:
            matchedBuyers = {'success': 'false', 'data': []}
            return matchedBuyers, 500


@application.route('/inputMarketData', methods=['GET'])
def marketDataTmpl():
    return render_template('marketData.html')


@application.route('/api/market/statistics', methods=['POST'])
def getMarketData():
    if request.method == 'POST':
        if (request.form.get('upc_product_code')):
            upc_product_code = str(request.form['upc_product_code'])
            zip_code = str(request.form['zip_code'])
        if (upc_product_code == '' or zip_code == ''):
            marketData = {}
            marketData['success'] = 'false'
            return marketData, 500
    try:

        market = MarketIntelligence(upc_product_code, zip_code)

        return market.getMarketStatistic(), 200

    except:
        marketData = {}
        marketData['success'] = 'false'
        return marketData, 500


@application.route('/inputAIPrediction', methods=['GET'])
def aiPredictionTmpl():
    return render_template('AIPrediction.html')


@application.route('/api/ai/prediction', methods=['POST'])
def getAIPrediction():
    if request.method == 'POST':
        if (request.form.get('upc_product_code')):
            upc_product_code = str(request.form['upc_product_code'])
            api_password = str(request.form['api_password'])
            seller_email = str(request.form['seller_email'])
            buyer_email = str(request.form['buyer_email'])
        if (upc_product_code == '' or api_password == '' or seller_email == '' or buyer_email == ''):
            aiData = {}
            aiData['success'] = 'false'
            aiData['prediction'] = '0'
            return aiData, 500
    try:
        ai = AI(upc_product_code, seller_email, buyer_email, api_password)
        aiData = {}
        aiData['success'] = 'true'
        aiData['prediction'] = ai.predict()

        return aiData, 200

    except:
        aiData = {}
        aiData['success'] = 'false'
        aiData['prediction'] = '0'
        return aiData, 500



@application.route('/inputDealSummary',methods=['GET'])
def dealSummaryTmpl():
    return render_template('dealSummary.html')	

@application.route('/api/ai/dealSummary',methods=['POST'])
def getDealSummary():
    if request.method=='POST':
        if (request.form.get('seller_email')):
            start = str(request.form['start_date'])
            end = str(request.form['end_date'])
            seller_email= str(request.form['seller_email'])
        if (start == '' or end == '' or seller_email == ''):
            returnObject = {}
            returnObject['success'] = 'false'
            return returnObject, 500
    try:
#		from ReportService.ReportService import ReportService
#		seller_email = 'seller1@robonegotiator.com'
#		start = '2020-05-06'
#		end = '2020-07-06'
#		upc_product_code = '2T2ZFMCA2GC001437'
        report = ReportService(start, end,seller_email)
        report.getDealSummary()

        now = datetime.now().strftime("%Y_%m_%d_%H%M%S")
        report_name =  "dealSummary_" + str(now)

        report = report.getReport(report_name)
        returnObject = {}
        returnObject['success'] = report
        response = make_response(returnObject)
        response.headers["Content-Type"] = "applicationlication/pdf"
        response.headers["Content-Disposition"] = "inline; filename=output.pdf"
        return response, 200
    except:
        returnObject = {}
        returnObject['success'] = 'false'
        return returnObject, 500

@application.route('/inputOfferSummaryReport',methods=['GET'])
def offerSummaryTmpl():
    return render_template('offerSummary.html')	

@application.route('/api/ai/offerSummaryReport',methods=['POST'])
def getOfferSummary():
    if request.method=='POST':
        if (request.form.get('seller_email')):
            start = str(request.form['start_date'])
            end = str(request.form['end_date'])
            seller_email= str(request.form['seller_email'])
            upc_product_code = str(request.form['upc_product_code'])
        if (start == '' or end == '' or seller_email == '' or upc_product_code == ''):
            returnObject = {}
            returnObject['success'] = 'false'
            return returnObject, 500
    try:
#		from ReportService.ReportService import ReportService
#		seller_email = 'seller1@robonegotiator.com'
#		start = '2020-05-06'
#		end = '2020-07-06'
#		upc_product_code = '2T2ZFMCA2GC001437'
        report = ReportService(start, end,seller_email,upc_product_code)
        report.getOfferSummary()

        now = datetime.now().strftime("%Y_%m_%d_%H%M%S")
        report_name =  "offerSummary_" + str(now)

        report = report.getReport(report_name)
        returnObject = {}
        returnObject['success'] = report
        response = make_response(returnObject)
        response.headers["Content-Type"] = "applicationlication/pdf"
        response.headers["Content-Disposition"] = "inline; filename=output.pdf"
        return response, 200
    except:
        returnObject = {}
        returnObject['success'] = 'false'
        return returnObject, 500


@application.route('/inputOfferClosedDeal',methods=['GET'])
def offerClosedDealTmpl():
    return render_template('closedDeals.html')	


@application.route('/api/ai/closedDealSummary',methods=['POST'])
def getClosedDealSummary():
    if request.method=='POST':
        if (request.form.get('seller_email')):
            start = str(request.form['start_date'])
            end = str(request.form['end_date'])
            seller_email= str(request.form['seller_email'])
        if (start == '' or end == '' or seller_email == ''):
            returnObject = {}
            returnObject['success'] = 'false'
            return returnObject, 500
    try:
#		from ReportService.ReportService import ReportService
#		seller_email = 'seller1@robonegotiator.com'
#		start = '2020-05-06'
#		end = '2020-07-06'
#		upc_product_code = '2T2ZFMCA2GC001437'
        report = ReportService(start, end,seller_email)
        report.getSuccess()

        now = datetime.now().strftime("%Y_%m_%d_%H%M%S")
        report_name =  "closedDealSummary_" + str(now)

        report = report.getReport(report_name)
        returnObject = {}
        returnObject['success'] = report
        response = make_response(returnObject)
        response.headers["Content-Type"] = "applicationlication/pdf"
        response.headers["Content-Disposition"] = "inline; filename=output.pdf"
        return response, 200
    except:
        returnObject = {}
        returnObject['success'] = 'false'
        return returnObject, 500


if __name__ == '__main__':
    # application.run(debug=True,port=80,host='0.0.0.0')
    application.run(debug=True)
