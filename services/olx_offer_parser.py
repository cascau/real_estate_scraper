import re
from datetime import datetime
import requests

from bs4 import BeautifulSoup

from core.requester import Requester
from db.location_repository import LocationRepository
from db.postgres_client import PostgresClient
from models.location import Location
from models.offer import Offer
from models.offer_request import OfferRequest
from utils.utils import get_geolocation_url
from core.logger_config import setup_logger

logger = setup_logger(__name__)


class OLXURLOfferParser:
    """ Extracts data from a single olx offer page"""

    def __init__(self, requester: Requester):
        self.requester = requester
        self.location_repository = LocationRepository(PostgresClient())

    def parse_offer(self, url: str, request: OfferRequest) -> Offer:
        logger.info(f"Parsing offer {url}")

        html = self.requester.get(url)
        soup = BeautifulSoup(html.content, "html.parser")

        specs = self.extract_specs_dict(soup)
        details = self.get_offer_details(specs)

        offer = Offer(url=url, sursa="olx")

        offer.titlu = self.get_title(soup)
        offer.pret = self.get_price(soup)

        offer.judet = request.judet
        offer.oras = request.oras
        offer.zona = self.get_zona(soup)

        geolocation: Location = self.get_geolocation(offer)
        offer.lat = geolocation.lat if geolocation and geolocation.lat else None
        offer.lng = geolocation.lng if geolocation and geolocation.lng else None

        offer.tip_proprietate = request.proprietate
        offer.tip_tranzactie = request.tranzactie
        offer.tip_vanzator = details.get("tip_vanzator") or request.vanzator

        offer.descriere = self.get_description(soup)
        offer.data_postarii = datetime.now()

        offer.suprafata = details.get("suprafata").replace(" m²", "") if details.get("suprafata") else None
        offer.numar_camere = details.get("numar_camere") or request.camere
        offer.etaj = details.get("etaj")
        offer.compartimentare = details.get("compartimentare")
        offer.an_constructie = details.get("an_constructie")

        offer.imagini = self.get_imagini(soup)

        return offer

    def get_geolocation_query(self, offer: Offer):
        oras = f",{offer.oras}" if offer.oras else ""
        zona = f",{offer.zona}" if offer.zona else ""
        return f"Romania{oras}{zona}"

    def get_geolocation(self, offer: Offer) -> Location | None:
        existing_geolocation = self.location_repository.find_location_by_judet_and_zona(offer)
        if existing_geolocation:
            return existing_geolocation

        query = self.get_geolocation_query(offer)
        url = get_geolocation_url(query)
        response = requests.get(url)
        json = response.json()[0] if response.status_code == 200 and len(response.json()) > 0 else None
        if not json:
            return None
        location: Location = Location(offer.judet, offer.zona, json["lat"], json["lon"])
        return self.location_repository.save_location(location)

    def get_title(self, soup: BeautifulSoup):
        title_tag = soup.select_one('div[data-cy="offer_title"]')
        return title_tag.get_text(strip=True) if title_tag else None

    def get_price(self, soup: BeautifulSoup):
        price_tag = soup.select_one('[data-testid="ad-price-container"]')
        if not price_tag:
            return None
        price_str = price_tag.get_text()
        price_str = re.sub("[^0-9.]", "", price_str)
        return int(price_str)

    def get_description(self, soup: BeautifulSoup):
        desc_tag = soup.select_one('div[data-cy="ad_description"]')
        return desc_tag.get_text(strip=True) if desc_tag else None

    def get_specifications_list(self, soup: BeautifulSoup):
        labels_tag = soup.select_one('div[data-testid="ad-parameters-container"]')
        return labels_tag.contents

    def extract_specs_dict(self, soup: BeautifulSoup) -> dict:
        specs = {}
        spec_tags = soup.select('div[data-testid="ad-parameters-container"] p')
        for tag in spec_tags:
            text = tag.get_text(strip=True)
            if ':' in text:
                key, value = map(str.strip, text.split(':', 1))
                specs[key] = value
            else:
                specs[text.strip()] = True
        return specs

    def get_offer_details(self, specs: dict):
        return {
            "an_constructie": specs.get("An constructie"),
            "etaj": specs.get("Etaj"),
            "compartimentare": specs.get("Compartimentare"),
            "suprafata": specs.get("Suprafata utila"),
            "numar_camere": specs.get("Numar camere"),
            "tip_vanzator": "private" if specs.get("Persoana fizica") else "business"
        }

    def get_imagini(self, soup: BeautifulSoup):
        imgs = []
        slide_show = soup.select('div[data-cy="adPhotos-swiperSlide"] > div > img')
        for slide in slide_show:
            imgs.append(slide['src'])
        return imgs

    def get_zona(self, soup: BeautifulSoup):
        breadcrumbs = soup.select('ol[data-testid="breadcrumbs"] > li')
        crumb = breadcrumbs.pop()
        if not crumb:
            return None
        zone = crumb.get_text(strip=True).split(" - ")
        return zone.pop().strip() if zone else None
