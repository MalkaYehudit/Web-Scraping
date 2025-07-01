from abc import ABC, abstractmethod

from abc import ABC, abstractmethod

class StoreScraper(ABC):
    def __init__(self, base_url):
        self.base_url = base_url

    @abstractmethod
    def scrape_products(self, products: list[dict]):

        pass
