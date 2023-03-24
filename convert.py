# input:
#   UHS_SKU, count, type, $per
# output: 
#   inv_ID, inv_count, type, on_van, on_base, UHS_SKU, chip_ID, FCC_ID, blade_ID, freq, total_sold, avg_cost, avg_sale, img, total_value

import csv
import requests
import json
import re
from bs4 import BeautifulSoup

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
    'only_smart' : 120
}

#***************************** inputs **********************************#
INPUTS = {'type' : 'combo'}

#*************** open and read the current inventory file **************#

#**** search UHS-hardware.com with SKU# to get info and product url ****#
HOME = 'https://www.uhs-hardware.com'
API_URL = 'https://www.searchserverapi.com/getwidgets'
SKU = 'RK-FD-404'


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


#*************************** AT THE SKU# PAGE ***************************#

product_URL = HOME + page_json['items'][0]['link']

# get all page info
page = requests.get(product_URL)
soup = BeautifulSoup(page.content, "html.parser")

# narrow down the request
# info = soup.find("ul", class_="product-sku-collection")
raw_data_ele = soup.find("ul", class_="product-sku-collection").find_all("li")

# extract SKU and price
info_values = {}
info_values['SKU'] = soup.find('span',id='sku').text
info_values['price'] = soup.find('div',class_='detail-price').get('content')

# if its a multipack, adjust pricing
is_multi_pack = info_values['SKU'][1] == 'x'
if is_multi_pack:
    keysCount = int(info_values['SKU'][0])      # extract num in multipack
    info_values['SKU'] = info_values['SKU'][2:] # remove count from SKU
    info_values['price'] = str(round(float(info_values['price']) / keysCount,2))

"""
Things to add:
- add support for out of stock items
"""

# extract remaining info
keys_to_extract = {'FCC ID','Chip','FCC ID','Emergency','Frequency','Battery','Test Key'}
for it in raw_data_ele:
    line = it.text
    for key in keys_to_extract:
        if key in line:
            value = line.split(':')[1].strip() if ':' in line else re.search(r'[\d\.]+', line).group(0)
            info_values[key] = value
            

#*********************** set all output variables ***********************#

count = 0
inv_count = 0

info_values['on_van'] = 1
info_values['on_base'] = 0
info_values['inv_ID'] = count
info_values['inv_count'] = inv_count
info_values['total_sold'] = 0
info_values['avg_cost'] = page_json['items'][0]['price']
info_values['img_link'] = HOME + page_json['items'][0]['image_link']
info_values['total_value'] = info_values['avg_cost'] * info_values['inv_count']
info_values['product_link'] = HOME + page_json['items'][0]['link']
info_values['type'] = INPUTS['type']
info_values['avg_sale'] = PRODUCT_TYPES[info_values['type']]


for val in info_values:
    print(str(val) + ' : ' + str(info_values[val]))

# with open('input.csv', 'r') as input_file, \
#      open('output_file.csv', 'w', newline='') as output_file:
#     reader = csv.DictReader(input_file)
#     writer = csv.writer(output_file)
#     for row in reader:
#         writer.writerow([row['uhs_SKU']])
