import requests
from models.product import Product
from scrapers.base_scraper import StoreScraper

class HaziHinamScraper(StoreScraper):
    def __init__(self):
        super().__init__("https://shop.hazi-hinam.co.il")

    def scrape_product(self, product_name):
        url = f"{self.base_url}/proxy/api/item/getItemsBySearch"
        headers = {
            'User-Agent': 'Mozilla/5.0',
            'Content-Type': 'application/json'
        }

        all_products = []
        page = 1
        page_size = 50

        while True:
            payload = {
                "StoreId": 1,
                "Page": page,
                "PageSize": page_size,
                "SearchText": product_name,
                "CategoryId": None,
                "SubCategoryId": None
            }

            try:
                response = requests.post(url, headers=headers, json=payload)
                response.raise_for_status()
                data = response.json()
                items = data.get("Items", [])

                if not items:
                    break

                for item in items:
                    try:
                        name = item.get("Name", "ללא שם")
                        price = item.get("Price_NET", 0)
                        all_products.append(Product(name, price, "חצי חינם"))
                    except Exception:
                        continue

                page += 1

            except Exception:
                break

        return all_products
