import random
from typing import List

from core.requester import Requester
from models.offer import Offer
from models.offer_request import OfferRequest
from services.base_scraper import BaseScraper
from services.romimo_offer_parser import RomimoURLOfferParser
from services.romimo_scraper import RomimoScraper


class RomimoFullScraper(BaseScraper):
    source_name = "romimo"

    def __init__(self, requester: Requester):
        self.requester = requester
        self.scraper = RomimoScraper(requester)
        self.parser = RomimoURLOfferParser(requester)

    def get_offer_requests(self) -> List[OfferRequest]:
        vanzatori = ["private", "business"]
        proprietati = ["garsoniera", "apartamente", "case"]
        tranzactii = ["vanzare", "inchiriere"]
        camere = ["2-camere", "3-camere", "4-camere", "5-camere", "6-camere"]
        judete = ["bucuresti", "ilfov"]
        orase = ["bucuresti"]

        reqs = [
            OfferRequest(self.source_name, vanzator, prop, tranz, cam, judet, oras)
            for vanzator in vanzatori
            for prop in proprietati
            for tranz in tranzactii
            for cam in camere if prop != "case"
            for judet in judete
            for oras in orase
        ]
        random.shuffle(reqs)
        return reqs

    def get_all_offers(self, offer_request: OfferRequest, max_pages: int = 1) -> list[str]:
        return self.scraper.get_all_offers(offer_request, max_pages=max_pages)

    def parse_offer(self, url: str, offer_request: OfferRequest) -> Offer:
        return self.parser.parse_offer(url, offer_request)