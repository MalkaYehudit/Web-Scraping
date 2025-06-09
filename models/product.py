# import re
#
#
# class Product:
#     def __init__(self, name, price, store, quantity=None, brand=None):
#         self.name = name
#         self.price = float(price)
#         self.store = store
#         self.quantity = quantity or self._extract_quantity_from_name(name)
#         self.brand = brand or self._extract_brand_from_name(name)
#
#     def _extract_quantity_from_name(self, name):
#         """חילוץ כמות מתוך שם המוצר"""
#         # דפוסים לחיפוש כמויות - מורחב ומשופר
#         patterns = [
#             r'(\d+(?:\.\d+)?)\s*(ק"?ג|קילו|קילוגרם)',  # קילוגרם
#             r'(\d+(?:\.\d+)?)\s*(גר\'?|גרם)',  # גרם
#             r'(\d+(?:\.\d+)?)\s*(מ"?ל|מיליליטר)',  # מיליליטר
#             r'(\d+(?:\.\d+)?)\s*(ליטר|ל\')',  # ליטר
#             r'(\d+)\s*(יחידות?|יח\'?)',  # יחידות
#             r'(\d+(?:\.\d+)?)\s*(מ"?ג|מיליגרם)',  # מיליגרם
#             r'(\d+(?:\.\d+)?)\s*ג\'',  # גרם בקיצור
#             # דפוסים חדשים למקרים מיוחדים
#             r'(\d+)\s*[×xX]\s*(\d+(?:\.\d+)?)\s*(מ"?ל|ליטר|גר\'?|גרם|ק"?ג)',  # פורמט כמו 4×1 ליטר
#             r'(\d+(?:\.\d+)?)\s*(ק"ג)',  # קילוגרם בלי נקודות
#             r'מארז\s*(\d+)\s*(יחידות?)',  # מארז X יחידות
#             r'(\d+)\s*(יח\')',  # יחידות בקיצור נוסף
#             r'(\d+)\s*חתיכות',  # חתיכות
#             r'(\d+)\s*עוגיות',  # עוגיות
#             r'(\d+)\s*כדורים',  # כדורים
#             r'(\d+)\s*פריטים',  # פריטים
#         ]
#
#         for pattern in patterns:
#             match = re.search(pattern, name, re.IGNORECASE)
#             if match:
#                 groups = match.groups()
#
#                 # טיפול בפורמט של כמות × יחידה (כמו 4×1 ליטר)
#                 if len(groups) == 3 and any(char in pattern for char in ['×', 'x', 'X']):
#                     count = groups[0]
#                     amount = groups[1]
#                     unit = groups[2]
#                     normalized_unit = self._normalize_unit(unit)
#                     return f"{count}×{amount} {normalized_unit}"
#
#                 # טיפול רגיל
#                 elif len(groups) >= 2:
#                     amount = groups[0]
#                     unit = groups[1] if len(groups) > 1 else groups[0]
#                     normalized_unit = self._normalize_unit(unit)
#                     return f"{amount} {normalized_unit}"
#
#                 # טיפול במקרה של יחידה בלבד
#                 else:
#                     amount = groups[0]
#                     return f"{amount} יחידות"
#
#         return None
#
#     def _extract_brand_from_name(self, name):
#         """חילוץ יצרן מתוך שם המוצר"""
#         # רשימת יצרנים ידועים בישראל
#         known_brands = [
#             # יצרני מזון מרכזיים
#             "אוסם", "תנובה", "יטבתה", "טעמן", "שטראוס", "עלית", "בישולי",
#             "סוגת", "מגדים", "ברמן", "חרמון", "דנונה", "מעדן", "בן עמי",
#             "זוגלובק", "מאיר בגל", "שמרית", "פרי גליל", "מאפיית אנג'ל",
#
#             # משקאות
#             "קוקה קולה", "פפסי", "שוופס", "נביעות", "מים עדן", "מי טבע",
#             "מי דניה", "פריגת", "מי שלמה", "מי אמרקה", "סודה קלאב",
#
#             # קפה ותה
#             "ויסוצקי", "עלי", "נס קפה", "עלית", "טארה", "לנדוור",
#
#             # מוצרי חלב
#             "תנובה", "יטבתה", "מעדן", "דנונה", "מילקי", "שטראוס",
#             "גבינות גד", "גבינות רמת הגולן",
#
#             # ממתקים וחטיפים
#             "עלית", "שטראוס", "פרינגלס", "דוריטוס", "במבה", "ביסלי",
#             "כרמית", "פסק זמן", "קליק", "מנטוס", "האריבו",
#
#             # בשר ודגים
#             "תבואות", "זוגלובק", "מעוף עופות", "לול", "יהודה", "דגי דגי",
#
#             # מוצרים בינלאומיים
#             "נסטלה", "יוניליוור", "פרוקטר", "קלוגס", "מאגי", "נוטלה",
#             "פרינגלס", "אוראו", "לייז", "נסטלה קראנץ'",
#
#             # רשתות קמעונאות (מותגים פרטיים)
#             "שופרסל", "רמי לוי", "מגה", "יוחננוף", "טיב טעם", "חצי חינם",
#             "מחסני השוק", "אושר עד", "ויקטורי", "שוק אהרונוב"
#         ]
#
#         name_lower = name.lower()
#         for brand in known_brands:
#             # בדיקה גם עם רווח לפני ואחרי למניעת התאמות חלקיות לעברית
#             if brand.lower() in name_lower:
#                 # בדיקה נוספת שזה לא חלק ממילה אחרת
#                 import re
#                 pattern = r'\b' + re.escape(brand.lower()) + r'\b'
#                 if re.search(pattern, name_lower):
#                     return brand
#
#         return None
#
#     def _normalize_unit(self, unit):
#         """נירמול יחידות מידה"""
#         unit_mapping = {
#             'ק"ג': 'קילוגרם',
#             'קילו': 'קילוגרם',
#             'גר\'': 'גרם',
#             'גרם': 'גרם',
#             'מ"ל': 'מ"ל',
#             'מיליליטר': 'מ"ל',
#             'ל\'': 'ליטר',
#             'ליטר': 'ליטר',
#             'יח\'': 'יחידות',
#             'יחידה': 'יחידות',
#             'יחידות': 'יחידות',
#             'מ"ג': 'מיליגרם',
#             'מיליגרם': 'מיליגרם',
#             'ג\'': 'גרם',
#             'חתיכות': 'יחידות',
#             'עוגיות': 'יחידות',
#             'כדורים': 'יחידות',
#             'פריטים': 'יחידות'
#         }
#
#         return unit_mapping.get(unit, unit)
#
#     def get_price_per_unit(self):
#         """חישוב מחיר ליחידה"""
#         if not self.quantity:
#             return None
#
#         # חילוץ המספר מתוך הכמות
#         import re
#
#         # חיפוש דפוס של מספר בתחילת המחרוזת
#         match = re.search(r'(\d+(?:\.\d+)?)', self.quantity)
#         if match:
#             try:
#                 quantity_num = float(match.group(1))
#                 if quantity_num > 0:
#                     return round(self.price / quantity_num, 2)
#             except ValueError:
#                 pass
#
#         return None
#
#     def __repr__(self):
#         parts = [f"{self.store}: {self.name}"]
#
#         if self.brand:
#             parts.append(f"({self.brand})")
#
#         if self.quantity:
#             parts.append(f"[{self.quantity}]")
#
#         parts.append(f"- {self.price} ש\"ח")
#
#         # הוספת מחיר ליחידה אם זמין
#         price_per_unit = self.get_price_per_unit()
#         if price_per_unit:
#             parts.append(f"({price_per_unit} ש\"ח ליחידה)")
#
#         return " ".join(parts)
#
#     def to_dict(self):
#         """המרה למילון לצורך שמירה או ייצוא"""
#         return {
#             'name': self.name,
#             'price': self.price,
#             'store': self.store,
#             'quantity': self.quantity,
#             'brand': self.brand,
#             'price_per_unit': self.get_price_per_unit()
#         }

class Product:
    def __init__(self, name, price, store, quantity=None, brand=None):
        self.name = name
        self.price = price
        self.store = store
        self.quantity = quantity
        self.brand = brand
        # שדות חדשים למחיר יחסי
        self.unit_price = None
        self.unit_type = None
        self.display_info = None

    def __str__(self):
        """הצגת המוצר עם מחיר יחסי"""
        # בניית מחרוזת בסיסית
        result = f"{self.store}: {self.name}"

        # הוספת יצרן אם קיים
        if self.brand:
            result += f" ({self.brand})"

        # הוספת כמות אם קיימת
        if self.quantity:
            result += f" [{self.quantity}]"

        # הוספת מחיר
        result += f" - {self.price} ש\"ח"

        # הוספת מחיר יחסי אם קיים
        if self.display_info:
            result += f" ({self.display_info})"

        return result

    def get_unit_price_value(self):
        """החזרת המחיר היחסי כמספר לצורך השוואה"""
        return self.unit_price if self.unit_price else float('inf')

    def get_formatted_unit_price(self):
        """החזרת המחיר היחסי מעוצב"""
        return self.display_info if self.display_info else "לא זמין"