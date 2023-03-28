import pdfplumber
import re
from SKUtoInfo import SKUtoCSV


def extract_order_info(pdf_text: str):
    # Define regex patterns for the order number, SKU lines, and prices
    order_number_pattern = r'#(\d{7})'
    sku_lines_pattern = r'(\d+)\s+([A-Za-z0-9\-]+)\s+\$([\d.]+)'
    price_pattern = r'\$([\d.]+)'
    quantities_pattern = r'(\d+)\s+[A-Za-z0-9\-]+\s+\$[\d.]+'
    rates_pattern = r'\d+\s+[A-Za-z0-9\-]+\s+\$([\d.]+)'

    # Find the order number, SKU lines, and prices using the regex patterns
    order_number = re.search(order_number_pattern, pdf_text)
    sku_lines = re.findall(sku_lines_pattern, pdf_text)
    prices = re.findall(price_pattern, pdf_text)
    quantities = re.findall(quantities_pattern, pdf_text)
    rates = re.findall(rates_pattern, pdf_text)

    # Extract the matched values
    order_number = order_number.group(1) if order_number else None

    # Extract SKU numbers from the SKU lines
    sku_numbers = [sku for _, sku, _ in sku_lines]

    return order_number, sku_numbers, rates, quantities

if __name__ == '__main__':
    pdf_text = '''
    ... # The extracted text from the PDF you provided
    '''

    order_number, sku_numbers, prices, qty = extract_order_info(pdf_text)


def extract_text_from_pdf(pdf_file_path):
    with pdfplumber.open(pdf_file_path) as pdf:
        all_text = []
        for page in pdf.pages:
            page_text = page.extract_text()
            all_text.append(page_text)

    return '\n'.join(all_text)

if __name__ == '__main__':
    pdf_file_path = '/Users/julian/Downloads/Invoice_INV1020594900653.8_1679953994348.pdf'
    pdf_text = extract_text_from_pdf(pdf_file_path)

    order_number, sku_numbers, prices, qty = extract_order_info(pdf_text)

    print('calling SKUtoCSV')
    for i in range(len(sku_numbers)):
        SKUtoCSV(sku_numbers[i], p=prices[i], q=qty[i])