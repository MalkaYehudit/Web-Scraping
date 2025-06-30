import requests
from bs4 import BeautifulSoup
from models.product import Product
from scarpers.base_scraper import StoreScraper
from models.quantity_extractor import QuantityExtractor
import re
import time


class ShukCityScraper(StoreScraper):
    def __init__(self):
        super().__init__("https://www.shukcity.co.il")
        self.quantity_extractor = QuantityExtractor()

    def scrape_product(self, product_name):
        url = f"{self.base_url}/v2/retailers/1254/branches/1639/products"

        # Headers מתקדמים יותר שמדמים דפדפן אמיתי
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'he-IL,he;q=0.9,en-US;q=0.8,en;q=0.7',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Referer': 'https://www.shukcity.co.il/',
            'Origin': 'https://www.shukcity.co.il',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Ch-Ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
            'Sec-Ch-Ua-Mobile': '?0',
            'Sec-Ch-Ua-Platform': '"Windows"',
            'Cache-Control': 'no-cache',
            'Pragma': 'no-cache'
        }

        # יצירת session לשמירת cookies
        session = requests.Session()
        session.headers.update(headers)

        # ביקור ראשון לעמוד הבית לקבלת cookies
        try:
            print("מבצע ביקור ראשון לאתר...")
            home_response = session.get("https://www.shukcity.co.il/")
            print(f"ביקור בעמוד הבית: {home_response.status_code}")
            time.sleep(2)
        except Exception as e:
            print(f"שגיאה בביקור בעמוד הבית: {e}")

        all_products = []
        size = 10  # שינוי לשליפת 10 תוצאות בלבד
        start = 0
        max_products = 10  # הגבלה על מספר המוצרים הכולל

        while len(all_products) < max_products:
            params = {
                "appId": "4",
                "filters": '{"must":{"exists":["family.id","family.categoriesPaths.id","branch.regularPrice"],"term":{"branch.isActive":true,"branch.isVisible":true}},"mustNot":{"term":{"branch.regularPrice":0,"branch.isOutOfStock":true}}}',
                "from": str(start),
                "languageId": "1",
                "query": product_name,
                "size": str(size)
            }

            try:
                print(f"שולח בקשה עם start={start}, size={size}")
                response = session.get(url, params=params, timeout=10)
                print(f"סטטוס קוד: {response.status_code}")
                print(f"Content-Type: {response.headers.get('content-type', 'לא ידוע')}")

                response.raise_for_status()
                data = response.json()

                print(f"מבנה התשובה: {list(data.keys())}")
                items = data.get("products", [])
                print(f"נמצאו {len(items)} מוצרים בעמוד זה")

                if not items:
                    print("אין עוד מוצרים, יוצא מהלולאה")
                    break

                for i, item in enumerate(items):
                    # בדיקה אם הגענו למספר המוצרים המבוקש
                    if len(all_products) >= max_products:
                        print(f"הגענו ל-{max_products} מוצרים, מפסיק")
                        break

                    try:
                        # חילוץ נתוני המוצר
                        name = self._extract_product_name(item)
                        price = self._extract_price(item)
                        brand = self._extract_brand(item)

                        # חילוץ כמות באמצעות QuantityExtractor
                        quantity = self._extract_quantity_with_extractor(item)

                        # יצירת מוצר
                        product = Product(name, price, "שוק העיר", quantity, brand)

                        # חישוב מחיר יחסי באמצעות QuantityExtractor
                        self.quantity_extractor.calculate_unit_price(product)

                        all_products.append(product)

                    except Exception as e:
                        print(f"שגיאה בעיבוד מוצר {i + 1}: {e}")
                        print(f"נתוני המוצר: {item}")
                        continue

                # בדיקה אם הגענו למספר המוצרים המבוקש
                if len(all_products) >= max_products:
                    print(f"הושלמה שליפת {max_products} מוצרים")
                    break

                start += size
                time.sleep(1.5)

            except requests.exceptions.HTTPError as e:
                if response.status_code == 403:
                    print("האתר חוסם את הבקשה (403 Forbidden)")
                    print("נסה להמתין כמה דקות ולנסות שוב, או להשתמש ב-VPN")
                    break
                else:
                    print(f"שגיאת HTTP: {e}")
                    break
            except requests.exceptions.RequestException as e:
                print(f"שגיאה בבקשת HTTP: {e}")
                break
            except Exception as e:
                print(f"שגיאה כללית: {e}")
                break

        return all_products

    def _extract_quantity_with_extractor(self, item):
        """חילוץ כמות באמצעות QuantityExtractor"""
        # חילוץ נתונים מהשדות
        weight = item.get("weight")
        unit_of_measure_data = item.get("unitOfMeasure", {}).get("names", {}).get("1")
        number_of_items = item.get("numberOfItems")
        size_field = item.get("size")

        # ניסיון ראשון - שימוש בשדות הישירים
        quantity = self.quantity_extractor.extract_quantity_from_fields(
            weight=weight,
            unit_of_measure=unit_of_measure_data,
            quantity_field=number_of_items,
            size_field=size_field
        )

        if quantity:
            return quantity

        # ניסיון שני - חילוץ משם המוצר
        name = self._extract_product_name(item)
        quantity_from_name = self.quantity_extractor.extract_quantity_from_name(name)

        if quantity_from_name:
            return quantity_from_name

        # ניסיון שלישי - בדיקות נוספות ספציפיות לשוק העיר
        return self._extract_quantity_fallback(item)

    def _extract_quantity_fallback(self, item):
        """פונקציה גיבוי לחילוץ כמות - עבור מקרים מיוחדים"""
        # בדיקות נוספות ספציפיות לשוק העיר
        quantity_sources = [
            item.get("original", {}).get("weight"),
            item.get("original", {}).get("size"),
            item.get("volume"),
            item.get("original", {}).get("volume")
        ]

        for quantity in quantity_sources:
            if quantity and str(quantity).strip():
                return str(quantity).strip()

        # בדיקה לmultipack
        number_of_items = item.get("numberOfItems")
        weight = item.get("weight")
        unit_of_measure = item.get("unitOfMeasure", {}).get("names", {}).get("1")

        if number_of_items and number_of_items > 1 and weight and unit_of_measure:
            normalized_unit = self.quantity_extractor.normalize_unit_type(unit_of_measure)
            return f"{number_of_items} יחידות של {weight} {normalized_unit}"

        return None

    def _extract_product_name(self, item):
        """חילוץ שם המוצר"""
        name_sources = [
            item.get("localName"),
            item.get("names", {}).get("1", {}).get("long"),
            item.get("names", {}).get("1", {}).get("short"),
            item.get("original", {}).get("names", {}).get("1", {}).get("long"),
            item.get("original", {}).get("names", {}).get("1", {}).get("short"),
            item.get("name"),
            item.get("description")
        ]

        for name in name_sources:
            if name and name.strip():
                return name.strip()

        return "לא ידוע"

    def _extract_price(self, item):
        """חילוץ מחיר המוצר"""
        try:
            price = item.get("branch", {}).get("regularPrice")
            if price is not None:
                return float(price)
        except (ValueError, TypeError):
            pass

        try:
            price = item.get("price")
            if price is not None:
                return float(price)
        except (ValueError, TypeError):
            pass

        return 0.0

    def _extract_brand(self, item):
        """חילוץ שם היצרן"""
        try:
            brand_data = item.get("brand", {})
            if isinstance(brand_data, dict):
                names_data = brand_data.get("names", {})
                if isinstance(names_data, dict):
                    for lang_id in ["1", "2"]:
                        if lang_id in names_data:
                            brand_name = names_data[lang_id]
                            if isinstance(brand_name, str) and brand_name.strip():
                                return brand_name.strip()

                if "name" in brand_data and brand_data["name"]:
                    brand_name = brand_data["name"]
                    if isinstance(brand_name, str) and brand_name.strip():
                        return brand_name.strip()

        except Exception:
            pass

        # מקורות נוספים ליצרן
        additional_brand_sources = [
            item.get("original", {}).get("brand", {}).get("names", {}).get("1"),
            item.get("original", {}).get("brand", {}).get("names", {}).get("2"),
            item.get("original", {}).get("brand", {}).get("name"),
            item.get("manufacturer"),
            item.get("producer"),
            item.get("supplier", {}).get("name") if isinstance(item.get("supplier"), dict) else None
        ]

        for brand in additional_brand_sources:
            if brand and isinstance(brand, str) and brand.strip():
                return brand.strip()
        #
        # # חילוץ יצרן מהשם באמצעות רשימה מובנית
        # name = self._extract_product_name(item)
        # extracted_brand = self._extract_brand_from_name(name)
        # if extracted_brand:
        #     return extracted_brand

        return None

    # def _extract_brand_from_name(self, name):
    #     """חילוץ יצרן מתוך שם המוצר"""
    #     known_brands = [
    #         "אוסם", "תנובה", "יטבתה", "טעמן", "קוקה קולה", "פפסי",
    #         "נסטלה", "בישולי", "שטראוס", "עלית", "שופרסל", "סוגת",
    #         "מגדים", "אסם", "ברמן", "חרמון", "גלידות שטראוס", "דנונה",
    #         "מאיר בגל", "מעדן", "ויסוצקי", "עלי", "מילקי", "סימפליסימו",
    #         "בן עמי", "זוגלובק", "פיצה האט", "דומינו", "תל אביב", "מוצר ישראלי",
    #         "coca cola", "cocacola", "ספרינג", "פריגת", "ג'אמפ",
    #         "רפאל'ס", "נובי", "פרינוק", "דניאלה", "אקטימל", "יופלה", "פרוט & ווג'",
    #         "פריטוב", "מטרנה", "בייבי ביס", "תנובה אלטרנטיב", "גמדים", "דנונה פרו"
    #     ]
    #
    #     name_lower = name.lower()
    #     for brand in known_brands:
    #         if brand.lower() in name_lower:
    #             return brand
    #
    #     return None