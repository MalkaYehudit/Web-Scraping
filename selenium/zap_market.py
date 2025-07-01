from difflib import SequenceMatcher
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import re
import time


class ZapMarketPage:
    def __init__(self, driver):
        self.driver = driver

        # אלמנטים מרכזיים
        self.UPDATE_ADDRESS_BUTTON = (By.CSS_SELECTOR, '.updateAddressTxtSpan')
        self.ADDRESS_INPUT = (By.ID, "addressInput")
        self.FIRST_AUTOCOMPLETE_RESULT = (By.CSS_SELECTOR, '.pac-container .pac-item')
        self.CONFIRM_ADDRESS_BUTTON = (By.CSS_SELECTOR, '.confirmAddress')

        self.PRODUCT_SEARCH_INPUT = (By.CSS_SELECTOR, 'input[placeholder*="הקלד את שם המוצר"]')
        self.ADD_PRODUCT_BUTTON = (By.CSS_SELECTOR, 'button.add-product-button')
        self.ADD_BUTTON_HOVER = (By.CSS_SELECTOR, 'button.addButton')

        self.COMPARE_PRICES_BUTTON = (By.CSS_SELECTOR, 'div.floatingFullCart div.cartTxt')
        self.AVERAGE_PRICE_DISPLAY = (By.CSS_SELECTOR, "div.generalCartPriceRange span.ng-binding")

        #self.STORE_LIST_CONTAINER = (By.CSS_SELECTOR, "div.branchData")
       # self.STORE_NAME = (By.CSS_SELECTOR, "div.branchName.ng-binding")
       # self.STORE_PRICE = (By.CSS_SELECTOR, "div.branchCartPrice.ng-binding")

        self.STORE_LIST_CONTAINER = (By.CSS_SELECTOR, "div.branchData")  # עודכן
        self.STORE_NAME = (By.CSS_SELECTOR, "div.branchName")  # עודכן
        self.STORE_PRICE = (By.CSS_SELECTOR, "div.branchCartPrice")  # עודכן

    def wait_for_page_load(self, timeout=15):
        WebDriverWait(self.driver, timeout).until(
            lambda d: d.execute_script("return document.readyState") == "complete"
        )

    def scroll_to_bottom(self):
        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)

    def open_page(self, url):
        print(f"פותח את האתר: {url}")
        self.driver.get(url)
        self.wait_for_page_load()
        WebDriverWait(self.driver, 15).until(
            EC.presence_of_element_located(self.ADDRESS_INPUT)
        )
        print("האתר נטען בהצלחה.")

    def close_promo_if_exists(self):
        try:
            promo = WebDriverWait(self.driver, 3).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'div.promo-main-section'))
            )
            self.driver.execute_script("arguments[0].style.display='none';", promo)
            print("⚠️ באנר פרסומת הוסתר.")
        except TimeoutException:
            pass

    def set_location(self, location_text):
        print(f"מזין מיקום: '{location_text}'")
        try:
            update_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable(self.UPDATE_ADDRESS_BUTTON)
            )
            self.close_promo_if_exists()
            self.driver.execute_script("arguments[0].scrollIntoView();", update_button)
            self.driver.execute_script("arguments[0].click();", update_button)
            time.sleep(1)

            address_input = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable(self.ADDRESS_INPUT)
            )
            address_input.clear()
            address_input.send_keys(location_text)
            time.sleep(2)

            first_result = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable(self.FIRST_AUTOCOMPLETE_RESULT)
            )
            first_result.click()
            time.sleep(1)

            confirm_button = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located(self.CONFIRM_ADDRESS_BUTTON)
            )
            self.driver.execute_script("arguments[0].scrollIntoView();", confirm_button)
            self.driver.execute_script("arguments[0].click();", confirm_button)

            print("המיקום נבחר ואושר בהצלחה.")
            time.sleep(1)

        except TimeoutException:
            print("שגיאה: לא ניתן היה לעדכן ולאשר את המיקום.")
            raise

    def add_product(self, product_name):
        def find_best_match(name):
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, "a[href*='/model/']"))
            )
            product_links = self.driver.find_elements(By.CSS_SELECTOR, "a[href*='/model/']")
            best_match, best_ratio = None, 0
            for link in product_links:
                try:
                    text = link.text.strip()
                    if name in text:
                        return link, 1.0
                    ratio = SequenceMatcher(None, name, text).ratio()
                    if ratio > best_ratio:
                        best_match = link
                        best_ratio = ratio
                except:
                    continue
            return best_match, best_ratio

        try:
            print(f"📦 מנסה להוסיף את המוצר: {product_name}")
            wait = WebDriverWait(self.driver, 15)

            best_match, best_ratio = find_best_match(product_name)

            if not best_match or best_ratio < 0.3:
                print(f"🔄 מנסה התאמה מחדש לפי מילת מפתח מהמוצר '{product_name}'")
                simplified_name = product_name.split()[0]
                best_match, best_ratio = find_best_match(simplified_name)

            if not best_match or best_ratio < 0.3:
                raise Exception(f"לא נמצא קישור מתאים מספיק למוצר '{product_name}' (יחס התאמה {best_ratio:.2f})")

            self.driver.execute_script("arguments[0].scrollIntoView();", best_match)
            time.sleep(0.5)
            best_match.click()
            print(f"➡️ עבר לעמוד המוצר המתאים ביותר: התאמה {best_ratio:.2f}")

            add_to_cart_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//div[contains(@class, 'addBtn') and contains(text(), 'הוסף לסל')]")))
            self.driver.execute_script("arguments[0].scrollIntoView();", add_to_cart_button)
            add_to_cart_button.click()
            print("🛒 המוצר נוסף לעגלה")

            time.sleep(1)
            self.driver.back()
            time.sleep(1)

        except Exception as e:
            print(f"❌ שגיאה בהוספת מוצר {product_name}: {e}")

    def click_compare_prices(self):
        print("לוחץ על כפתור השוואת המחירים...")
        try:
            button = WebDriverWait(self.driver, 20).until(
                EC.element_to_be_clickable(self.COMPARE_PRICES_BUTTON)
            )
            self.driver.execute_script("arguments[0].scrollIntoView();", button)
            button.click()
            print("כפתור השוואת המחירים נלחץ.")

            WebDriverWait(self.driver, 20).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'div.branchData'))
            )
            print("תוצאות ההשוואה נטענו.")

        except Exception as e:
            print("שגיאה: כפתור השוואת המחירים לא נמצא או שהתוצאות לא נטענו בזמן.")
            raise e

    def get_average_price(self):
        try:
            avg_price_element = self.driver.find_element(*self.AVERAGE_PRICE_DISPLAY)
            price_text = avg_price_element.text.strip()
            match = re.findall(r'[\d.]+', price_text)
            if len(match) == 2:
                low, high = map(float, match)
                return (low + high) / 2
            elif len(match) == 1:
                return float(match[0])
            else:
                raise ValueError("לא נמצאו מספרים בתצוגת המחיר")
        except Exception as e:
            print(f"שגיאה: לא ניתן למצוא את המחיר הממוצע ישירות ({e}), מנסה לחשב מתוך החנויות...")
            stores = self.get_top_stores(num_stores=10)
            if not stores:
                return None
            total = sum(store['price'] for store in stores if store['price'] > 0)
            count = sum(1 for store in stores if store['price'] > 0)
            return round(total / count, 2) if count else None


    def get_top_stores(self, num_stores=3):

        stores_data = []
        try:
            self.scroll_to_bottom()
            time.sleep(2)

            store_elements = WebDriverWait(self.driver, 15).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.branchData"))
            )
            print(f"נמצאו {len(store_elements)} חנויות.")

            for index, store_elem in enumerate(store_elements):
                try:
                    name_elem = store_elem.find_element(By.CSS_SELECTOR, "div.branchDataRight > div.branchName")
                    price_elem = store_elem.find_element(By.CSS_SELECTOR, "div.branchDataLeft > div.branchCartPrice")

                    store_name = name_elem.get_attribute("textContent").strip()
                    price_text = price_elem.get_attribute("textContent").strip()

                    if not store_name or not price_text:
                        print(f"⚠️ חנות #{index + 1} חסרה שם או מחיר, מדלג.")
                        continue

                    print(f"📍 חנות: {store_name}, מחיר גולמי: {price_text}")

                    match = re.search(r'[\d.]+', price_text)
                    store_price = float(match.group()) if match else 0.0

                    stores_data.append({
                        'name': store_name,
                        'price': store_price
                    })

                except Exception as e:
                    print(f"❌ חנות #{index + 1} נכשלה: {e}")
                    continue

            valid_stores = [store for store in stores_data if store['price'] > 0]
            valid_stores.sort(key=lambda x: x['price'])

            print("✅ שלושת החנויות הזולות ביותר:")
            for s in valid_stores[:num_stores]:
                print(f"🏪 {s['name']} - ₪{s['price']}")

            return valid_stores[:num_stores]

        except TimeoutException:
            print("❌ רשימת החנויות לא נטענה בזמן.")
            return []
        except Exception as e:
            print(f"❌ שגיאה כללית באחזור חנויות: {e}")
            return []
