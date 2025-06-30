from core.base_store import BaseStore
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class RamiLevyStore(BaseStore):

    def get_login_url(self):
        return "https://www.rami-levy.co.il/he"

    def get_username_selector(self):
        return "input#email"

    def get_password_selector(self):
        return "input#password"

    def get_submit_selector(self):
        return "button.focus-item.online-full-btn[aria-label='כניסה']"

    def open_login_modal(self):
        login_button_selector = "div#login-user"
        print("⌛ ממתין שהכפתור התחברות יהיה קליקבילי...")
        self.wait_and_click(login_button_selector)
        print("✅ נלחץ על כפתור ההתחברות")