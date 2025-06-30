class OnlineStore:
    def __init__(self, driver):
        self.driver = driver

    def login(self, username, password):
        raise NotImplementedError

    def search_item(self, item_name):
        raise NotImplementedError

    def add_to_cart(self, item_name):
        raise NotImplementedError

    def checkout(self):
        raise NotImplementedError
#
# from abc import ABC, abstractmethod
#
# class OnlineStore(ABC):
#     def __init__(self, driver):
#         self.driver = driver
#
#     @abstractmethod
#     def login(self, username, password):
#         pass
#
#     @abstractmethod
#     def search_item(self, item_name):
#         pass
#
#     @abstractmethod
#     def add_to_cart(self, item_name):
#         pass
#
#     @abstractmethod
#     def checkout(self):
#         pass



# דוגמא לקוד ששני הביאה
#
# class StoreA(OnlineStore):
#     def login(self, username, password):
#         self.driver.get("https://store-a.com/login")
#         WebDriverWait(self.driver, 10).until(
#             EC.presence_of_element_located((By.ID, "username"))
#         ).send_keys(username)
#         self.driver.find_element(By.ID, "password").send_keys(password)
#         self.driver.find_element(By.ID, "login-button").click()
#
#     def search_item(self, item_name):
#         search_box = WebDriverWait(self.driver, 10).until(
#             EC.presence_of_element_located((By.ID, "search-box"))
#         )
#         search_box.send_keys(item_name)
#         search_box.submit()
#
#     def add_to_cart(self, item_name):
#         self.search_item(item_name)
#         WebDriverWait(self.driver, 10).until(
#             EC.presence_of_element_located((By.CLASS_NAME, "add-to-cart"))
#         ).click()
#
#     def checkout(self):
#         self.driver.get("https://store-a.com/cart")
#         WebDriverWait(self.driver, 10).until(
#             EC.presence_of_element_located((By.ID, "checkout-button"))
#         ).click()
#
