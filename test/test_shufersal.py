import requests
import webbrowser
import os

url = "https://www.shufersal.co.il/online/he/search?text=חלב"
headers = {'User-Agent': 'Mozilla/5.0'}

response = requests.get(url, headers=headers, verify=False)

with open("shufersal.html", "w", encoding="utf-8") as f:
    f.write(response.text)

print("✅ הקובץ shufersal.html נשמר בהצלחה!")



path = r"D:\קבצי משתמש לא לגעת!!!\Documents\python exercises\food_scraper_project\test\shufersal.html"
webbrowser.open('file://' + os.path.realpath(path))

from scarpers.shufersal_scraper import ShufersalScraper

def test_scrape():
    scraper = ShufersalScraper()
    results = scraper.scrape_product("חלב")
    for product in results:
        print(product)

if __name__ == "__main__":
    test_scrape()
