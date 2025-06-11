from abc import ABC, abstractmethod
#TODO: Remember 2 blank lines after moles import


class StoreScraper(ABC):
    # TODO: Remember blank line after class declaration

    def __init__(self, base_url):
        # TODO: Add to init an argument of type Store (create abstract Store class with name and URL, and optional description)
        self.base_url = base_url

    # TODO: Split scrape_product function into 2 functions: first one will be load_data that returns data object, second one will be get_product_price
    @abstractmethod
    def scrape_product(self, product_name):
        pass