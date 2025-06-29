from scarpers.shufersal_scraper import ShufersalScraper
# from scrapers.rami_levy_scraper import RamiLevyScraper

def get_all_prices(product_name):
    scrapers = [
        ShufersalScraper(),
        # RamiLevyScraper(),
        # תוסיפי כאן עוד סקרייפרים
    ]

    results = []

    for scraper in scrapers:
        try:
            products = scraper.scrape_product(product_name)
            results.extend(products)
        except Exception as e:
            print(f"שגיאה בסקרייפר {scraper.__class__.__name__}: {e}")

    # נניח שהמבנה הוא [{'name': 'לחם אחיד', 'price': 5.90, 'store': 'שופרסל'}, ...]
    results.sort(key=lambda item: item['price'])
    return results
