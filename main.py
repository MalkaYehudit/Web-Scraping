from scrapers.shukcity_scraper import ShukCityScraper
# from scrapers.haziHinam_scraper import HaziHinamScraper
#
# if __name__ == "__main__":
#     scraper = HaziHinamScraper()
#     results = scraper.scrape_product("לחם פרוס")
#     print(f"התקבלו {len(results)} מוצרים")
#     for product in results:
#         print(product)
#

from scrapers.haziHinam_scraper import HaziHinamScraper

if __name__ == "__main__":
    scraper = HaziHinamScraper()
    results = scraper.scrape_product("חלב")
    print(f"התקבלו {len(results)} מוצרים")
    for product in results:
        print(product)
