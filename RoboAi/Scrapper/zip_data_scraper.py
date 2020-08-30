import requests
import json
from Database.dbscrapper import DBScrapperConnect
 

def scrapeZip():
    zip= 90123
    while zip <99999:
        base_url= "https://www.truecar.com/abp/api/geographic/locations/"
        url = base_url + str(zip)

        try:
            response = json.loads(requests.get(url).content)

            response['dma_id']

            db = DBScrapperConnect()

            db.insertZipTrueCar(zip=response['postal_code'],city= response['city'],state=response['state'],county=response['county'] ,lon=response['lon'] ,lat=response['lat'], timezone=response['timezone'], slug= response['slug'])
        except: 
            print("No Data")
        
        print(zip)
        zip+=1
        