import requests
from bs4 import BeautifulSoup
from models.product import Product
from scrapers.base_scraper import StoreScraper

class ShufersalScraper(StoreScraper):
    def scrape_product(self, product_name):
        url = f"https://www.shufersal.co.il/online/he/search?text={product_name}"
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'lxml')

        products = []
        for item in soup.select('.product-details'):
            try:
                name = item.select_one('.product-title').text.strip()
                price_text = item.select_one('.price-number').text.strip().replace('₪', '').replace(',', '')
                price = float(price_text)
                products.append(Product(name, price, "שופרסל"))
            except Exception:
                continue

        return products
