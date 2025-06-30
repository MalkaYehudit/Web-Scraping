# import requests
# from bs4 import BeautifulSoup
# from models.product import Product
# from scarpers.shukcity_scraper import ShukCityScraper
#
# def print_product(product: Product):
#     print(f"מוצר: {product.name}")
#     print(f"מחיר: {product.get_formatted_price()}")
#     if product.brand:
#         print(f"יצרן: {product.brand}")
#     print(f"חנות: {product.store}")
#     if product.quantity:
#         print(f"כמות: {product.quantity}")
#     if product.get_unit_price_display():
#         print(f"מחיר ליחידה: {product.get_unit_price_display()}")
#     if product.description:
#         print(f"תיאור: {product.description}")
#     print("-" * 40)
#
# if __name__ == "__main__":
#     scraper = ShukCityScraper()
#     results = scraper.scrape_product("מים")
#     print(f"התקבלו {len(results)} מוצרים:\n")
#     for product in results:
#         print_product(product)
#





# from scarpers.rami_levy_scraper import RamiLevyScraper
# if __name__ == "__main__":
#     scraper = RamiLevyScraper()
#     results = scraper.scrape_product("מים")
#     print(f"התקבלו {len(results)} מוצרים")
#     for product in results:
#         print(product)
#
# from scarpers.ybitan_scraper import YbitanScraper
# from models.product import Product
#
# if __name__ == "__main__":
#     scraper = YbitanScraper()
#
#
#     product_to_search = "מים"
#
#     print(f"=== חיפוש מוצר: {product_to_search} ===")
#
#     products = scraper.search_products(product_to_search)
#
#     if products:
#         print(f"נמצאו {len(products)} מוצרים:")
#         print("-" * 50)
#
#         for i, product in enumerate(products, 1):
#             print(f"{i}. {product.name}")
#             print(f"   מחיר: {product.price}₪")
#
#             if product.brand:
#                 print(f"   מותג: {product.brand}")
#
#             if product.quantity:
#                 print(f"   כמות: {product.quantity}")
#
#             if hasattr(product, 'display_info') and product.display_info:
#                 print(f"   {product.display_info}")
#
#             print("-" * 30)
#     else:
#         print(f"לא נמצאו מוצרים עבור '{product_to_search}'")
#         print("נסה:")
#         print("1. לוודא שהמוצר קיים באתר")
#         print("2. לנסות שם מוצר אחר")
#         print("3. לבדוק את החיבור לאינטרנט")
#
#
# import unittest
# import os
# import undetected_chromedriver as uc
# from scarpers.zap_market import ZapScraper
# import time
#
# class TestZapScraper(unittest.TestCase):
#
#     @classmethod
#     def setUpClass(cls):
#         print("🚀 מעלה את הדפדפן עם הגדרות משופרות...")
#
#         options = uc.ChromeOptions()
#
#         # הגדרות נגד זיהוי אוטומציה
#         options.add_argument(
#             "--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
#         options.add_argument("--no-sandbox")
#         options.add_argument("--disable-dev-shm-usage")
#         options.add_argument("--disable-blink-features=AutomationControlled")
#         # options.add_experimental_option("excludeSwitches", ["enable-automation"])
#         # options.add_experimental_option('useAutomationExtension', False)
#
#         # הגדרות נוספות ליציבות
#         options.add_argument("--disable-extensions")
#         options.add_argument("--disable-plugins")
#         options.add_argument("--disable-images")  # מאיץ טעינה
#         # הסרתי את --disable-javascript כי זה עלול לגרום לטעינה לקויה או חסימה באתר
#         # options.add_argument("--disable-javascript")
#         options.add_argument("--window-size=1920,1080")
#
#         # הגדרות זיכרון
#         options.add_argument("--max_old_space_size=4096")
#         options.add_argument("--memory-pressure-off")
#
#         # הסרת headless לבדיקה ויזואלית
#         # options.add_argument("--headless")
#
#         try:
#             cls.driver = uc.Chrome(options=options, version_main=None)  # אוטו-זיהוי גרסה
#
#             # הגדרות נוספות אחרי יצירת הדרייבר
#             cls.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
#
#             print("✅ דפדפן הופעל בהצלחה")
#             print(f"✅ webdriver status: {cls.driver.execute_script('return navigator.webdriver')}")
#             print(f"✅ user agent: {cls.driver.execute_script('return navigator.userAgent')}")
#
#             cls.scraper = ZapScraper(cls.driver)
#
#         except Exception as e:
#             print(f"❌ כישלון בהפעלת הדפדפן: {e}")
#             raise
#
#     @classmethod
#     def tearDownClass(cls):
#         print("🧹 סוגר את הדפדפן...")
#         try:
#             if hasattr(cls, 'driver'):
#                 cls.driver.quit()
#                 print("✅ דפדפן נסגר בהצלחה")
#         except Exception as e:
#             print(f"⚠️ בעיה בסגירת הדפדפן: {e}")
#
#     def setUp(self):
#         """הכנה לפני כל טסט"""
#         print(f"\n{'=' * 50}")
#         print(f"מתחיל טסט חדש...")
#         time.sleep(2)  # מנוחה בין טסטים - ייבוא המודול time מונע שגיאה
#
#     def test_chalav_tnuva(self):
#         products = [
#             {
#                 "name": "חלב תנובה",
#                 "brand": "תנובה",
#                 "weight": 1,
#                 "weight_unit": "ליטר"
#             }
#         ]
#
#         print(f"🔬 מבצע בדיקה עבור: {products[0]['name']}")
#
#         if not self.scraper.is_driver_alive():
#             self.fail("❌ הדרייבר לא פעיל לפני התחלת הטסט")
#
#         results = self.scraper.scrape_products(products)
#
#         self.scraper.save_screenshot("final_test_chalav")
#
#         if len(results) == 0:
#             print("❌ לא נמצאו תוצאות - בודק אם זה בגלל חסימה")
#             try:
#                 self.scraper.driver.get("https://www.google.com")
#                 print("✅ הגישה לגוגל עובדת - הבעיה ספציפית לזאפ")
#             except:
#                 print("❌ בעיה כללית בחיבור לאינטרנט")
#
#         if len(results) > 0:
#             print(f"✅ נמצאו {len(results)} תוצאות")
#             self.assertIn("תנובה", results[0]["name"],
#                           f"❌ שם המוצר לא כולל את המותג 'תנובה': {results[0]['name']}")
#         else:
#             print("⚠️ לא נמצאו תוצאות - יתכן שהאתר חוסם")
#
#     def test_gvina_tuv_taam(self):
#         products = [
#             {
#                 "name": "גבינה לבנה 5%",
#                 "brand": "טוב טעם",
#                 "weight": 250,
#                 "weight_unit": "גרם"
#             }
#         ]
#
#         print(f"🔬 מבצע בדיקה עבור: {products[0]['name']}")
#
#         if not self.scraper.is_driver_alive():
#             self.fail("❌ הדרייבר לא פעיל לפני התחלת הטסט")
#
#         results = self.scraper.scrape_products(products)
#
#         self.scraper.save_screenshot("final_test_gvina")
#
#         if len(results) > 0:
#             print(f"✅ נמצאו {len(results)} תוצאות")
#             self.assertIn("גבינה", results[0]["name"],
#                           f"❌ שם המוצר לא כולל את המילה 'גבינה': {results[0]['name']}")
#         else:
#             print("⚠️ לא נמצאו תוצאות - יתכן שהאתר חוסם")
#
#     def test_basic_connectivity(self):
#         print("🔗 בודק חיבור בסיסי לאתר...")
#
#         try:
#             if not self.scraper.is_driver_alive():
#                 self.fail("❌ הדרייבר לא פעיל")
#
#             success = self.scraper.load_homepage_with_retry()
#             self.assertTrue(success, "❌ כישלון בטעינת דף הבית")
#
#             current_url = self.scraper.driver.current_url
#             print(f"✅ URL נוכחי: {current_url}")
#
#             title = self.scraper.driver.title
#             print(f"✅ כותרת העמוד: {title}")
#
#         except Exception as e:
#             self.fail(f"❌ בעיה בחיבור בסיסי: {e}")
#
#
# if __name__ == "__main__":
#     unittest.main(verbosity=2)
#
# from selenium import webdriver
# from selenuim.shufersal_site import ShufersalSite, Product, CustomerInfo, PaymentInfo
#  import time
#
# # הפעלת דפדפן
# driver = webdriver.Chrome()
#
# # יצירת מופע
# shufersal = ShufersalSite(driver)
#
# # פתיחת אתר
# if shufersal.open_site():
#     if shufersal.set_delivery_location("תל אביב, הרצל 10"):
#         products = shufersal.search_product("חלב")
#         if products:
#             shufersal.add_to_cart(products[0], quantity=1)
#             shufersal.view_cart()
#             if shufersal.proceed_to_checkout():
#                 customer = CustomerInfo(
#                     first_name="טסט",
#                     last_name="בדיקה",
#                     email="test@example.com",
#                     phone="0500000000",
#                     address="הרצל 10",
#                     city="תל אביב",
#                     zip_code="12345"
#                 )
#                 payment = PaymentInfo(
#                     card_number="1234123412341234",  # לא אמיתי
#                     expiry_month="12",
#                     expiry_year="2027",
#                     cvv="123",
#                     card_holder_name="טסט בדיקה"
#                 )
#
#                 if shufersal.fill_customer_info(customer):
#                     if shufersal.fill_payment_info(payment):
#                         order_summary = shufersal.complete_purchase()
#                         print(order_summary)
#
# # המתנה לצפייה
# time.sleep(10)
# driver.quit()
#


#
# from selenium import webdriver
# from stores.shufersal_store import ShufersalStore
# import time
# print("פותח דפדפן...")
#
# driver = webdriver.Chrome()  # ודא ש-Chromedriver מותקן
# store = ShufersalStore(driver)
#
# print("מריץ חיפוש...")
#
# # store.search_item("גבינה צהובה עמק 28 400 גר")  # לדוגמה – חיפוש חלב
# store.add_to_cart("גבינה צהובה עמק 28 400 גר")
#
# print("המתנה לסגירה")
# input("לחץ אנטר לסגור את הדפדפן")
# driver.quit()

# הרצת דימוי משתמש ברמי לוי
from selenium import webdriver
from stores.rami_levy_store import RamiLevyStore
from dotenv import load_dotenv
import os
import traceback

print("📦 טוען קובץ .env...")
load_dotenv()

username = os.getenv("RAMI_LEVY_USER")
password = os.getenv("RAMI_LEVY_PASS")

if not username or not password:
    raise Exception("❌ חסר ערך ל־RAMI_LEVY_USER או RAMI_LEVY_PASS בקובץ .env")

print("🚀 מפעיל את הדפדפן...")
driver = webdriver.Chrome()

try:
    print("🌐 יוצר מופע של החנות רמי לוי...")
    store = RamiLevyStore(driver)

    print("🔐 מתחבר עם שם משתמש וסיסמה...")
    store.login(username, password)

    print("✅ התחברות הסתיימה בהצלחה.")
except Exception as e:
    print(f"❌ שגיאה במהלך ההרצה: {e}")
    traceback.print_exc()
finally:
    print("🧹 סוגר את הדפדפן...")
    input("לחץ אנטר כדי לסגור את הדפדפן ולהסיים...")
    driver.quit()