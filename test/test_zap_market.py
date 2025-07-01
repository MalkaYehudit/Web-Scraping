import unittest
import os
import undetected_chromedriver as uc
from scarpers.zap_market import ZapScraper

class TestZapScraper(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        options = uc.ChromeOptions()
        options.add_argument("--headless")
        cls.driver = uc.Chrome(options=options)
        print("navigator.webdriver =", cls.driver.execute_script("return navigator.webdriver"))
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

        if len(results) == 0:
            screenshot_path = os.path.join(os.getcwd(), "no_results_screenshot.png")
            self.scraper.driver.save_screenshot(screenshot_path)
            print("Screenshot saved to:", screenshot_path)

        self.assertGreater(len(results), 0, f"מוצר לא נמצא: {products[0]['name']}")
        self.assertIn("תנובה", results[0]["name"], f"שם המוצר לא כולל את המותג 'תנובה': {results[0]['name']}")

if __name__ == "__main__":
    unittest.main()
