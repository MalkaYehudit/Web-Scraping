import requests
from bs4 import BeautifulSoup
from models.product import Product
from scrapers.base_scraper import StoreScraper
import re


class ShukCityScraper(StoreScraper):
    def __init__(self):
        super().__init__("https://www.shukcity.co.il")

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

            # המתנה קטנה
            import time
            time.sleep(2)

        except Exception as e:
            print(f"שגיאה בביקור בעמוד הבית: {e}")

        all_products = []
        size = 50
        start = 0

        while True:
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

                # שימוש ב-session במקום requests ישירות
                response = session.get(url, params=params, timeout=10)
                print(f"סטטוס קוד: {response.status_code}")

                # הדפסת headers של התגובה לדיבוג
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
                    try:
                        # חילוץ שם המוצר
                        name = self._extract_product_name(item)

                        # חילוץ מחיר
                        price = self._extract_price(item)

                        # חילוץ כמות
                        quantity = self._extract_quantity(item)

                        # חילוץ יצרן
                        brand = self._extract_brand(item)

                        # יצירת מוצר עם חישוב מחיר יחסי
                        product = self._create_product_with_unit_price(name, price, quantity, brand)
                        all_products.append(product)

                    except Exception as e:
                        print(f"שגיאה בעיבוד מוצר {i + 1}: {e}")
                        print(f"נתוני המוצר: {item}")
                        continue

                start += size

                # הפסקה ארוכה יותר בין בקשות
                import time
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

    def _create_product_with_unit_price(self, name, price, quantity, brand):
        """יצירת מוצר עם חישוב מחיר יחסי"""
        # חישוב מחיר יחסי
        unit_price_info = self._calculate_unit_price(price, quantity)

        # יצירת מוצר בסיסי
        product = Product(name, price, "שוק העיר", quantity, brand)

        # הוספת מידע על מחיר יחסי
        if unit_price_info:
            product.unit_price = unit_price_info["price"]
            product.unit_type = unit_price_info["unit"]
            product.display_info = unit_price_info["display"]

        return product

    def _calculate_unit_price(self, price, quantity_str):
        """חישוב מחיר ליחידת מידה סטנדרטית"""
        if not quantity_str or price <= 0:
            return None

        # פרסוני כמות ויחידה
        quantity_info = self._parse_quantity(quantity_str)
        if not quantity_info:
            return None

        amount = quantity_info["amount"]
        unit = quantity_info["unit"]

        # הגדרת יחידות סטנדרטיות
        unit_standards = {
            # משקל
            "גרם": {"standard": 100, "display": "100 גרם"},
            "קילוגרם": {"standard": 1, "display": "1 ק\"ג"},
            "מיליגרם": {"standard": 100000, "display": "100 גרם"},  # המרה ל-100 גרם

            # נפח
            "מ\"ל": {"standard": 100, "display": "100 מ\"ל"},
            "ליטר": {"standard": 1, "display": "1 ליטר"},

            # יחידות
            "יחידות": {"standard": 1, "display": "יחידה"},
        }

        if unit not in unit_standards:
            return None

        standard = unit_standards[unit]

        # חישוב מחיר יחסי
        unit_price = (price / amount) * standard["standard"]

        return {
            "price": round(unit_price, 2),
            "unit": standard["display"],
            "display": f"{round(unit_price, 2)} ש\"ח ל{standard['display']}"
        }

    def _parse_quantity(self, quantity_str):
        """פרסונג כמות ויחידה מתוך מחרוזת"""
        if not quantity_str:
            return None

        # דפוסי חיפוש לכמות ויחידה
        patterns = [
            # דפוסים רגילים
            r'(\d+(?:\.\d+)?)\s*(ק"?ג|קילוגרם|גר\'?|גרם|מ"?ל|ליטר|מיליגרם|מ"?ג)',
            r'(\d+)\s*(יחידות?|יח\'?)',

            # דפוסי מארז (4×1 ליטר)
            r'(\d+)\s*[×xX]\s*(\d+(?:\.\d+)?)\s*(ק"?ג|קילוגרם|גר\'?|גרם|מ"?ל|ליטר)',
        ]

        for pattern in patterns:
            match = re.search(pattern, quantity_str, re.IGNORECASE)
            if match:
                groups = match.groups()

                if len(groups) == 3:  # מארז
                    count = float(groups[0])
                    unit_amount = float(groups[1])
                    unit = self._normalize_unit_for_calculation(groups[2])
                    total_amount = count * unit_amount
                    return {"amount": total_amount, "unit": unit}
                else:  # רגיל
                    amount = float(groups[0])
                    unit = self._normalize_unit_for_calculation(groups[1])
                    return {"amount": amount, "unit": unit}

        # ניסיון להבין מהשם אם לא נמצא דפוס
        if "ליטר" in quantity_str.lower():
            match = re.search(r'(\d+(?:\.\d+)?)', quantity_str)
            if match:
                return {"amount": float(match.group(1)), "unit": "ליטר"}

        if any(word in quantity_str.lower() for word in ["גרם", "ק\"ג", "קילו"]):
            match = re.search(r'(\d+(?:\.\d+)?)', quantity_str)
            if match:
                amount = float(match.group(1))
                if "ק" in quantity_str.lower() or "קילו" in quantity_str.lower():
                    return {"amount": amount, "unit": "קילוגרם"}
                else:
                    return {"amount": amount, "unit": "גרם"}

        return None

    def _normalize_unit_for_calculation(self, unit):
        """נירמול יחידות לחישוב מחיר יחסי"""
        unit_mapping = {
            'ק"ג': 'קילוגרם',
            'קילו': 'קילוגרם',
            'קילוגרm': 'קילוגרם',
            'גר\'': 'גרם',
            'גרם': 'גרם',
            'ג\'': 'גרם',
            'מ"ל': 'מ"ל',
            'מיליליטר': 'מ"ל',
            'ל\'': 'ליטר',
            'ליטר': 'ליטר',
            'יח\'': 'יחידות',
            'יחידה': 'יחידות',
            'יחידות': 'יחידות',
            'מ"ג': 'מיליגרם',
            'מג': 'מיליגרם',
            'מיליגרם': 'מיליגרם',
        }

        return unit_mapping.get(unit.lower(), unit)

    def _extract_product_name(self, item):
        """חילוץ שם המוצר"""
        # מנסים מספר מקורות לשם המוצר
        name_sources = [
            item.get("localName"),  # שם מקומי - בדרך כלל הכי מדויק
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

        # נסיון נוסף למקרה שהמחיר נמצא במקום אחר
        try:
            price = item.get("price")
            if price is not None:
                return float(price)
        except (ValueError, TypeError):
            pass

        return 0.0

    def _extract_quantity(self, item):
        """חילוץ כמות המוצר - גרסה משופרת"""
        # קודם כל נחפש בשדות הישירים
        quantity_sources = [
            item.get("weight"),
            item.get("unitOfMeasure", {}).get("names", {}).get("1"),  # יחידת מידה
            item.get("numberOfItems"),  # מספר יחידות
            item.get("original", {}).get("weight"),
            item.get("size"),
            item.get("original", {}).get("size"),
            item.get("volume"),
            item.get("original", {}).get("volume")
        ]

        # בדיקה מיוחדת עבור weight ו-unitOfMeasure
        weight = item.get("weight")
        unit_of_measure = item.get("unitOfMeasure", {}).get("names", {}).get("1")

        if weight and unit_of_measure:
            return f"{weight} {self._normalize_unit(unit_of_measure)}"

        # בדיקה לmultipack (כמו 4×1 ליטר)
        number_of_items = item.get("numberOfItems")
        if number_of_items and number_of_items > 1 and weight and unit_of_measure:
            return f"{number_of_items}×{weight} {self._normalize_unit(unit_of_measure)}"

        # בדיקה בשדות אחרים
        for quantity in quantity_sources:
            if quantity and str(quantity).strip():
                if quantity not in [weight, unit_of_measure, number_of_items]:  # למנוע כפל
                    return str(quantity).strip()

        # אם לא נמצאה כמות ישירה, מנסים לחלץ מהשם
        name = self._extract_product_name(item)
        extracted_quantity = self._extract_quantity_from_name(name)
        if extracted_quantity:
            return extracted_quantity

        # מנסים לחלץ מכל השמות הזמינים
        names_data = item.get("names", {})
        for lang_id, name_data in names_data.items():
            if isinstance(name_data, dict):
                for name_type in ["long", "short"]:
                    if name_type in name_data and name_data[name_type]:
                        extracted = self._extract_quantity_from_name(name_data[name_type])
                        if extracted:
                            return extracted

        return None

    def _extract_brand(self, item):
        """חילוץ שם היצרן - גרסה משופרת"""
        # מנסים מספר מקורות ליצרן
        try:
            # בדיקה הדרגתית בmulti-level dictionaries
            brand_data = item.get("brand", {})
            if isinstance(brand_data, dict):
                # נסיון לגשת לשם היצרן
                names_data = brand_data.get("names", {})
                if isinstance(names_data, dict):
                    # מחפשים בשפה העברית (1) או באנגלית (2)
                    for lang_id in ["1", "2"]:
                        if lang_id in names_data:
                            brand_name = names_data[lang_id]
                            if isinstance(brand_name, str) and brand_name.strip():
                                return brand_name.strip()

                # אם לא נמצא ב-names, מנסים ישירות ב-brand
                if "name" in brand_data and brand_data["name"]:
                    brand_name = brand_data["name"]
                    if isinstance(brand_name, str) and brand_name.strip():
                        return brand_name.strip()

        except Exception as e:
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
                brand_name = brand.strip()
                return brand_name

        # אם לא נמצא יצרן ישיר, מנסים לחלץ מהשם
        name = self._extract_product_name(item)
        extracted_brand = self._extract_brand_from_name(name)
        if extracted_brand:
            return extracted_brand

        return None

    def _extract_brand_from_name(self, name):
        """חילוץ יצרן מתוך שם המוצר"""
        # רשימת יצרנים ידועים
        known_brands = [
            "אוסם", "תנובה", "יטבתה", "טעמן", "קוקה קולא", "פפסי",
            "נסטלה", "בישולי", "שטראוס", "עלית", "שופרסל", "סוגת",
            "מגדים", "אסם", "ברמן", "חרמון", "גלידות שטראוס", "דנונה",
            "מאיר בגל", "מעדן", "ויסוצקי", "עלי", "מילקי", "סימפליסימו",
            "בן עמי", "זוגלובק", "פיצה האט", "דומינו", "תל אביב", "מוצר ישראלי",
            "קוקה קולה", "coca cola", "cocacola", "ספרינג", "פריגת", "ג'אמפ",
            "רפאל'ס", "נובי", "פרינוק", "דניאלה", "אקטימל", "יופלה", "פרוט & ווג'",
            "פריטוב", "מטרנה", "בייבי ביס", "תנובה אלטרנטיב", "גמדים", "דנונה פרו"
        ]

        name_lower = name.lower()
        for brand in known_brands:
            if brand.lower() in name_lower:
                return brand

        return None

    def _extract_quantity_from_name(self, name):
        """חילוץ כמות מתוך שם המוצר - פונקציה משופרת"""
        import re

        patterns = [
            r'(\d+(?:\.\d+)?)\s*(ק"?ג|קילו|קילוגרם)',  # קילוגרם
            r'(\d+(?:\.\d+)?)\s*(גר\'?|גרם)',  # גרם
            r'(\d+(?:\.\d+)?)\s*(מ"?ל|מיליליטר)',  # מיליליטר
            r'(\d+(?:\.\d+)?)\s*(ליטר|ל\')',  # ליטר
            r'(\d+)\s*(יחידות?|יח\'?)',  # יחידות
            r'(\d+(?:\.\d+)?)\s*(מ"?ג|מיליגרם)',  # מיליגרם
            r'(\d+(?:\.\d+)?)\s*ג\'',  # גרם בקיצור
            r'(\d+)\s*[×xX]\s*(\d+(?:\.\d+)?)\s*(מ"?ל|ליטר|גר\'?|גרם|ק"?ג)',  # פורמט כמו 4×1 ליטר
            r'מארז\s*(\d+)\s*(יחידות?)',  # מארז X יחידות
            r'(\d+)\s*חתיכות',  # חתיכות
            r'(\d+)\s*עוגיות',  # עוגיות
            r'(\d+)\s*כדורים',  # כדורים
        ]

        for pattern in patterns:
            match = re.search(pattern, name, re.IGNORECASE)
            if match:
                groups = match.groups()

                if len(groups) == 3 and any(char in pattern.lower() for char in ['×', 'x']):
                    # פורמט של כמות × יחידה
                    count = groups[0]
                    amount = groups[1]
                    unit = groups[2]
                    return f"{count}×{amount} {self._normalize_unit(unit)}"
                else:
                    amount = groups[0]
                    unit = groups[1] if len(groups) > 1 else "יחידות"
                    return f"{amount} {self._normalize_unit(unit)}"

        return None

    def _normalize_unit(self, unit):
        """נירמול יחידות מידה"""
        if not unit:
            return "יחידות"

        unit_mapping = {
            'ק"ג': 'קילוגרם',
            'קילו': 'קילוגרם',
            'קילוגרם': 'קילוגרם',
            'גר\'': 'גרם',
            'גרם': 'גרם',
            'מ"ל': 'מ"ל',
            'מיליליטר': 'מ"ל',
            'ל\'': 'ליטר',
            'ליטר': 'ליטר',
            'יח\'': 'יחידות',
            'יחידה': 'יחידות',
            'יחידות': 'יחידות',
            'מ"ג': 'מיליגרם',
            'מג': 'מיליגרם',
            'מיליגרם': 'מיליגרם',
            'ג\'': 'גרם',
            'חתיכות': 'יחידות',
            'עוגיות': 'יחידות',
            'כדורים': 'יחידות'
        }

        return unit_mapping.get(unit.lower(), unit)