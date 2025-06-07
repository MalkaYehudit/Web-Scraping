import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def test_victory_api():
    base_url = "https://www.victoryonline.co.il/api/v1/search/products"
    params = {
        "appId": 4,
        "size": 16,
        "languageId": 1,
        "isSearch": "true",
        "filters": '{"must":{"exists":["family.id","family.categoriesPaths.id","branch.regularPrice"],"term":{"branch.isActive":true,"branch.isVisible":true}},"mustNot":{"term":{"branch.regularPrice":0,"branch.isOutOfStock":true}}}'
    }
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Referer": "https://www.victoryonline.co.il/"
    }

    response = requests.get(base_url, params=params, headers=headers, verify=False)
    print("סטטוס:", response.status_code)
    print("תוכן התגובה (raw):")
    print(response.text)  # מדפיס את התגובה הגולמית

    try:
        data = response.json()
        print("=== JSON שהתקבל ===")
        print(data)
    except Exception as e:
        print("שגיאה בניתוח JSON:", e)

if __name__ == "__main__":
    test_victory_api()
