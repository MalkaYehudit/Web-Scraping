import requests
from models.product import Product
from scarpers.base_scraper import StoreScraper
import json


class VictoryScraper(StoreScraper):
    def __init__(self):
        super().__init__("https://www.victoryonline.co.il")

    def scrape_product(self, product_name):
        url = f"{self.base_url}/v2/retailers/1470/branches/2331/products"

        filters_dict = {
            "must": {
                "exists": ["family.id", "family.categoriesPaths.id", "branch.regularPrice"],
                "term": {"branch.isActive": True, "branch.isVisible": True}
            },
            "mustNot": {
                "term": {"branch.regularPrice": 0, "branch.isOutOfStock": True}
            }
        }

        params = {
            "appId": 4,
            "size": 16,
            "languageId": 1,
            "isSearch": "true",
            "from": 0,
            "filters": json.dumps(filters_dict),  # encode filters as JSON string
            "query": product_name  # ללא quote
        }

        headers = {
            "User-Agent": "Mozilla/5.0",
            "Accept": "application/json"
        }

        try:
            response = requests.get(url, params=params, headers=headers, verify=False)
            print("Final URL:", response.url)  # הדפסת ה-URL הסופי לבדיקה

            if response.status_code != 200:
                print(f"❌ שגיאה בבקשה ל-Victory: {response.status_code}")
                return []

            data = response.json()
            raw_products = data.get("hits", [])
        except Exception as e:
            print("❌ שגיאה בבקשה או בניתוח JSON:", e)
            return []

        products = []
        for item in raw_products:
            try:
                name = item["name"]
                price = float(item["branch"]["regularPrice"])
                products.append(Product(name, price, "ויקטורי"))
            except Exception:
                continue

        return products
