import unittest
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from scarpers.zap_market import ZapScraper

class TestZapScraper(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        cls.driver = webdriver.Chrome(options=chrome_options)
        cls.scraper = ZapScraper(cls.driver)

    @classmethod
    def tearDownClass(cls):
        cls.driver.quit()

    def test_chalav_tnuva(self):
        products = [
            {
                "name": "חלב תנובה 3%",
                "brand": "תנובה",
                "weight": 1,
                "weight_unit": "ליטר"
            }
        ]
        results = self.scraper.scrape_products(products)

        # במקרה של כשל, לצלם צילום מסך לעיון
        if len(results) == 0:
            screenshot_path = os.path.join(os.getcwd(), "no_results_screenshot.png")
            self.scraper.driver.save_screenshot(screenshot_path)
            print(f"📸 Screenshot saved to: {screenshot_path}")

        self.assertGreater(len(results), 0, f"❌ לא נמצאו תוצאות עבור המוצר: {products[0]['name']}")
        self.assertIn("תנובה", results[0]["name"], f"❌ שם המוצר לא כולל את המותג 'תנובה': {results[0]['name']}")

if __name__ == "__main__":
    unittest.main()
