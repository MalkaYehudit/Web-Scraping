from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import TimeoutException, WebDriverException
from difflib import SequenceMatcher
import time
import os
import ssl

# ⛔ עקיפת בדיקת SSL – זמני בלבד
ssl._create_default_https_context = ssl._create_unverified_context


def safe_get(driver, url, retries=3, delay=5):
    for attempt in range(retries):
        try:
            driver.set_page_load_timeout(60)
            driver.get(url)
            return True
        except (TimeoutException, WebDriverException) as e:
            print(f"שגיאה בטעינת {url}, ניסיון {attempt+1} מתוך {retries}: {e}")
            time.sleep(delay)
    return False


class ZapScraper:
    def __init__(self, driver):
        self.base_url = "https://zapmarket.co.il"
        self.driver = driver
        self.wait = WebDriverWait(self.driver, 30)

    def safe_print(self, msg):
        try:
            print(str(msg).encode('ascii', errors='ignore').decode())
        except Exception:
            pass

    def close_popups(self):
        try:
            cookie_btn = self.wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, ".btn.btn-primary.cookie-close"))
            )
            cookie_btn.click()
        except:
            pass

        try:
            popup = self.driver.find_element(By.CLASS_NAME, "popup-close")
            popup.click()
        except:
            pass

    def scrape_products(self, product_objects):
        results = []
        for product in product_objects:
            if not safe_get(self.driver, self.base_url):
                self.safe_print(f"שגיאה: לא ניתן לטעון את {self.base_url} עבור {product['name']}")
                continue

            time.sleep(2)
            self.close_popups()

            try:
                self.search_product(product["name"])
                products = self.extract_products()

                self.safe_print(f"נמצאו {len(products)} מוצרים עבור: {product['name']}")
                match = self.find_best_product(products, product)

                if match:
                    self.safe_print(f"התאמה: {match['name']} במחיר {match['price']} ₪")
                    results.append(match)
                else:
                    self.safe_print(f"לא נמצאה התאמה עבור: {product['name']}")

            except Exception as e:
                self.safe_print(f"שגיאה בחיפוש מוצר: {product['name']}: {e}")
                screenshot_path = os.path.join(os.getcwd(), "search_error.png")
                self.driver.save_screenshot(screenshot_path)
                self.safe_print(f"צילום מסך נשמר: {screenshot_path}")
                continue

        return results

    def search_product(self, name):
        input_box = self.wait.until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, 'input[placeholder*="הקלד את שם המוצר"]'))
        )
        self.driver.execute_script("arguments[0].scrollIntoView(true);", input_box)
        time.sleep(1)
        input_box.clear()
        input_box.send_keys(name)
        input_box.send_keys(Keys.ENTER)
        time.sleep(5)  # זמן טעינה

    def extract_products(self):
        self.wait.until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, "productItem"))
        )
        product_elements = self.driver.find_elements(By.CLASS_NAME, "productItem")
        print(f"DEBUG: נמצאו {len(product_elements)} מוצרים בדף")

        extracted = []

        for el in product_elements:
            try:
                name = el.find_element(By.CSS_SELECTOR, ".productName a").text.strip()

                # כמות (אם קיימת)
                try:
                    quantity = el.find_element(By.CSS_SELECTOR, ".productCap span").text.strip()
                except:
                    quantity = "לא צויין"

                # שליפת המחיר הנמוך מתוך טווח המחירים
                try:
                    price_container = el.find_element(By.CSS_SELECTOR, ".productPriceRange")
                    price_spans = price_container.find_elements(By.CSS_SELECTOR, "span.ng-binding")
                    if not price_spans:
                        raise ValueError("מחיר לא נמצא")
                    price_text = price_spans[0].text.strip()  # המחיר הנמוך - הראשון ברשימה
                    if not price_text:
                        raise ValueError("מחיר ריק")
                    price = float(price_text.replace(",", "").strip())
                except Exception as e:
                    print("⚠️ שגיאה בשליפת מחיר:", e)
                    continue

                print(f"✅ נשלף: {name} | {quantity} | {price} ₪")

                extracted.append({
                    "name": name,
                    "quantity": quantity,
                    "price": price,
                    "element": el
                })

            except Exception as e:
                print("❌ שגיאה כללית בשליפה:", e)
                continue

        return extracted

    def find_best_product(self, products, user_product: dict):
        best_score = 0
        best_match = None

        for prod in products:
            score = 0
            score += SequenceMatcher(None, prod["name"], user_product.get("name", "")).ratio() * 3

            if user_product.get("brand") and user_product["brand"] in prod["name"]:
                score += 1.5

            if user_product.get("weight") and str(user_product["weight"]) in prod["quantity"]:
                score += 1

            if user_product.get("weight_unit") and user_product["weight_unit"] in prod["quantity"]:
                score += 1

            if score > best_score:
                best_score = score
                best_match = prod

        return best_match


# -------------------------------
# פונקציית main מחוץ לקלאס
# -------------------------------

def main():
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")  # הסר את השורה אם ברצונך לראות את הדפדפן

    service = Service(r"C:\Program Files\chromedriver-win64\chromedriver.exe")
    driver = webdriver.Chrome(service=service, options=options)
    scraper = ZapScraper(driver)

    try:
        products = [
            {
                "name": "חלב",
                "brand": "",
                "weight": 1,
                "weight_unit": "ליטר"
            }
        ]

        results = scraper.scrape_products(products)

        if not results:
            screenshot_path = os.path.join(os.getcwd(), "no_results_screenshot.png")
            driver.save_screenshot(screenshot_path)
            print(f"אין תוצאות. צילום מסך נשמר: {screenshot_path}")
        else:
            for product in results:
                print(f"✅ נמצא מוצר: {product['name']} - {product['price']} ₪")

    finally:
        driver.quit()


if __name__ == "__main__":
    main()
