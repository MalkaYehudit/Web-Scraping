import requests
from models.product import Product
from base_scraper import StoreScraper


class VictoryScraper(StoreScraper):
    def __init__(self):
        super().__init__("https://www.victoryonline.co.il/v2/retailers/1470/branches/2331/products")

    def scrape_product(self, product_name):
        params = {
            "appId": 4,
            "filters": '{"must":{"exists":["family.id","family.categoriesPaths.id","branch.regularPrice"],"term":{"branch.isActive":true,"branch.isVisible":true}},"mustNot":{"term":{"branch.regularPrice":0,"branch.isOutOfStock":true}}}',
            "from": 0,
            "isSearch": "true",
            "languageId": 1,
            "query": product_name,
            "size": 16
        }

        headers = {
            "User-Agent": "Mozilla/5.0",
            "Referer": "https://www.victoryonline.co.il/",
        }

        response = requests.get(self.base_url, params=params, headers=headers, verify=False)
        response.raise_for_status()

        data = response.json()

        # לנסות לשלוף את המוצרים מה-JSON במקומות שונים, לפי המבנה שהראית
        items = data.get("items") or data.get("data", {}).get("items", [])

        if not items:
            print("לא נמצאו מוצרים.")
            return []

        products = []
        for item in items:
            # להשיג שם מוצר (מקומי / עברית)
            name = item.get("localName") or item.get("names", {}).get("2", {}).get("short")
            price = item.get("branch", {}).get("regularPrice", 0)

            if name and price:
                print(f"{name} - ויקטורי")
                products.append(Product(name, price, "ויקטורי"))

        return products



