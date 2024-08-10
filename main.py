from url import urls
from parser import ProductParser
import time
import pandas as pd

if __name__ == '__main__':
    url = urls

    parser = ProductParser()
    parsed_data = []

    for url in urls:
        product_data = parser.parse_product(url)
        parsed_data.append(product_data)
        time.sleep(5)

    parser.quit_driver()

    df = pd.DataFrame(parsed_data)
    df.to_excel('товары.xlsx', index=False)