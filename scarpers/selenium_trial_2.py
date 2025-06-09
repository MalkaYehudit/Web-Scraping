# from selenium import webdriver
# from selenium.webdriver.common.by import By
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# import time # לצורך המתנה קצרה לצפייה בשינוי
#
# # נתיב ל-WebDriver שלך (לדוגמה, ChromeDriver)
# # ודא שה-WebDriver תואם לגרסת הדפדפן שלך
# driver_path = 'נתיב/ל-chromedriver.exe'  # *** שנה את הנתיב לנתיב הנכון בקובץ שלך ***
# driver = webdriver.Chrome(executable_path=driver_path)
#
# try:
#     # נווט לאתר
#     driver.get("https://www.zapmarket.co.il/")
#
#     # הגדר המתנה מפורשת (explicit wait)
#     # זה חשוב כדי לוודא ששדה הקלט נטען וזמין לפני שננסה לקיים איתו אינטראקציה.
#     wait = WebDriverWait(driver, 10) # המתן עד 10 שניות
#
#     # 1. מצא את שדה הקלט לפי ה-ID שלו
#     # ייתכן ששדה הקלט לא יהיה גלוי או זמין מיידית בטעינת הדף,
#     # לכן נחפש אותו לאחר טעינת הדף ונוודא שהוא ניתן לאינטראקציה.
#     address_input_field = wait.until(EC.element_to_be_clickable((By.ID, "AddressInput")))
#
#     # 2. נקה כל ערך קיים בשדה (אופציונלי, אך מומלץ)
#     address_input_field.clear()
#
#     # 3. הזן את הערך החדש "בית שמש"
#     address_input_field.send_keys("בית שמש")
#
#     print("הערך בשדה 'AddressInput' עודכן בהצלחה ל'בית שמש'.")
#
#     # המתן מספר שניות כדי שתוכל לראות את השינוי בדפדפן
#     time.sleep(5)
#
#     # ניתן לבצע פעולות נוספות כאן, לדוגמה, ללחוץ על כפתור חיפוש אם קיים
#
# except Exception as e:
#     print(f"אירעה שגיאה: {e}")
#
# finally:
#     # סגור את הדפדפן
#     driver.quit()