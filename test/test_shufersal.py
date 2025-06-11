import requests
import webbrowser
import os
# TODO: Do you need this code? if not - comment it
url = "https://www.shufersal.co.il/online/he/search?text=חלב"
headers = {'User-Agent': 'Mozilla/5.0'}

response = requests.get(url, headers=headers, verify=False)

with open("shufersal.html", "w", encoding="utf-8") as f:
    f.write(response.text)

print("✅ הקובץ shufersal.html נשמר בהצלחה!")


# TODO: change to relative path
path = r"D:\קבצי משתמש לא לגעת!!!\Documents\python exercises\food_scraper_project\test\shufersal.html"
webbrowser.open('file://' + os.path.realpath(path))

from scarpers.shufersal_scraper import ShufersalScraper
# TODO: please use unittest module here (ask GPT how) and validate product list is not empty
def test_scrape():
    scraper = ShufersalScraper()
    results = scraper.scrape_product("חלב")
    for product in results:
        print(product)

if __name__ == "__main__":
    test_scrape()
