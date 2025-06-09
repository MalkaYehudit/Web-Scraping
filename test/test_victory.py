import requests
import webbrowser
import os
import json
from scarpers.victory_scraper import VictoryScraper

# שלב 1: שמירת תגובת JSON לבדיקה ידנית
url = "https://www.victoryonline.co.il/v2/retailers/1470/branches/2331/products"
params = {
    "appId": 4,
    "size": 16,
    "languageId": 1,
    "isSearch": "true",
    "from": 0,
    "filters": '{"must":{"exists":["family.id","family.categoriesPaths.id","branch.regularPrice"],"term":{"branch.isActive":true,"branch.isVisible":true}},"mustNot":{"term":{"branch.regularPrice":0,"branch.isOutOfStock":true}}}',
    "query": "חלב"
}
headers = {'User-Agent': 'Mozilla/5.0'}

response = requests.get(url, params=params, headers=headers)

with open("victory.json", "w", encoding="utf-8") as f:
    json.dump(response.json(), f, ensure_ascii=False, indent=2)

print("✅ הקובץ victory.json נשמר בהצלחה!")

# שלב 2: פתיחה עם תוכנת ברירת מחדל (נניח Notepad או דפדפן JSON)
path = r"D:\קבצי משתמש לא לגעת!!!\Documents\python exercises\food_scraper_project\test\victory.json"
webbrowser.open('file://' + os.path.realpath(path))


def test_scrape():
    scraper = VictoryScraper()
    results = scraper.scrape_product("חלב")
    for product in results:
        print(product)

if __name__ == "__main__":
    test_scrape()
