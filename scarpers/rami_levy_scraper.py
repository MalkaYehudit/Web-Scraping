import requests
from models.product import Product
from base_scraper import StoreScraper

class RamiLeviScraper(StoreScraper):
    def __init__(self):
        super().__init__("https://www.rami-levy.co.il/api/catalog")

    def scrape_product(self, product_name):
        payload = {
            "q": product_name,
            "store": 331
        }
        headers = {
            "User-Agent": "Mozilla/5.0",
            "Content-Type": "application/json",
            "Referer": "https://www.rami-levy.co.il/he/online/market",
            "Origin": "https://www.rami-levy.co.il"
        }

        response = requests.post(self.base_url, json=payload, headers=headers, verify=False)
        print(response.status_code)
        # מחיקת ההדפסה של כל הטקסט כדי לא לקבל את כל הפרטים
        # print(response.text)

        response.raise_for_status()

        data = response.json()
        products = []
        for item in data.get('data', []):
            try:
                name = item.get("internal_product_description") or item.get("name")
                price = float(item.get("price", {}).get("price", 0))
                print(f"{name} - {price} ש\"ח")  # הדפסה ממוקדת
                products.append(Product(name, price, "רמי לוי"))
            except Exception as e:
                print(f"שגיאה: {e}")
        return products
