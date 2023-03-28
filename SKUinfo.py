# input:
#   UHS_SKU, count, type
# output: 
#   inv_ID, inv_count, type, on_van, on_base, UHS_SKU, chip_ID, FCC_ID, blade_ID, freq, total_sold, avg_cost, avg_sale, img, total_value

import csv
import requests
import json
import re
from bs4 import BeautifulSoup


def SKUtoInfo(SKU):
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
    info_values['price'] = soup.find('div',class_='detail-price').get('content')
    info['count'] = 1
    if info_values['SKU'][1] == 'x':
        info['count'] = int(info_values['SKU'][0])      # extract num in multipack
        info['SKU'] = info_values['SKU'][2:] # remove count from SKU
        info['price'] = str(round(float(info_values['price']) / keysCount,2))
    
    # extract remaining info
    keys_to_extract = {'FCC ID','Chip','FCC ID','Emergency','Frequency','Battery','Test Key'}
    for it in elements:
        line = it.text
        for key in keys_to_extract:
            if key in line:
                value = line.split(':')[1].strip() if ':' in line else re.search(r'[\d\.]+', line).group(0)
                info[key] = value
                    
    #*********************** set all output variables ***********************#
        
    info['img_link'] = HOME + page_json['items'][0]['image_link']
    info['product_link'] = HOME + page_json['items'][0]['link']
    info['link'] = product_URL

    return info


#**************************** init *************************************#
PRODUCT_TYPES = {
    'transponder' : 80,
    'metal' : 60,
    'smart' : 160,
    'combo' : 120,
    'flip' : 120,
    'remote' : 60,
    'battery' : 5,
    'shell' : 80,
    'chip' : 40,
    'only_blade' : 40,
    'only_smart' : 120,
    'fobik' : 120
}

csv_out = open('SKUinfo-output.csv', mode='w', newline='')
csv_writer = csv.writer(csv_out)

#***************************** inputs **********************************#
INPUTS = {}

with open('SKU_input.csv', newline='') as csvfile:
    reader = csv.reader(csvfile)
    for item in reader:
        INPUTS['SKU'] = item[0]     # uhs_SKU
        INPUTS['count'] = item[1]   # quantity
        INPUTS['type'] = item[2]    # type

        #************** search UHS-hardware.com with SKU# to get info and product url **************#
        HOME = 'https://www.uhs-hardware.com'
        API_URL = 'https://www.searchserverapi.com/getwidgets'
        SKU = INPUTS['SKU']
        # The data to be sent with the POST request
        params = {
            'api_key': '4F2k7T3h6y',
            'q': SKU,
            'maxResults': '1',
            'output': 'json'
        }
        # Getting data as JSON
        page = requests.post(API_URL, data=params)
        page_json = page.json()

        # if its out of stock cant get any info, write what is known with the OOS flag

        #*************************** AT THE SKU# PAGE ***************************#
                # if its out of stock cant get any info, write what is known with the OOS flag
        try:
            product_URL = HOME + page_json['items'][0]['link']
        except IndexError:
            csv_writer.writerow([INPUTS['inv_id'],'x',INPUTS['SKU'],INPUTS['count']])
            continue

        # get all page info
        page = requests.get(product_URL)
        soup = BeautifulSoup(page.content, "html.parser")
        # narrow down the request
        # info = soup.find("ul", class_="product-sku-collection")
        raw_data_ele = soup.find("ul", class_="product-sku-collection").find_all("li")
        # extract SKU and price
        info_values = {}
        info_values['SKU'] = soup.find('span',id='sku').text
        if info_values['SKU'] != INPUTS['SKU']:
            csv_writer.writerow(['','x',INPUTS['SKU'],INPUTS['count']])
            continue

        info_values['price'] = soup.find('div',class_='detail-price').get('content')
        # if its a multipack, adjust pricing
        is_multi_pack = info_values['SKU'][1] == 'x'
        if is_multi_pack:
            keysCount = int(info_values['SKU'][0])      # extract num in multipack
            info_values['SKU'] = info_values['SKU'][2:] # remove count from SKU
            info_values['price'] = str(round(float(info_values['price']) / keysCount,2))
        # extract remaining info
        keys_to_extract = {'FCC ID','Chip','FCC ID','Emergency','Frequency','Battery','Test Key'}
        for it in raw_data_ele:
            line = it.text
            for key in keys_to_extract:
                if key in line:
                    value = line.split(':')[1].strip() if ':' in line else re.search(r'[\d\.]+', line).group(0)
                    info_values[key] = value
                    
        #*********************** set all output variables ***********************#
        
        info_values['on_van'] = INPUTS['count']
        info_values['on_base'] = 0
        info_values['inv_count'] = INPUTS['count']
        info_values['total_sold'] = 0
        info_values['img_link'] = HOME + page_json['items'][0]['image_link']
        info_values['total_value'] = float(info_values['price']) * int(info_values['inv_count'])
        info_values['product_link'] = HOME + page_json['items'][0]['link']
        info_values['type'] = INPUTS['type']
        info_values['avg_sale'] = PRODUCT_TYPES[info_values['type']]
        info_values['link'] = product_URL

# inv_ID	OOS	inv_count	optimal	min	type	on_van	on_base	UHS_SKU	chip_ID	fcc_id	blade_ID	freq	total_sold	avg_cost	avg_sale	img	total_value	link
        csv_writer.writerow(
            ['',
             '',
             info_values.get('inv_count', 'n/a'),
             '',
             1,
             info_values.get('type', 'n/a'),
             info_values.get('on_van', 'n/a'),
             info_values.get('on_base', 'n/a'),
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
             info_values.get('link', 'n/a')])


csv_out.close()