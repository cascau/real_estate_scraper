# services/olx_scraper_full.py
import random
from typing import List
from core.requester import Requester
from models.offer_request import OfferRequest
from models.offer import Offer
from services.base_scraper import BaseScraper
from services.olx_scraper import OLXScraper
from services.olx_offer_parser import OLXURLOfferParser


class OLXFullScraper(BaseScraper):
    source_name = "olx"

    def __init__(self, requester: Requester):
        self.requester = requester
        self.scraper = OLXScraper(requester)
        self.parser = OLXURLOfferParser(requester)

    def get_offer_requests(self) -> List[OfferRequest]:
        vanzatori = ["private", "business"]
        proprietati = ["garsoniere", "apartamente", "case"]
        tranzactii = ["vanzare", "inchiriat"]
        camere = ["1-camera", "2-camere", "3-camere", "4-camere"]
        judete = ["bucuresti-ilfov"]
        orase = ["bucuresti"]

        reqs = [
            OfferRequest(self.source_name, vanzator, prop, tranz, cam, judet, oras)
            for vanzator in vanzatori
            for prop in proprietati
            for tranz in tranzactii
            for cam in camere
            for judet in judete
            for oras in orase
        ]
        random.shuffle(reqs)
        return reqs

    def get_all_offers(self, offer_request: OfferRequest, max_pages: int = 5) -> list[str]:
        return self.scraper.get_all_offers(offer_request, max_pages=max_pages)

    def parse_offer(self, url: str, offer_request: OfferRequest) -> Offer:
        return self.parser.parse_offer(url, offer_request)
