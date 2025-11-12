import re
from datetime import datetime

from bs4 import BeautifulSoup

from core.logger_config import setup_logger
from core.requester import Requester
from db.location_repository import LocationRepository
from db.postgres_client import PostgresClient
from models.location import Location
from models.offer import Offer
from models.offer_request import OfferRequest
from utils.utils import get_geolocation

logger = setup_logger(__name__)

breadcrumbs_selector = 'ol[data-testid="breadcrumbs"] > li'


def get_title(soup: BeautifulSoup):
    title_tag = soup.select_one('div[data-cy="offer_title"]')
    return title_tag.get_text(strip=True) if title_tag else None


def get_price(soup: BeautifulSoup):
    price_tag = soup.select_one('[data-testid="ad-price-container"]')
    if not price_tag:
        return None
    price_str = price_tag.get_text()
    price_str = re.sub("[^0-9.]", "", price_str)
    return int(price_str) if not price_str.isdigit() else None


def get_description(soup: BeautifulSoup):
    desc_tag = soup.select_one('div[data-cy="ad_description"]')
    return desc_tag.get_text(strip=True) if desc_tag else None


def extract_specs_dict(soup: BeautifulSoup) -> dict:
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


def get_specifications_list(soup: BeautifulSoup):
    labels_tag = soup.select_one('div[data-testid="ad-parameters-container"]')
    return labels_tag.contents


def get_offer_details(specs: dict):
    return {
        "an_constructie": specs.get("An constructie"),
        "etaj": specs.get("Etaj"),
        "compartimentare": specs.get("Compartimentare"),
        "suprafata": specs.get("Suprafata utila"),
        "numar_camere": specs.get("Numar camere"),
        "tip_vanzator": "private" if specs.get("Persoana fizica") else "business"
    }


def get_imagini(soup: BeautifulSoup):
    imgs = []
    slide_show = soup.select('div[data-cy="adPhotos-swiperSlide"] > div > img')
    for slide in slide_show:
        imgs.append(slide['src'])
    return imgs


def get_judet(soup: BeautifulSoup):
    breadcrumbs = soup.select(breadcrumbs_selector)
    crumb = breadcrumbs.pop()
    if not crumb:
        return None
    crumb = breadcrumbs.pop()
    if not crumb:
        return None
    crumb = breadcrumbs.pop()
    if not crumb:
        return None
    zone = crumb.get_text(strip=True).split(" - ")
    return zone.pop().strip() if zone else None


def get_oras(soup: BeautifulSoup):
    breadcrumbs = soup.select(breadcrumbs_selector)
    crumb = breadcrumbs.pop()
    if not crumb:
        return None
    crumb = breadcrumbs.pop()
    if not crumb:
        return None
    zone = crumb.get_text(strip=True).split(" - ")
    return zone.pop().strip() if zone else None


def get_zona(soup: BeautifulSoup):
    breadcrumbs = soup.select(breadcrumbs_selector)
    crumb = breadcrumbs.pop()
    if not crumb:
        return None
    zone = crumb.get_text(strip=True).split(" - ")
    return zone.pop().strip() if zone else None


class OLXURLOfferParser:
    """ Extracts data from a single olx offer page"""

    def __init__(self, requester: Requester):
        self.requester = requester
        self.location_repository = LocationRepository(PostgresClient())

    def parse_offer(self, url: str, request: OfferRequest) -> Offer:
        logger.info(f"Parsing offer {url}")

        html = self.requester.get(url)
        soup = BeautifulSoup(html.content, "html.parser")

        specs = extract_specs_dict(soup)
        details = get_offer_details(specs)

        offer = Offer(url=url, sursa="olx")

        offer.titlu = get_title(soup)
        offer.pret = get_price(soup)

        offer.judet = get_judet(soup) or request.judet
        offer.oras = get_oras(soup) or request.oras
        offer.zona = get_zona(soup)

        geolocation: Location = get_geolocation(self, offer)
        offer.lat = geolocation.lat if geolocation and geolocation.lat else None
        offer.lng = geolocation.lng if geolocation and geolocation.lng else None

        offer.tip_proprietate = request.proprietate
        offer.tip_tranzactie = request.tranzactie
        offer.tip_vanzator = details.get("tip_vanzator") or request.vanzator

        offer.descriere = get_description(soup)
        offer.data_postarii = datetime.now()

        offer.suprafata = details.get("suprafata").replace(" m²", "") if details.get("suprafata") else None
        offer.numar_camere = details.get("numar_camere") or request.camere
        offer.etaj = details.get("etaj")
        offer.compartimentare = details.get("compartimentare")
        offer.an_constructie = details.get("an_constructie")

        offer.imagini = get_imagini(soup)

        return offer
