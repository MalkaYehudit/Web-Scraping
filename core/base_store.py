from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from core.online_store import OnlineStore

class BaseStore(OnlineStore):

    # ✅ פונקציית login - מרוכזת אחת בלבד
    def login(self, username, password):
        print(f"🌐 טוען דף: {self.get_login_url()}")
        self.driver.get(self.get_login_url())

        self.open_login_modal()

        try:
            print("⌛ ממתין לשדות התחברות...")
            self.wait_for_element(self.get_username_selector())
            self.fill_input(self.get_username_selector(), username)
            self.fill_input(self.get_password_selector(), password)

            self.wait_and_click(self.get_submit_selector())

            # self.wait_until_disappear(self.get_username_selector())
            self.wait_for_element("div#user-box")
            print("✅ התחברות הצליחה")


        except TimeoutException:
            raise Exception("❌ שגיאה בהתחברות")

    # ✅ פונקציית ברירת מחדל לפתיחת מודל התחברות
    def open_login_modal(self):
        pass

    # ✅ פונקציות עזר כלליות לשימוש חוזר בכל תהליך (לא רק login)
    def wait_for_element(self, selector, timeout=10):
        return WebDriverWait(self.driver, timeout).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, selector))
        )

    def wait_and_click(self, selector, timeout=10):
        WebDriverWait(self.driver, timeout).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
        ).click()

    def fill_input(self, selector, value):
        self.driver.find_element(By.CSS_SELECTOR, selector).send_keys(value)

    def wait_until_disappear(self, selector, timeout=10):
        WebDriverWait(self.driver, timeout).until_not(
            EC.presence_of_element_located((By.CSS_SELECTOR, selector))
        )

    # ✅ פונקציות מופשטות שהמחלקות היורשות חייבות לממש
    def get_login_url(self):
        raise NotImplementedError

    def get_username_selector(self):
        raise NotImplementedError

    def get_password_selector(self):
        raise NotImplementedError

    def get_submit_selector(self):
        raise NotImplementedError
