import csv
import requests
import json
import re
from bs4 import BeautifulSoup

# input: UHS-hardware.com SKU number
# output: 'info' = {'SKU','price','count','FCC ID','Chip','Emergency','Frequency','Batery','Test Key','img_link','product_link'}
def SKUtoCSV(SKU, **kwargs):
    # init
    info = {}
    HOME = 'https://www.uhs-hardware.com'
    API_URL = 'https://www.searchserverapi.com/getwidgets'

    # get product link
    params = {
            'api_key': '4F2k7T3h6y',
            'q': SKU,
            'maxResults': '1',
            'output': 'json'
        }
    page = requests.post(API_URL, data=params)
    page_json = page.json()
    try:    # is anything found?
        product_URL = HOME + page_json['items'][0]['link']
    except IndexError:
        return 'OOS'

    # get soup
    page = requests.get(product_URL)
    soup = BeautifulSoup(page.content, "html.parser")
    elements = soup.find("ul", class_="product-sku-collection").find_all("li")

    # selected correct one?
    info['SKU'] = soup.find('span',id='sku').text
    if info['SKU'] != SKU:
        return 'OOS'

    # adjust if it is a multi-pack
    if not kwargs:
        info['price'] = soup.find('div',class_='detail-price').get('content')
        info['count'] = 1
        if info['SKU'][1] == 'x':
            info['count'] = int(info['SKU'][0])      # extract num in multipack
            info['SKU'] = info['SKU'][2:] # remove count from SKU
            info['price'] = str(round(float(info['price']) / info['count'],2))
    else:
        info['price'] = kwargs['p']
        info['count'] = kwargs['q']

    # extract remaining info
    keys_to_extract = {'FCC ID','Chip','Emergency','Frequency','Battery','Test Key'}
    for it in elements:
        line = it.text
        for key in keys_to_extract:
            if key in line:
                value = line.split(':')[1].strip() if ':' in line else re.search(r'[\d\.]+', line).group(0)
                info[key] = value
                    
    #*********************** set all output variables ***********************#
        
    info['img_link'] = HOME + page_json['items'][0]['image_link']
    info['product_link'] = product_URL

    print('outputting to CSV...')
    outputToCSV(info)
    print('done')

def outputToCSV(info_values):
        csv_out = open('invoice_output.csv', mode='a', newline='')
        print('opened to CSV...')
        csv_writer = csv.writer(csv_out)
        csv_writer.writerow([
             '',
             '',
             info_values.get('inv_count', 'n/a'),
             '',
             1,
             info_values.get('type', 'n/a'),
             info_values.get('on_van', '1'),
             info_values.get('on_base', '1'),
             info_values.get('SKU', 'n/a'), 
             info_values.get('Chip', 'n/a'), 
             info_values.get('FCC ID', 'n/a'), 
             info_values.get('Emergency', 'n/a'), 
             info_values.get('Frequency', 'n/a'), 
             info_values.get('total_sold', 'n/a'), 
             info_values.get('price', 'n/a'), 
             info_values.get('avg_sale', 'n/a'), 
             info_values.get('img', 'n/a'), 
             info_values.get('total_value', 'n/a'),
             info_values.get('link', 'n/a')]
             )
