from abc import ABC, abstractmethod
import requests

class BaseScraper(ABC):
    def __init__(self, headers: dict):
        self.headers = headers

    def fetch_page(self, url: str) -> str:
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        return response.text

    @abstractmethod
    def parse_results_page(self, html: str) -> list[str]:
        """Implement in child classes"""
        pass
