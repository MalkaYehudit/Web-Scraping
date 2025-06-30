import re
from typing import Optional, Tuple
from models.product import Product


class QuantityExtractor:
    def __init__(self):
        self.multi_unit_patterns = [
            r'(\d+)\s*[*×x]\s*(\d+(?:\.\d+)?)\s*(ליטר|מ"ל|ק"ג|גרם|יח\'?|יחידות?)',
            r'(\d+)\s*(?:×|x|\*)\s*(\d+(?:\.\d+)?)\s*(ליטר|מ"ל|ק"ג|גרם|יח\'?|יחידות?)',
            r'(\d+)\s*(?:יח\'?|יחידות?)\s*(?:של|×|x|\*)\s*(\d+(?:\.\d+)?)\s*(ליטר|מ"ל|ק"ג|גרם)',
            r'(\d+)\s*(?:בקבוקי|בקבוקים)\s*(?:של|×|x|\*)\s*(\d+(?:\.\d+)?)\s*(ליטר|מ"ל)',
            r'(\d+)\s*(?:חבילות|חבי?לות)\s*(?:של|×|x|\*)\s*(\d+(?:\.\d+)?)\s*(ק"ג|גרם)',
        ]

        self.regular_patterns = [
            (r'(\d+(?:\.\d+)?)\s*(?:ליטר|ל\'?)', 'ליטר'),
            (r'(\d+(?:\.\d+)?)\s*(?:מ"?ל|מיליליטר)', 'מ"ל'),
            (r'(\d+(?:\.\d+)?)\s*(?:ק"?ג|קילו|קילוגרם)', 'ק"ג'),
            (r'(\d+(?:\.\d+)?)\s*(?:גר\'?|גרם)', 'גרם'),
            (r'(\d+(?:\.\d+)?)\s*(?:יח\'?|יחידות?|יחידה)', 'יחידה'),
            (r'(\d+(?:\.\d+)?)\s*(?:חבי?לות?|חבילה)', 'יחידה'),
            (r'(\d+(?:\.\d+)?)\s*(?:בקבוקים?|בקבוק)', 'יחידה'),
            (r'(\d+(?:\.\d+)?)\s*(?:כוסות?|כוס)', 'יחידה'),
            (r'(\d+(?:\.\d+)?)\s*(?:פחיות?|פחית)', 'יחידה'),
        ]

        self.word_quantity_map = {
            'שישיה': 6,
            'שישיית': 6,
            'שלישיה': 3,
            'שלישיית': 3,
            'רביעייה': 4,
            'רביעיית': 4,
            'מארז של': 6,
            'מארז': 6,
            'שיש': 6,
        }

    def extract_quantity_from_fields(self, weight: Optional[float] = None,
                                     unit_of_measure: Optional[str] = None,
                                     quantity_field: Optional[str] = None,
                                     size_field: Optional[str] = None) -> str:
        if weight and unit_of_measure:
            normalized_unit = self.normalize_unit_type(unit_of_measure)
            return f"{weight} {normalized_unit}"

        if quantity_field:
            return str(quantity_field).strip()

        if size_field:
            return str(size_field).strip()

        return ""

    def extract_quantity_from_name(self, product_name: str) -> str:
        if not product_name:
            return ""

        quantity = self._extract_multi_unit_quantity(product_name)
        if quantity:
            return quantity

        quantity = self._extract_word_based_quantity(product_name)
        if quantity:
            return quantity

        return self._extract_regular_quantity(product_name)

    def _extract_multi_unit_quantity(self, product_name: str) -> str:
        for pattern in self.multi_unit_patterns:
            match = re.search(pattern, product_name, re.IGNORECASE)
            if match:
                units_count = match.group(1)
                unit_size = match.group(2)
                unit_type = match.group(3)
                unit_type_normalized = self.normalize_unit_type(unit_type)
                return f"{units_count} יחידות של {unit_size} {unit_type_normalized}"
        return ""

    def _extract_word_based_quantity(self, product_name: str) -> str:
        for word, count in self.word_quantity_map.items():
            if word in product_name:
                match = re.search(r'(\d+(?:\.\d+)?)\s*(ליטר|מ"ל|גרם|ק"ג)', product_name)
                if match:
                    size = match.group(1)
                    unit = match.group(2)
                    unit = self.normalize_unit_type(unit)
                    return f"{count} יחידות של {size} {unit}"
        return ""

    def _extract_regular_quantity(self, product_name: str) -> str:
        for pattern, unit_type in self.regular_patterns:
            match = re.search(pattern, product_name, re.IGNORECASE)
            if match:
                return match.group(0)
        return ""

    def normalize_unit_type(self, unit_type: str) -> str:
        if not unit_type:
            return ""

        unit_type = unit_type.lower().strip()

        unit_mapping = {
            'ליטר': ['ליטר', 'ל', 'ל\'', 'liter', 'l'],
            'מ"ל': ['מ"ל', 'מל', 'מיליליטר', 'ml', 'milliliter'],
            'ק"ג': ['ק"ג', 'קג', 'קילו', 'קילוגרם', 'kg', 'kilogram'],
            'גרם': ['גר\'', 'גר', 'גרם', 'g', 'gram', 'גרמים'],
            'יחידה': ['יח\'', 'יח', 'יחידות', 'יחידה', 'יחי', 'unit', 'piece']
        }

        for normalized, variations in unit_mapping.items():
            if unit_type in variations:
                return normalized

        return unit_type

    def parse_quantity_text(self, quantity_text: str) -> Tuple[Optional[float], Optional[str]]:
        if not quantity_text:
            return None, None

        quantity_text = quantity_text.lower().strip()

        # ניסיון רגיל עם תבנית מלאה
        multi_unit_match = re.search(
            r'(\d+)\s*(?:יחידות|יח\'?|בקבוקים?|חבילות?)\s*של\s*(\d+(?:\.\d+)?)\s*(ליטר|מ"ל|ק"ג|גרם)',
            quantity_text
        )
        if multi_unit_match:
            units_count = float(multi_unit_match.group(1))
            unit_size = float(multi_unit_match.group(2))
            unit_type = multi_unit_match.group(3)
            total_quantity = units_count * unit_size
            return total_quantity, self.normalize_unit_type(unit_type)

        # ניסיון רגיל: למצוא כמות אחת
        for pattern, unit in self.regular_patterns:
            match = re.search(pattern, quantity_text)
            if match:
                try:
                    quantity_num = float(match.group(1))
                    unit = self.normalize_unit_type(unit)

                    # בדיקה אם יש מילה שמעידה על כמה יחידות
                    for word, count in self.word_quantity_map.items():
                        if word in quantity_text:
                            return quantity_num * count, unit

                    return quantity_num, unit
                except (ValueError, IndexError):
                    continue

        # ניסיון אחרון: מילה שמעידה על כמות אך בלי מספר
        for word, count in self.word_quantity_map.items():
            if word in quantity_text:
                # נניח שהיחידה היא "מ"ל" ונחפש מספר
                match = re.search(r'(\d+(?:\.\d+)?)\s*(מ"ל|ליטר|גרם|ק"ג)', quantity_text)
                if match:
                    quantity_num = float(match.group(1))
                    unit = self.normalize_unit_type(match.group(2))
                    return quantity_num * count, unit

        return None, None

    def calculate_unit_price(self, product: Product):
        if not product.price:
            return

        quantity_text = product.quantity

        if not quantity_text:
            quantity_text = self.extract_quantity_from_name(product.name)
            if quantity_text:
                product.quantity = quantity_text

        if not quantity_text:
            return

        quantity_num, unit = self.parse_quantity_text(quantity_text)

        if quantity_num and unit:
            self._calculate_price_by_unit_type(product, quantity_num, unit)

    def _calculate_price_by_unit_type(self, product: Product, quantity_num: float, unit: str):
        try:
            if unit == 'מ"ל':
                unit_price = round((product.price / quantity_num) * 100, 2)
                product.unit_price = unit_price
                product.unit_type = '100 מ"ל'
                product.display_info = f"₪{unit_price} ל-100 מ\"ל"

            elif unit == 'ליטר':
                unit_price = round(product.price / quantity_num, 2)
                product.unit_price = unit_price
                product.unit_type = 'ליטר'
                product.display_info = f"₪{unit_price} לליטר"

            elif unit == 'גרם':
                unit_price = round((product.price / quantity_num) * 100, 2)
                product.unit_price = unit_price
                product.unit_type = '100 גרם'
                product.display_info = f"₪{unit_price} ל-100 גרם"

            elif unit == 'ק"ג':
                unit_price = round(product.price / quantity_num, 2)
                product.unit_price = unit_price
                product.unit_type = 'ק"ג'
                product.display_info = f"₪{unit_price} לק\"ג"

            elif unit == 'יחידה':
                unit_price = round(product.price / quantity_num, 2)
                product.unit_price = unit_price
                product.unit_type = 'יחידה'
                product.display_info = f"₪{unit_price} ליחידה"

        except (ValueError, ZeroDivisionError):
            pass

    def get_weight_and_unit_for_db(self, quantity_text: str) -> Tuple[Optional[float], Optional[str]]:
        quantity_num, unit = self.parse_quantity_text(quantity_text)

        if quantity_num and unit:
            if unit in ['ליטר', 'מ"ל']:
                if unit == 'ליטר':
                    return quantity_num * 1000, 'מ"ל'
                return quantity_num, 'מ"ל'

            elif unit in ['ק"ג', 'גרם']:
                if unit == 'ק"ג':
                    return quantity_num * 1000, 'גרם'
                return quantity_num, 'גרם'

            elif unit == 'יחידה':
                return quantity_num, 'יחידה'

        return None, None
