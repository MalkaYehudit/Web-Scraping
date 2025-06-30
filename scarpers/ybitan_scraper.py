import requests
import urllib.parse
import json
from typing import List, Optional
from models.product import Product
from scarpers.base_scraper import StoreScraper
from models.quantity_extractor import QuantityExtractor
import time
import random


class YbitanScraper(StoreScraper):
    def __init__(self):
        super().__init__("https://www.ybitan.co.il")
        self.api_base = "https://www.ybitan.co.il/v2"
        self.session = requests.Session()

        # יצירת מופע של חילוץ הכמויות
        self.quantity_extractor = QuantityExtractor()

        # Headers to mimic a real browser
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'he-IL,he;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Referer': 'https://www.ybitan.co.il/',
            'Origin': 'https://www.ybitan.co.il'
        })

        # פרמטרים קבועים לAPI
        self.retailer_id = "1131"
        self.branch_id = "1369"
        self.app_id = "4"
        self.language_id = "1"  # עברית

    def scrape_product(self, product_name):
        """שיטה לשליפת מוצר בודד"""
        return self.search_products(product_name)

    def search_products(self, query: str, max_results: int = 10) -> List[Product]:
        """חיפוש מוצרים באתר יינות ביתן באמצעות API"""
        products = []

        try:
            print(f"מחפש מוצרים עבור: '{query}'")
            encoded_query = urllib.parse.quote(query, safe='')
            api_url = self.build_search_url(encoded_query, size=max_results)
            print(f"API URL: {api_url}")

            self.add_delay()

            response = self.session.get(api_url, timeout=15)
            response.raise_for_status()

            print(f"קוד תגובה: {response.status_code}")
            data = response.json()
            products = self.parse_api_response(data)
            print(f"נמצאו {len(products)} מוצרים")

        except requests.RequestException as e:
            print(f"שגיאה בבקשת API: {e}")
        except json.JSONDecodeError as e:
            print(f"שגיאה בפרסור JSON: {e}")
        except Exception as e:
            print(f"שגיאה כללית: {e}")

        return products

    def build_search_url(self, encoded_query: str, size: int = 10, from_idx: int = 0) -> str:
        """בניית URL לחיפוש במוצרים"""
        filters = {
            "must": {
                "exists": ["family.id", "family.categoriesPaths.id", "branch.regularPrice"],
                "term": {
                    "branch.isActive": True,
                    "branch.isVisible": True
                }
            },
            "mustNot": {
                "term": {
                    "branch.regularPrice": 0,
                    "branch.isOutOfStock": True
                }
            }
        }

        filters_json = json.dumps(filters, separators=(',', ':'))
        encoded_filters = urllib.parse.quote(filters_json, safe='')

        url = (f"{self.api_base}/retailers/{self.retailer_id}/branches/{self.branch_id}/products"
               f"?appId={self.app_id}"
               f"&filters={encoded_filters}"
               f"&from={from_idx}"
               f"&isSearch=true"
               f"&languageId={self.language_id}"
               f"&query={encoded_query}"
               f"&size={size}")

        return url

    def parse_api_response(self, data: dict) -> List[Product]:
        """פרסור תגובת API וחילוץ מוצרים"""
        products = []

        try:
            if 'data' in data and 'products' in data['data']:
                products_data = data['data']['products']
            elif 'products' in data:
                products_data = data['products']
            elif isinstance(data, list):
                products_data = data
            else:
                print("מבנה תגובה לא מוכר")
                print(f"מפתחות בתגובה: {list(data.keys()) if isinstance(data, dict) else 'לא dict'}")
                return products

            print(f"מעבד {len(products_data)} מוצרים מהAPI")

            for item in products_data:
                try:
                    product = self.parse_single_product(item)
                    if product:
                        products.append(product)
                except Exception as e:
                    print(f"שגיאה בעיבוד מוצר: {e}")
                    continue

        except Exception as e:
            print(f"שגיאה בפרסור תגובת API: {e}")

        return products

    def parse_single_product(self, item: dict) -> Optional[Product]:
        """פרסור מוצר בודד מתגובת API"""
        try:
            # חילוץ שם המוצר
            name = self.extract_product_name(item)
            if not name:
                return None

            # חילוץ מחיר
            price = self.extract_price(item)
            if price <= 0:
                print(f"לא נמצא מחיר למוצר: {name}")
                return None

            # חילוץ מותג/יצרן
            brand = self.extract_brand(item)

            # חילוץ כמות באמצעות המחלקה החדשה
            quantity = self.extract_quantity(item, name)

            # יצירת מוצר
            product = Product(
                name=name,
                price=price,
                store="יינות ביתן",
                quantity=quantity,
                brand=brand
            )

            # חישוב מחיר יחסי באמצעות המחלקה החדשה
            if quantity:
                self.quantity_extractor.calculate_unit_price(product)

            return product

        except Exception as e:
            print(f"שגיאה בפרסור מוצר: {e}")
            return None

    def extract_product_name(self, item: dict) -> str:
        """חילוץ שם המוצר"""
        name = ""

        # ניסיון ראשון - localName
        if 'localName' in item and item['localName']:
            name = item['localName']

        # ניסיון שני - names
        elif 'names' in item and item['names']:
            if '1' in item['names']:  # עברית
                if isinstance(item['names']['1'], dict):
                    name = item['names']['1'].get('short', '') or item['names']['1'].get('long', '')
                else:
                    name = str(item['names']['1'])
            elif 'he' in item['names']:
                name = item['names']['he']

        # ניסיון שלישי - name
        elif 'name' in item and item['name']:
            name = item['name']

        # ניסיון רביעי - family name
        elif 'family' in item and item['family'] and 'names' in item['family']:
            if '1' in item['family']['names']:
                name = item['family']['names']['1']

        return name.strip() if name else ""

    def extract_price(self, item: dict) -> float:
        """חילוץ מחיר המוצר"""
        price = 0.0

        # ניסיון ראשון - branch data
        if 'branch' in item and item['branch']:
            branch_data = item['branch']
            if 'regularPrice' in branch_data and branch_data['regularPrice']:
                price = float(branch_data['regularPrice'])
            elif 'price' in branch_data and branch_data['price']:
                price = float(branch_data['price'])
            elif 'currentPrice' in branch_data and branch_data['currentPrice']:
                price = float(branch_data['currentPrice'])

        # ניסיון שני - מחיר ישיר
        if price <= 0:
            for price_field in ['regularPrice', 'price', 'currentPrice']:
                if price_field in item and item[price_field]:
                    try:
                        price = float(item[price_field])
                        if price > 0:
                            break
                    except (ValueError, TypeError):
                        continue

        return price

    def extract_brand(self, item: dict) -> str:
        """חילוץ מותג/יצרן"""
        brand = ""

        # ניסיון ראשון - brand object
        if 'brand' in item and item['brand']:
            brand_data = item['brand']
            if isinstance(brand_data, dict):
                if 'names' in brand_data and '1' in brand_data['names']:
                    brand = brand_data['names']['1']
                elif 'name' in brand_data:
                    brand = brand_data['name']
            elif isinstance(brand_data, str):
                brand = brand_data

        # ניסיון שני - manufacturer
        elif 'manufacturer' in item and item['manufacturer']:
            manufacturer_data = item['manufacturer']
            if isinstance(manufacturer_data, dict):
                if 'names' in manufacturer_data and '1' in manufacturer_data['names']:
                    brand = manufacturer_data['names']['1']
                elif 'name' in manufacturer_data:
                    brand = manufacturer_data['name']
            elif isinstance(manufacturer_data, str):
                brand = manufacturer_data

        return brand.strip() if brand else ""

    def extract_quantity(self, item: dict, product_name: str) -> str:
        """
        חילוץ כמות המוצר באמצעות המחלקה המשותפת
        """
        # ניסיון חילוץ מהשדות
        weight = item.get('weight')
        unit_of_measure = None

        # חילוץ יחידת מידה
        if 'unitOfMeasure' in item and item['unitOfMeasure']:
            unit_data = item['unitOfMeasure']
            if isinstance(unit_data, dict):
                if 'names' in unit_data and '1' in unit_data['names']:
                    unit_of_measure = unit_data['names']['1']
                elif 'name' in unit_data:
                    unit_of_measure = unit_data['name']
                else:
                    unit_of_measure = str(unit_data)
            else:
                unit_of_measure = str(unit_data)

        quantity_field = item.get('quantity')
        size_field = item.get('size')

        # ניסיון חילוץ מהשדות
        quantity = self.quantity_extractor.extract_quantity_from_fields(
            weight=weight,
            unit_of_measure=unit_of_measure,
            quantity_field=quantity_field,
            size_field=size_field
        )

        # אם לא נמצא בשדות, נחפש בשם המוצר
        if not quantity:
            quantity = self.quantity_extractor.extract_quantity_from_name(product_name)

        return quantity

    def get_product_data_for_db(self, product: Product) -> dict:
        """
        הכנת נתוני המוצר עבור מסד הנתונים

        Returns:
            dict: נתונים מסודרים עבור הטבלה
        """
        weight, weight_unit = self.quantity_extractor.get_weight_and_unit_for_db(product.quantity)

        return {
            'name': product.name[:50],  # הגבלת אורך לפי הטבלה
            'description': f"{product.name} - {product.store}",
            'brand_id': None,  # יש לקשר עם טבלת המותגים
            'weight': weight,
            'weight_unit': weight_unit,
            'price': product.price,
            'unit_price': getattr(product, 'unit_price', None),
            'unit_type': getattr(product, 'unit_type', None),
            'store': product.store
        }

    def get_branch_info(self) -> dict:
        """קבלת מידע על הסניף"""
        try:
            url = f"{self.api_base}/retailers/{self.retailer_id}/branches"
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"שגיאה בקבלת מידע סניפים: {e}")
            return {}

    def add_delay(self):
        """הוספת עיכוב אקראי למניעת חסימה"""
        time.sleep(random.uniform(1.0, 2.5))