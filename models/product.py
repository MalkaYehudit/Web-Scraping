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

# class Product:
#     def __init__(self, name, price, store, quantity=None, brand=None):
#         self.name = name
#         self.price = price
#         self.store = store
#         self.quantity = quantity
#         self.brand = brand
#         # שדות חדשים למחיר יחסי
#         self.unit_price = None
#         self.unit_type = None
#         self.display_info = None
#
#     def __str__(self):
#         """הצגת המוצר עם מחיר יחסי"""
#         # בניית מחרוזת בסיסית
#         result = f"{self.store}: {self.name}"
#
#         # הוספת יצרן אם קיים
#         if self.brand:
#             result += f" ({self.brand})"
#
#         # הוספת כמות אם קיימת
#         if self.quantity:
#             result += f" [{self.quantity}]"
#
#         # הוספת מחיר
#         result += f" - {self.price} ש\"ח"
#
#         # הוספת מחיר יחסי אם קיים
#         if self.display_info:
#             result += f" ({self.display_info})"
#
#         return result
#
#     def get_unit_price_value(self):
#         """החזרת המחיר היחסי כמספר לצורך השוואה"""
#         return self.unit_price if self.unit_price else float('inf')
#
#     def get_formatted_unit_price(self):
#         """החזרת המחיר היחסי מעוצב"""
#         return self.display_info if self.display_info else "לא זמין"

#
# import re
#
# class Product:
#     def __init__(self, name, price, store, quantity=None, brand=None):
#         self.name = name
#         self.price = price
#         self.store = store
#         self.quantity = quantity
#         self.brand = brand
#         self.unit_price = None
#         self.unit_type = None
#         self.display_info = None
#
#         # חישוב מחיר יחסי אם אפשר
#         if quantity:
#             self.original_quantity = quantity  # לשימור מחרוזת המקור
#             total_qty, unit = self._parse_total_quantity(quantity)
#             if total_qty and unit:
#                 if unit == 'מ"ל':
#                     unit_price = round(price / total_qty * 100, 2)
#                     display_unit = '100 מ"ל'
#                 elif unit == 'גרם':
#                     unit_price = round(price / total_qty * 100, 2)
#                     display_unit = '100 גרם'
#                 elif unit == 'ליטר':
#                     unit_price = round(price / total_qty, 2)
#                     display_unit = 'ליטר'
#                 elif unit == 'ק"ג':
#                     unit_price = round(price / total_qty, 2)
#                     display_unit = 'ק"ג'
#                 else:
#                     unit_price = None
#                     display_unit = None
#
#                 if unit_price is not None:
#                     self.unit_price = unit_price
#                     self.unit_type = display_unit
#                     self.display_info = f"{unit_price} ש\"ח ל{display_unit}"
#                     self.quantity = f"{total_qty} {unit}"  # שומר את כמות המקור (כולל יחידה)
#
#     # def _parse_total_quantity(self, quantity_str):
#     #     """
#     #     מנתח מחרוזות כמו:
#     #     - "6x2 ליטר" => 12 ליטר
#     #     - "10x10 גרם" => 100 גרם
#     #     - "1.5 ליטר" => 1.5 ליטר
#     #     - "500 מ\"ל" => 500 מ"ל
#     #     - "1 יחידה" => לא מחשב
#     #     """
#     #     quantity_str = quantity_str.strip()
#     #
#     #     # תבנית למארזים: 6x2 ליטר, 10x10 גרם
#     #     match_pack = re.search(
#     #         r'(\d+)\s*(?:x|\*|כפול)?\s*(\d+\.?\d*)\s*(ליטר|מ"ל|גרם|ק"ג)',
#     #         quantity_str.replace('מ\"ל', 'מ"ל').replace('ק\"ג', 'ק"ג')  # נרמל צורת גרשיים
#     #     )
#     #     if match_pack:
#     #         units = int(match_pack.group(1))
#     #         amount = float(match_pack.group(2))
#     #         unit = match_pack.group(3)
#     #         total = units * amount
#     #         return total, unit
#     #
#     #     # תבנית רגילה: 1.5 ליטר, 500 מ"ל
#     #     match_single = re.match(r'(\d+\.?\d*)\s*(ליטר|מ\"ל|גרם|ק\"ג)', quantity_str)
#     #     if match_single:
#     #         total = float(match_single.group(1))
#     #         unit = match_single.group(2)
#     #         return total, unit
#     #
#     #     # לא הצליח לפרש – אין כמות מדידה
#     #     return None, None
#
#     @staticmethod
#     def _parse_total_quantity(quantity_str):
#         """
#         מפרש תיאור כמות כמו:
#         - "6x2 ליטר" => 12 ליטר
#         - "10x10 גרם" => 100 גרם
#         - "1.5 ליטר" => 1.5 ליטר
#         - "500 מ\"ל" => 500 מ"ל
#         - "שישייה 1.5 ליטר" => 9 ליטר
#         - "320*6 מ"ל" => 1920 מ"ל
#         - "1 יחידה" => None
#         """
#         quantity_str = quantity_str.strip().replace('\"', '"').replace('מ\"ל', 'מ"ל').replace('ק\"ג', 'ק"ג')
#
#         # מילים מוכרות למארזים
#         known_packs = {
#             'שישייה': 6,
#             'רביעייה': 4,
#             'שלישייה': 3,
#             'זוג': 2,
#         }
#
#         # 1. זיהוי לפי מילת מארז + נפח
#         for word, count in known_packs.items():
#             pattern = rf'{word}\s*(\d+\.?\d*)\s*(ליטר|מ"ל|גרם|ק"ג)'
#             match = re.search(pattern, quantity_str)
#             if match:
#                 amount = float(match.group(1))
#                 unit = match.group(2)
#                 return count * amount, unit
#
#         # 2. זיהוי לפי כמות × גודל – בשני הסדרים
#         patterns = [
#             r'(\d+)\s*[x\*]\s*(\d+\.?\d*)\s*(ליטר|מ"ל|גרם|ק"ג)',  # כמות × גודל
#             r'(\d+\.?\d*)\s*[x\*]\s*(\d+)\s*(ליטר|מ"ל|גרם|ק"ג)',  # גודל × כמות
#         ]
#         for pattern in patterns:
#             match = re.search(pattern, quantity_str)
#             if match:
#                 a = float(match.group(1))
#                 b = float(match.group(2))
#                 unit = match.group(3)
#                 # נניח שהכמות היא השלם והנפח הוא השבר (אם ברור)
#                 if a.is_integer() and not b.is_integer():
#                     units, amount = int(a), b
#                 elif b.is_integer() and not a.is_integer():
#                     units, amount = int(b), a
#                 else:
#                     # אם שניהם שלמים או שניהם עשרוניים – נניח הראשון זה כמות
#                     units, amount = int(a), b
#                 return units * amount, unit
#
#         # 3. זיהוי רגיל – כמות אחת
#         match = re.match(r'(\d+\.?\d*)\s*(ליטר|מ"ל|גרם|ק"ג)', quantity_str)
#         if match:
#             return float(match.group(1)), match.group(2)
#
#         # 4. לא הצליח לפרש
#         return None, None
#
#     def __str__(self):
#         result = f"{self.store}: {self.name}"
#         if self.brand:
#             result += f" ({self.brand})"
#         if self.quantity:
#             result += f" [{self.quantity}]"
#         result += f" - {self.price} ש\"ח"
#         if self.display_info:
#             result += f" ({self.display_info})"
#         return result
#
#     def get_unit_price_value(self):
#         return self.unit_price if self.unit_price else float('inf')
#
#     def get_formatted_unit_price(self):
#         return self.display_info if self.display_info else "לא זמין"
#
# import re
# from models.utils import parse_total_quantity
#
# class Product:
#     def __init__(self, name, price, store, quantity=None, brand=None):
#         self.name = name
#         self.price = price
#         self.store = store
#         self.quantity = quantity
#         self.brand = brand
#         self.unit_price = None
#         self.unit_type = None
#         self.display_info = None
#
#         if quantity:
#             self.original_quantity = quantity
#             total_qty, unit = parse_total_quantity(quantity)
#             if total_qty and unit:
#                 if unit == 'מ"ל':
#                     unit_price = round(price / total_qty * 100, 2)
#                     display_unit = '100 מ"ל'
#                 elif unit == 'גרם':
#                     unit_price = round(price / total_qty * 100, 2)
#                     display_unit = '100 גרם'
#                 elif unit == 'ליטר':
#                     unit_price = round(price / total_qty, 2)
#                     display_unit = 'ליטר'
#                 elif unit == 'ק"ג':
#                     unit_price = round(price / total_qty, 2)
#                     display_unit = 'ק"ג'
#                 else:
#                     unit_price = None
#                     display_unit = None
#
#                 if unit_price is not None:
#                     self.unit_price = unit_price
#                     self.unit_type = display_unit
#                     self.display_info = f"{unit_price} ש\"ח ל{display_unit}"
#                     self.quantity = f"{total_qty} {unit}"
#
#     def __str__(self):
#         result = f"{self.store}: {self.name}"
#         if self.brand:
#             result += f" ({self.brand})"
#         if self.quantity:
#             result += f" [{self.quantity}]"
#         result += f" - {self.price} ש\"ח"
#         if self.display_info:
#             result += f" ({self.display_info})"
#         return result
#
#     def get_unit_price_value(self):
#         return self.unit_price if self.unit_price else float('inf')
#
#     def get_formatted_unit_price(self):
#         return self.display_info if self.display_info else "לא זמין"


from dataclasses import dataclass
from typing import Optional


@dataclass
class Product:
    """
    מודל למוצר עם תמיכה במחירים יחסיים
    """
    name: str
    price: float
    store: str
    quantity: Optional[str] = None
    brand: Optional[str] = None

    # שדות למחיר יחסי
    unit_price: Optional[float] = None
    unit_type: Optional[str] = None
    display_info: Optional[str] = None

    # שדות נוספים לשימוש עתידי
    description: Optional[str] = None
    category: Optional[str] = None
    is_available: bool = True

    def __post_init__(self):
        """אתחול לאחר יצירת האובייקט"""
        if not self.description:
            self.description = f"{self.name} - {self.store}"

    def get_formatted_price(self) -> str:
        """החזרת מחיר מעוצב"""
        return f"₪{self.price:.2f}"

    def get_unit_price_display(self) -> str:
        """החזרת מחיר יחסי מעוצב"""
        if self.unit_price and self.unit_type:
            return f"₪{self.unit_price:.2f} ל{self.unit_type}"
        return ""

    def to_dict(self) -> dict:
        """המרה למילון"""
        return {
            'name': self.name,
            'price': self.price,
            'store': self.store,
            'quantity': self.quantity,
            'brand': self.brand,
            'unit_price': self.unit_price,
            'unit_type': self.unit_type,
            'display_info': self.display_info,
            'description': self.description,
            'category': self.category,
            'is_available': self.is_available
        }