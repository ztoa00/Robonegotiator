import os
config_path = os.path.dirname(os.path.abspath(__file__))
# print(config_path)


#Local Instance
configLocalDict={}
configLocalDict['customerPath'] = '/var/www/ai.robonegotiator.online/testcutomerdata.csv'
configLocalDict['dealPath'] =  '/var/www/ai.robonegotiator.online/mapped_deal_customers.csv'
configLocalDict['csvToSql'] = 1
configLocalDict['host'] = 'localhost'
configLocalDict['port'] = 3306
configLocalDict['user'] = 'root'
configLocalDict['passwd'] = '123'
configLocalDict['database'] = 'dev_base'
configLocalDict['getMostCommonDemographics'] = 'http://mi.robonegotiator.com/api/api/getMostCommonDemographics'
configLocalDict['wkhtmltopdfDirectory'] =''


#Production instance 
configProdDict={}
configProdDict['customerPath'] = '/var/www/mi.robonegotiator.online/testcutomerdata.csv'
configProdDict['dealPath'] =  '/var/www/mi.robonegotiator.online/mapped_deal_customers.csv'
configProdDict['csvToSql'] = 1
configProdDict['host'] = '209.126.3.200'
configProdDict['port'] = 3306
configProdDict['user'] = 'beta_user'
configProdDict['passwd'] = 'cEe8dcSSd84dHH012'
configProdDict['database'] = 'beta_base'
configProdDict['getMostCommonDemographics'] = 'http://mi.robonegotiator.com/api/api/getMostCommonDemographics'
configProdDict['wkhtmltopdfDirectory'] ='a'

configDict = configLocalDict # choose between configLocalDict or configProdDict

#Scrapper Db
configScrapperDict={}
configScrapperDict['host'] = 'localhost'
configScrapperDict['port'] = 3306
configScrapperDict['user'] = 'root'
configScrapperDict['passwd'] = 'root'
configScrapperDict['database'] = 'db_market'
