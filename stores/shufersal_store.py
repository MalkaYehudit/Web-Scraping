# shufersal_store.py
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from core.online_store import OnlineStore
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import traceback

class ShufersalStore(OnlineStore):
    def login(self, username, password):
        try:
            self.driver.get("https://www.shufersal.co.il/")
            login_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.ID, "header-login-button"))
            )
            login_button.click()

            email_input = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "j_username"))
            )
            email_input.send_keys(username)

            password_input = self.driver.find_element(By.ID, "j_password")
            password_input.send_keys(password)

            submit_button = self.driver.find_element(By.ID, "loginFormSubmit")
            submit_button.click()

            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "header-my-account-button"))
            )
            print("התחברות הצליחה")
        except Exception as e:
            print("שגיאה בהתחברות:", e)
            traceback.print_exc()


    # def search_item(self, item_name):
    #     self.driver.get("https://www.shufersal.co.il/")  # כתובת חנות בפועל
    #     search_box = WebDriverWait(self.driver, 10).until(
    #         EC.presence_of_element_located((By.ID, "js-site-search-input"))
    #     )
    #     search_box.clear()
    #     search_box.send_keys(item_name)
    #     search_box.submit()

    def search_item(self, item_name):
        print(f"מחפש: {item_name}")
        self.driver.get("https://www.shufersal.co.il/")

        try:
            # המתנה שהדף יטען לחלוטין
            WebDriverWait(self.driver, 15).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )

            # חיפוש תיבת החיפוש והמתנה שתהיה לחיצה
            search_box = WebDriverWait(self.driver, 15).until(
                EC.element_to_be_clickable((By.ID, "js-site-search-input"))
            )

            search_box.clear()
            search_box.send_keys(item_name)
            search_box.send_keys(Keys.ENTER)

            # המתנה שתוצאות החיפוש יטענו - מתבסס על מה שמצאנו
            WebDriverWait(self.driver, 20).until(
                lambda driver: (
                        "search" in driver.current_url and
                        len(driver.find_elements(By.CSS_SELECTOR, ".tile")) > 0
                )
            )
            print("תוצאות החיפוש נטענו בהצלחה")

        except TimeoutException:
            print("בעיה במציאת תיבת החיפוש או תוצאות החיפוש לא נטענו")
            raise

    def add_to_cart(self, item_name):
        try:
            # חיפוש המוצר
            self.search_item(item_name)

            print("מחפש מוצרים בתוצאות...")

            # לפי הדיבאג שלך - יש 29 tiles, בואי נחפש את אלה שהם מוצרים אמיתיים
            tiles = WebDriverWait(self.driver, 10).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".tile"))
            )

            print(f"נמצאו {len(tiles)} tiles")

            # נמצא tile שמכיל מוצר (לא מלאי חסר וכו')
            product_tile = None
            for tile in tiles:
                try:
                    # בודק שהוא לא חסר במלאי או הודעה אחרת
                    tile_html = tile.get_attribute('outerHTML')
                    if ('miglog-prod-inStock' in tile_html and
                            'notOverlay' in tile_html and
                            len(tile.find_elements(By.CSS_SELECTOR, "button, .add")) > 0):
                        product_tile = tile
                        print("נמצא מוצר מתאים")
                        break
                except Exception:
                    continue

            if not product_tile:
                print("לא נמצא מוצר זמין. בודק את כל ה-tiles:")
                for i, tile in enumerate(tiles[:5]):  # רק 5 הראשונים לדיבאג
                    print(f"Tile {i + 1}: {tile.get_attribute('outerHTML')[:200]}...")
                return

            # גלילה לאלמנט והמתנה שיהיה גלוי
            print("מבצע גלילה למוצר...")
            self.driver.execute_script(
                "arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});",
                product_tile
            )

            # המתנה שהאלמנט יהיה גלוי לחלוטין
            WebDriverWait(self.driver, 10).until(
                EC.visibility_of(product_tile)
            )

            # חיפוש כפתור הוספה - לפי מבנה שופרסל
            add_button_selectors = [
                ".js-add-to-cart",
                "button.js-add-to-cart",
                ".add-to-cart",
                "button[data-add-to-cart]",
                ".btn-add-cart",
                ".addToCart",
                "button.addToCart"
            ]

            add_button = None
            for selector in add_button_selectors:
                try:
                    add_button = product_tile.find_element(By.CSS_SELECTOR, selector)
                    if add_button.is_displayed():
                        print(f"נמצא כפתור הוספה: {selector}")
                        break
                except NoSuchElementException:
                    continue

            # אם לא נמצא כפתור ספציפי, נחפש כל כפתור
            if not add_button:
                try:
                    buttons = product_tile.find_elements(By.TAG_NAME, "button")
                    for btn in buttons:
                        if (btn.is_displayed() and
                                ("הוסף" in btn.text or "add" in btn.text.lower() or
                                 "הוספה" in btn.get_attribute('title') or
                                 "cart" in btn.get_attribute('class').lower())):
                            add_button = btn
                            print(f"נמצא כפתור עם טקסט/class: {btn.text} / {btn.get_attribute('class')}")
                            break
                except Exception:
                    pass

            if add_button:
                try:
                    # המתנה שהכפתור יהיה לחיץ
                    WebDriverWait(self.driver, 10).until(
                        EC.element_to_be_clickable(add_button)
                    )

                    # ניסיון לחיצה רגילה
                    add_button.click()
                    print(f"המוצר '{item_name}' נוסף לעגלה!")

                    # המתנה לאישור הוספה
                    try:
                        WebDriverWait(self.driver, 5).until(
                            lambda driver: (
                                    "נוסף" in driver.page_source or
                                    "added" in driver.page_source.lower() or
                                    len(driver.find_elements(By.CSS_SELECTOR,
                                                             ".cart-count, .notification, .success, .added, .cart-badge")) > 0
                            )
                        )
                        print("אישור הוספה לעגלה התקבל!")
                        self.check_and_replace_with_promo()
                    except TimeoutException:
                        print("לא התקבל אישור ברור, אבל הלחיצה בוצעה")

                except Exception as click_error:
                    print(f"בעיה בלחיצה רגילה: {click_error}")
                    try:
                        # ניסיון לחיצה עם JavaScript
                        self.driver.execute_script("arguments[0].click();", add_button)
                        print(f"המוצר '{item_name}' נוסף לעגלה (JavaScript)!")

                        # המתנה לאישור הוספה
                        try:
                            WebDriverWait(self.driver, 5).until(
                                lambda driver: (
                                        "נוסף" in driver.page_source or
                                        "added" in driver.page_source.lower() or
                                        len(driver.find_elements(By.CSS_SELECTOR,
                                                                 ".cart-count, .notification, .success, .added, .cart-badge")) > 0
                                )
                            )
                            print("אישור הוספה לעגלה התקבל!")
                            self.check_and_replace_with_promo()

                        except TimeoutException:
                            print("לא התקבל אישור ברור, אבל הלחיצה בוצעה")

                    except Exception as js_error:
                        print(f"כישלון גם בלחיצה עם JavaScript: {js_error}")
            else:
                print("לא נמצא כפתור הוספה לעגלה")
                print("HTML של המוצר לדיבאג:")
                print(product_tile.get_attribute('outerHTML')[:500])

        except Exception as e:
            print(f"שגיאה כללית בהוספת מוצר: {e}")
            traceback.print_exc()

    def check_and_replace_with_promo(self):
        try:
            print("בודק אם קיימת הודעה חוסמת עם כפתור סגירה...")

            try:
                close_button = WebDriverWait(self.driver, 5).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, "button.btnClose"))
                )
                print("נמצא כפתור X לסגירת ההודעה – לוחץ עליו...")
                close_button.click()

                # המתנה קלה לוודא סגירה
                WebDriverWait(self.driver, 5).until_not(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "button.btnClose"))
                )
                print("ההודעה נסגרה בהצלחה")

            except TimeoutException:
                print("לא נמצאה הודעה חוסמת – ממשיך כרגיל")

            print("לוחץ על כפתור העגלה...")

            cart_icon = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, 'img[alt="הסל שלי"]'))
            )
            self.driver.execute_script("arguments[0].scrollIntoView(true);", cart_icon)
            cart_icon.click()
            print("נלחץ כפתור העגלה")

            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div.miglog-prod-promo"))
            )
            print("העגלה נטענה – מחפש 'החלף וחסוך'")

            promo_divs = self.driver.find_elements(By.CSS_SELECTOR, "div.miglog-prod-promo")
            clicked = False
            for div in promo_divs:
                try:
                    span = div.find_element(By.CSS_SELECTOR, "span")
                    if "החלף וחסוך" in span.text:
                        self.driver.execute_script("arguments[0].scrollIntoView(true);", div)
                        WebDriverWait(self.driver, 5).until(EC.element_to_be_clickable(div))
                        div.click()
                        print("נלחץ כפתור 'החלף וחסוך'")
                        clicked = True
                        break
                except NoSuchElementException:
                    continue

            if not clicked:
                print("לא נמצא כפתור 'החלף וחסוך'")
                return

            print("ממתין לכפתור 'לבחירה'...")
            choose_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "a.js-replacing-btn"))
            )
            self.driver.execute_script("arguments[0].scrollIntoView(true);", choose_button)
            choose_button.click()
            print("נלחץ כפתור 'לבחירה' להצגת מוצרים חלופיים")

        except Exception as e:
            print(f"שגיאה כללית במהלך החלפה: {e}")
