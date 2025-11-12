# services/base_scraper.py
from abc import ABC, abstractmethod
from typing import List
from models.offer_request import OfferRequest
from models.offer import Offer

class BaseScraper(ABC):
    source_name: str

    @abstractmethod
    def get_offer_requests(self) -> List[OfferRequest]:
        pass

    @abstractmethod
    def get_all_offers(self, offer_request: OfferRequest, max_pages: int = 1) -> list[str]:
        pass

    @abstractmethod
    def parse_offer(self, url: str, offer_request: OfferRequest) -> Offer:
        pass
