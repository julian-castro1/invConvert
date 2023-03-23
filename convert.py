# input:
#   UHS_SKU, count, type, $per
# output: 
#   inv_ID, inv_count, type, on_van, on_base, UHS_SKU, chip_ID, FCC_ID, blade_ID, freq, total_sold, avg_cost, avg_sale, img, total_value

import csv
import requests
import re
from bs4 import BeautifulSoup

# open and read the current inventory file

# navigate to the uhs-hardware.com page for the SKU#
URL = "https://www.uhs-hardware.com/products/2019-2022-nissan-altima-sentra-5-button-smart-key-pn-285e3-6ca6a-kr5txn4-aftermarket?rq=mk_nissan~md_altima~yr_2021"

#****************** AT THE SKU# PAGE ******************#
# get all page info
page = requests.get(URL)
soup = BeautifulSoup(page.content, "html.parser")

# narrow down the request
info = soup.find("ul", class_="product-sku-collection")
raw = info.find_all("li")

# extract info
info_values = {}
info_values['SKU'] = soup.find('span',id='sku').text
info_values['price'] = soup.find('div',class_='detail-price').get('content')

keys_to_extract = {'FCC ID','Chip','FCC ID','Emergency','Frequency'}
for it in raw:
    line = it.text
    for key in keys_to_extract:
        if key in line:
            value = line.split(':')[1].strip() if ':' in line else re.search(r'[\d\.]+', line).group(0)
            info_values[key] = value
            
print(info_values)
    

# with open('input.csv', 'r') as input_file, \
#      open('output_file.csv', 'w', newline='') as output_file:
#     reader = csv.DictReader(input_file)
#     writer = csv.writer(output_file)
#     for row in reader:
#         writer.writerow([row['uhs_SKU']])