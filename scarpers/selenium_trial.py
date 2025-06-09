from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import time
import re  # לטיפול בטקסט וניקוי מחירים

# --- הגדרות גלובליות ---
CHROMEDRIVER_PATH = 'C:\\Users\\User\\Downloads\\chromedriver-win64\\chromedriver.exe'  # עדכנו את הנתיב הנכון!
ZAP_MARKET_URL = "https://www.zapmarket.co.il/"


# --- 1. מחלקת ZapMarketPage: מייצגת את האינטראקציה עם דף האתר ---
class ZapMarketPage:
    def __init__(self, driver):
        self.driver = driver
        # הגדרת אלמנטים לפי מזהים (נאמת בבדיקה ידנית!)
        self.ADDRESS_INPUT = (By.ID, "AddressInput")  # השדה למיקום
        self.PRODUCT_SEARCH_INPUT = (By.CSS_SELECTOR,
                                     'input[placeholder="הכנס מוצר..."]')  # שדה חיפוש מוצר (אולי id="productSearchInput"?)
        self.ADD_PRODUCT_BUTTON = (By.CSS_SELECTOR, 'button.add-product-button')  # כפתור "הוסף" ליד שדה המוצר
        self.COMPARE_PRICES_BUTTON = (By.ID,
                                      "comparePricesButton")  # כפתור השוואת מחירים הסופי (ייתכן שצריך לחפש class)
        self.AVERAGE_PRICE_DISPLAY = (By.CSS_SELECTOR, '.average-price-display .price-value')  # תצוגת מחיר ממוצע
        self.STORE_LIST_CONTAINER = (By.CSS_SELECTOR, '.stores-list .store-card')  # קונטיינר לרשימת חנויות
        self.STORE_NAME = (By.CSS_SELECTOR, '.store-name')
        self.STORE_PRICE = (By.CSS_SELECTOR, '.store-total-price')

    def open_page(self):
        """פותח את דפדפן ונווט לאתר זאפ מרקט."""
        print(f"פותח את האתר: {ZAP_MARKET_URL}")
        self.driver.get(ZAP_MARKET_URL)
        # המתנה לטעינת הדף, נחפש אלמנט מרכזי כמו שדה המיקום
        WebDriverWait(self.driver, 15).until(
            EC.presence_of_element_located(self.ADDRESS_INPUT)
        )
        print("האתר נטען בהצלחה.")

    def set_location(self, location_text):
        """מזין את המיקום לשדה המתאים."""
        print(f"מזין מיקום: '{location_text}'")
        try:
            address_input = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable(self.ADDRESS_INPUT)
            )
            address_input.clear()
            address_input.send_keys(location_text)
            # לחיצה על מקש אנטר או המתנה לתוצאות אוטומטיות אם יש
            # address_input.send_keys(Keys.RETURN) # אם יש השלמה אוטומטית שדורשת Enter
            print("המיקום הוזן בהצלחה.")
        except TimeoutException:
            print("שגיאה: שדה המיקום לא נמצא או לא ניתן לאינטראקציה.")
            raise

    def add_product(self, product_name):
        """מזין מוצר לשדה החיפוש ולוחץ על 'הוסף'."""
        print(f"מנסה להוסיף מוצר: '{product_name}'")
        try:
            product_input = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable(self.PRODUCT_SEARCH_INPUT)
            )
            product_input.send_keys(product_name)
            time.sleep(0.5)  # המתנה קצרה לטעינת כפתור ההוספה

            add_button = WebDriverWait(self.driver, 5).until(
                EC.element_to_be_clickable(self.ADD_PRODUCT_BUTTON)
            )
            add_button.click()
            print(f"המוצר '{product_name}' נוסף בהצלחה.")
            time.sleep(1)  # המתנה לריענון הדף לאחר הוספת מוצר
        except (TimeoutException, NoSuchElementException) as e:
            print(f"שגיאה בהוספת מוצר '{product_name}': {e}")
            print("ודאו שהמזהים של שדה החיפוש וכפתור 'הוסף' נכונים ב-ZapMarketPage.")
            raise

    def click_compare_prices(self):
        """לוחץ על כפתור השוואת המחירים הסופי."""
        print("לוחץ על כפתור השוואת המחירים...")
        try:
            compare_button = WebDriverWait(self.driver, 15).until(
                EC.element_to_be_clickable(self.COMPARE_PRICES_BUTTON)
            )
            compare_button.click()
            print("כפתור השוואת המחירים נלחץ.")
            # המתנה לטעינת התוצאות
            WebDriverWait(self.driver, 30).until(
                EC.presence_of_element_located(self.AVERAGE_PRICE_DISPLAY)
            )
            print("תוצאות ההשוואה נטענו.")
        except TimeoutException:
            print("שגיאה: כפתור השוואת המחירים לא נמצא או שהתוצאות לא נטענו בזמן.")
            raise

    def get_average_price(self):
        """מחזיר את המחיר הממוצע המוצג בדף."""
        try:
            avg_price_element = self.driver.find_element(*self.AVERAGE_PRICE_DISPLAY)
            price_text = avg_price_element.text
            # נקה את הטקסט כדי להשאיר רק מספרים (כולל נקודה עשרונית)
            cleaned_price = re.sub(r'[^\d.]', '', price_text)
            return float(cleaned_price)
        except (NoSuchElementException, ValueError):
            print("שגיאה: לא ניתן למצוא או לנתח את המחיר הממוצע.")
            return None

    def get_top_stores(self, num_stores=3):
        """מחזיר רשימה של החנויות המובילות עם המחיר שלהן."""
        stores_data = []
        try:
            # המתנה שרשימת החנויות תהיה גלויה
            store_elements = WebDriverWait(self.driver, 10).until(
                EC.presence_of_all_elements_located(self.STORE_LIST_CONTAINER)
            )

            for store_elem in store_elements:
                try:
                    name_elem = store_elem.find_element(*self.STORE_NAME)
                    price_elem = store_elem.find_element(*self.STORE_PRICE)

                    store_name = name_elem.text.strip()
                    price_text = price_elem.text.strip()
                    cleaned_price = re.sub(r'[^\d.]', '', price_text)

                    stores_data.append({
                        'name': store_name,
                        'price': float(cleaned_price) if cleaned_price else 0.0
                    })
                except NoSuchElementException:
                    print("אזהרה: לא ניתן למצוא שם או מחיר לחנות מסוימת.")
                    continue

            # ממיינים לפי מחיר מהנמוך לגבוה ובוחרים את ה-num_stores הראשונות
            stores_data.sort(key=lambda x: x['price'])
            return stores_data[:num_stores]

        except TimeoutException:
            print("שגיאה: רשימת החנויות לא נטענה בזמן.")
            return []
        except Exception as e:
            print(f"שגיאה כללית באחזור חנויות: {e}")
            return []


# --- 2. מחלקת ShoppingBot: מתאמת את הלוגיקה העסקית ---
class ShoppingBot:
    def __init__(self, driver_path):
        options = webdriver.ChromeOptions()
        # options.add_argument("--headless") # מפעיל את הדפדפן ללא ממשק גרפי (לפרודקשן)
        options.add_argument("--start-maximized")  # פותח בחלון מקסימלי
        self.driver = webdriver.Chrome(executable_path=driver_path, options=options)
        self.zap_page = ZapMarketPage(self.driver)

    def run_shopping_comparison(self, location, shopping_list):
        """מפעיל את תהליך השוואת הקניות."""
        try:
            self.zap_page.open_page()
            self.zap_page.set_location(location)

            # הוספת מוצרים
            for item in shopping_list:
                self.zap_page.add_product(item)

            # לחיצה על כפתור השוואת מחירים
            self.zap_page.click_compare_prices()

            # קבלת התוצאות
            avg_price = self.zap_page.get_average_price()
            top_stores = self.zap_page.get_top_stores(num_stores=3)

            # הצגת התוצאות
            print("\n--- סיכום תוצאות השוואת קניות ---")
            if avg_price is not None:
                print(f"מחיר ממוצע משוער לרשימת הקניות: {avg_price:.2f} שקלים")
            else:
                print("לא ניתן היה לאחזר את המחיר הממוצע.")

            if top_stores:
                print("\nשלוש החנויות הזולות ביותר הקרובות אליכם:")
                for i, store in enumerate(top_stores):
                    print(f"{i + 1}. {store['name']}: {store['price']:.2f} שקלים")
            else:
                print("לא ניתן היה לאחזר את רשימת החנויות הזולות.")

            print("\n--- סיום ---")

        except Exception as e:
            print(f"\nאירעה שגיאה קריטית במהלך השוואת הקניות: {e}")
            print("אנא בדקו את חיבור האינטרנט, נתיב הדרייבר, ואת מזהי האלמנטים בדף.")
        finally:
            self.driver.quit()  # סוגר את הדפדפן בסיום או במקרה של שגיאה


# --- שימוש בבוט הקניות שלנו ---
if __name__ == "__main__":
    my_shopping_list = [
        "חלב 3%",
        "לחם אחיד",
        "עגבניות",
        "מלפפונים",
        "קוטג' 5%",
        "שוקולד השחר"
    ]
    my_location = "בית שמש"  # או כל עיר/כתובת אחרת

    print("מתחיל את בוט הקניות החכם...")
    bot = ShoppingBot(CHROMEDRIVER_PATH)
    bot.run_shopping_comparison(my_location, my_shopping_list)