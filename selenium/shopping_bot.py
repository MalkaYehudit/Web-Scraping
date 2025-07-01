from zap_market import ZapMarketPage
from selenium import webdriver
from selenium.webdriver.chrome.service import Service

ZAP_MARKET_URL = "https://www.zapmarket.co.il/"
CHROMEDRIVER_PATH = 'C:\Program Files\chromedriver-win64/chromedriver.exe'




class ShoppingBot:
    def __init__(self, driver_path):
        options = webdriver.ChromeOptions()
        # options.add_argument("--headless")
        options.add_argument("--start-maximized")
        service = Service(executable_path=driver_path)
        self.driver = webdriver.Chrome(service=service, options=options)

        self.zap_page = ZapMarketPage(self.driver)

    def run_shopping_comparison(self, location, shopping_list):
        try:
            self.zap_page.open_page(ZAP_MARKET_URL)
            self.zap_page.set_location(location)

            for item in shopping_list:
                self.zap_page.add_product(item)

            self.zap_page.click_compare_prices()

            avg_price = self.zap_page.get_average_price()
            top_stores = self.zap_page.get_top_stores(num_stores=3)

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
        finally:
            self.driver.quit()


# --- נקודת הפעלה של הבוט ---
if __name__ == "__main__":
    my_shopping_list = [
        "חלב תנובה",
        "לחם אחיד פרוס",
        "עגבניות",
        "מלפפונים",
        "קוטג' 5%",
        "שוקולד השחר"
    ]
    my_location = "בית שמש"

    print("מתחיל את בוט הקניות החכם...")
    bot = ShoppingBot(CHROMEDRIVER_PATH)
    bot.run_shopping_comparison(my_location, my_shopping_list)
