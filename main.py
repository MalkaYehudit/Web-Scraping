import requests
from bs4 import BeautifulSoup
from models.product import Product
#
# from scrapers.shukcity_scraper import ShukCityScraper
# if __name__ == "__main__":
#     scraper = ShukCityScraper()
#     results = scraper.scrape_product("מים")
#     print(f"התקבלו {len(results)} מוצרים")
#     for product in results:
#         print(product)

# from scrapers.rami_levy_scraper import RamiLevyScraper
# if __name__ == "__main__":
#     scraper = RamiLevyScraper()
#     results = scraper.scrape_product("מים")
#     print(f"התקבלו {len(results)} מוצרים")
#     for product in results:
#         print(product)

import sys
import os


from scarpers.victory_scraper import  VictoryScraper
def main():
    scraper = VictoryScraper()
    search_term = input("הכנס שם מוצר לחיפוש (למשל: חלב): ")
    products = scraper.scrape_product(search_term)

    if not products:
        print("לא נמצאו מוצרים.")
    else:
        print(f"\n📦 נמצאו {len(products)} מוצרים:\n")
        for product in products:
            print(product)

if __name__ == "__main__":
    main()
