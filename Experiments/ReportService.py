import jinja2
import pdfkit
from Database.dbconnect import DBConnect
import pandas as pd
import os
import config

class ReportService:
	def __init__(self, start_date, end_date, seller_email='', upc_product_code=''):
		self.upc_product_code = upc_product_code
		if config.configDict['wkhtmltopdfDirectory'] != '':
			wkhtmltopdfDirectory = '/opt/wkhtmltox/bin/wkhtmltopdf'
			self.config = pdfkit.configuration(wkhtmltopdf=wkhtmltopdfDirectory)
		self.seller_email = seller_email
		self.start_date = start_date
		self.end_date = end_date
		self.db = DBConnect().myDB
		self.options={	'dpi':400, 
					'page-size': 'Letter',
					'margin-top': '0.75in',
					'margin-right': '0.75in',
					'margin-bottom': '0.75in',
					'margin-left': '0.75in',
					'orientation': 'landscape',
					'footer-center' : 'Page [page] of [topage] Pages', 
					'footer-font-name': 'Roboto',
					'footer-font-size': '10',
				}
		self.cHandler = self.db.cursor()
		self.templateLoader = jinja2.FileSystemLoader(searchpath="./ReportService/html_template")
		self.templateEnv = jinja2.Environment(loader=self.templateLoader)
		self.TEMPLATE_FILE = "report_template"
		self.template = self.templateEnv.get_template(self.TEMPLATE_FILE)

		sellerInfoSQL= '''
		select concat(first_name, ' ', last_name) as name, email_id as email, contact_number as contact
		from tbl_sellers
		where email_id ="{}"
		'''.format(self.seller_email)
		self.cHandler.execute(sellerInfoSQL)
		self.sellerInfo = self.cHandler.fetchone()
		self.sqlQuery = '';
		self.reportType = '';

	def getReport(self, report_name):

		if (self.sqlQuery != ''):
			df = pd.read_sql_query(self.sqlQuery, self.db)

			conf = {}
			conf['sellerName']= self.sellerInfo[0]
			conf['sellerEmail']= self.sellerInfo[1]
			conf['sellerPhone']= self.sellerInfo[2]
			conf['startDate']= self.start_date
			conf['endDate']= self.end_date
			conf['totalProducts']=len(df)
			conf['reportType']=self.reportType
			conf['df']=df
			outputText = self.template.render(conf)

			base_dir = './ReportService/html_template/'
			hashItems = conf['sellerName']+conf['sellerEmail']+conf['sellerPhone']
			name = hash(hashItems)
			base_dir =  base_dir + str(name) + ".html"

			html_file = open(base_dir, 'w')
			html_file.write(outputText)
			html_file.close()

			save_dir = './ReportService/Example PDF/' + str(report_name) + '.pdf'

			if config.configDict['wkhtmltopdfDirectory'] != '':
				pdf = pdfkit.from_file(base_dir, save_dir, options=self.options, configuration=self.config)
			else:
				pdf = pdfkit.from_file(base_dir, save_dir, options=self.options)
			
			os.remove(base_dir)
			
			return pdf, str(report_name) + '.pdf'
		else:
			print('No SQL Command is selected')


	def getDealSummary(self):
		dealSQL = '''
		select tbl_seller_deals.upc_product_code as `Product ID`,
		tbl_products.parameter1 as `Param 1`,
		tbl_products.parameter2 as `Param 2`,
		tbl_products.title as `Title`,
		format(tbl_seller_deals.seller_orignal_quantity,0) as `Original Quantity`,
		format(tbl_seller_deals.seller_remaining_quantity,0) as `Remaining Quantity`,
		date(tbl_seller_deals.created_at) as `Created At`,
		format(tbl_seller_deals.seller_deal_price,2) as `Deal Price`,
		format(tbl_seller_deals.seller_lowest_deal_price,2) as `Lowest Price`,
		case 
			when tbl_service_requests.status = 2 Then "Full Match"
			when tbl_service_requests.status = 1 Then "Partial Match"
			when tbl_service_requests.status = 0 Then "No Match"
		end  as `Status`
		from tbl_seller_deals
		inner join tbl_products on ( tbl_seller_deals.upc_product_code=tbl_products.upc_product_code)
		inner join tbl_service_requests on (tbl_seller_deals.id =  tbl_service_requests.id)
		where tbl_seller_deals.seller_email = '{}'  and
		STR_TO_DATE(tbl_seller_deals.created_at, '%Y-%m-%d ') between STR_TO_DATE('{}' , '%Y-%m-%d ')  and STR_TO_DATE('{}' , '%Y-%m-%d')
		'''.format(self.seller_email,self.start_date, self.end_date)

		self.sqlQuery = dealSQL
		self.reportType = 'Deal Summary'

	def getOfferSummary(self):
		offerSQL = '''
		Select  tbl_buyer_offers.upc_product_code as `Product Code`,
		tbl_buyer_offers.id as `Offer ID`,
		tbl_buyer_offers.buyer_email as `Buyer Email`,
		tbl_buyer_offers.buyer_phone as `Buyer Phone`,
		format(tbl_buyer_offers.buyer_orignal_quantity,0) as `Original Quantity`,
		format(tbl_buyer_offers.buyer_remaining_quantity,0) as `Remaining Quantity`,
		date(tbl_buyer_offers.created_at) as `Created At`,
		format(tbl_buyer_offers.buyer_highest_offer_price,2) as `Highest Price`,
		format(tbl_buyer_offers.buyer_offer_price,2) as `Lowest Price`,
		case 
				when tbl_service_requests.status = 2 Then "Full Match"
				when tbl_service_requests.status = 1 Then "Partial Match"
				when tbl_service_requests.status = 0 Then "No Match"
		end  as `Status`
		from tbl_buyer_offers
		inner join tbl_service_requests on (tbl_buyer_offers.id = tbl_service_requests.id)
		where tbl_buyer_offers.upc_product_code = '{}'  and
		STR_TO_DATE(tbl_buyer_offers.created_at, '%Y-%m-%d ') between STR_TO_DATE('{}' , '%Y-%m-%d ')  and STR_TO_DATE('{}' , '%Y-%m-%d')
		'''.format(self.upc_product_code,self.start_date, self.end_date)


		self.sqlQuery = offerSQL
		self.reportType = 'Offers Summary by Product ID'


	def getSuccess(self):
		successSQL = '''
		select  tbl_closed_deals.upc_product_code as `Product Code`, 
		tbl_closed_deals.type1_request_id as `Offer ID`,
		tbl_closed_deals.buyer_email as `Buyer Email`,
		tbl_buyer_offers.buyer_phone as `Buyer Phone`,
		tbl_closed_deals.matched_quantity as `Matched Quantity`,
		date(tbl_closed_deals.created_at) as `Date Received`,
		format(tbl_closed_deals.final_amount,2) as `Final Price`,
		format(tbl_closed_deals.total_discounted_amount,2) as `Discounts/Rebates`
		from tbl_closed_deals
		inner join tbl_buyer_offers on (tbl_closed_deals.type2_request_id=tbl_buyer_offers.id)
		where tbl_closed_deals.seller_email = '{}'  and
		STR_TO_DATE(tbl_closed_deals.created_at, '%Y-%m-%d ') between STR_TO_DATE('{}' , '%Y-%m-%d ')  and STR_TO_DATE('{}' , '%Y-%m-%d')
		'''.format(self.seller_email,self.start_date, self.end_date)

		self.sqlQuery = successSQL
		self.reportType = 'Successful Negotiations Summary Report'
