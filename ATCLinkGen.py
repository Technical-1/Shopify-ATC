import requests
import json

def getProducts(site):
    headers={'cache-control': 'no-store'}
    r3 = requests.get(site, headers=headers)
    products = json.loads((r3.text))['products']
    return products

def main(link):
    products = getProducts(link + '/products.json?limit=250')
    for product in products:
        print('\n')
        print(product['title'])
        print(link + '/collections/frontpage/products/' + product['handle'])
        for x in range(0, len(product['variants'])):
            if ((((product['variants'])[x])['available'])==True):
                print(((product['variants'])[x])['title'])
                #print(((product['variants'])[x])['id'])
                print(link + '/cart/add?id=' + str(((product['variants'])[x])['id']) + '&quantity=1')

site = input('What site do you want ATC links?')
if (site == '1'):
    site = 'https://marketmarketmarket.com'
    
try:
    main(site);
except:
  print("An exception occurred")
