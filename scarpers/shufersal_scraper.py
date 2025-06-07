
import requests
from bs4 import BeautifulSoup
from models.product import Product
from base_scraper import StoreScraper
class ShufersalScraper(StoreScraper):
    def __init__(self):
        super().__init__("https://www.shufersal.co.il")

    def scrape_product(self, product_name):


        url = f"{self.base_url}/online/he/search?text={product_name}"
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers, verify=False)
        # verify = certifi.where()
        soup = BeautifulSoup(response.text, 'lxml')

        products = []
        for item in soup.select('li.SEARCH.tileBlock.miglog-prod.miglog-sellingmethod-by_unit'):
            try:
                name = item['data-product-name']
                price = float(item['data-product-price'])
                products.append(Product(name, price, "שופרסל"))
            except Exception:
                continue
        return products

