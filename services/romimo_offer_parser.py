import re
from datetime import datetime
from typing import Optional, List

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


def get_title(soup: BeautifulSoup) -> str:
    title_tag = soup.select_one('h1[itemprop="name"]')
    return title_tag.get_text(strip=True) if title_tag else None


def get_price(soup: BeautifulSoup) -> Optional[int]:
    price_tag = soup.select_one('span[itemprop="price"]')
    if not price_tag:
        return None
    price_str = price_tag.get_text(strip=True)
    price_str = re.sub("[^0-9.]", "", price_str)
    return int(float(price_str))


def get_zona(soup: BeautifulSoup):
    zone_details = soup.select_one("div.row div.detail-info")
    links = zone_details.select("a")
    if links:
        links.pop()  # Remove Vezi pe harta
    return links.pop().get_text() if links else None  # Real zona


def get_description(soup: BeautifulSoup) -> Optional[str]:
    description_tag = soup.select_one('div[itemprop="description"]')
    return description_tag.get_text(strip=True) if description_tag else None


def get_date_posted(soup: BeautifulSoup) -> Optional[datetime]:
    valid_from = soup.select_one('i[itemprop="validFrom"]')
    if not valid_from:
        return None
    date_str = valid_from.get_text(strip=True).replace("Valabil din ", "")
    return datetime.strptime(date_str, "%m/%d/%Y %I:%M:%S %p") if date_str else None


def get_imagini(soup: BeautifulSoup) -> Optional[List[str]]:
    imgs = []
    slide_show = soup.select('div[id="detail-gallery"] > ul > li > img')
    if not slide_show:
        return None
    for slide in slide_show:
        imgs.append(slide['src'])
    return imgs


def extract_specs_dict(soup: BeautifulSoup) -> dict:
    specs = {}
    spec_tags = soup.select('div[class="attribute-item"]')
    for tag in spec_tags:
        tag_attr = tag.select_one('div[class="attribute-label"]')
        attr = tag_attr.get_text(strip=True) if tag_attr else None
        tag_value = tag.select_one('div[class="attribute-value"]')
        tag = tag_value.get_text(strip=True) if tag_value else True
        specs[attr] = tag
    return specs


def get_offer_details(specs: dict):
    return {
        "an_constructie": specs.get("Anul constructiei"),
        "etaj": str(specs.get("Etaj")).replace("etaj", "").strip() if specs.get("Etaj") else None,
        "compartimentare": specs.get("Compartimentare"),
        "suprafata": specs.get("Suprafata utila").replace("m2", "").strip() if specs.get("Suprafata utila") else None,
        "numar_camere": str(specs.get("Numar camere")).replace(" ", "-") if specs.get("Numar camere") else None,
    }


class RomimoURLOfferParser:
    def __init__(self, requester: Requester):
        self.requester = requester
        self.location_repository = LocationRepository(PostgresClient())

    def parse_offer(self, url: str, request: OfferRequest) -> Offer:
        logger.info(f"Parsing offer {url}")

        html = self.requester.get(url)
        soup = BeautifulSoup(html.content, "html.parser")

        specs = extract_specs_dict(soup)
        details = get_offer_details(specs)

        offer: Offer = Offer(url, "romimo")

        offer.titlu = get_title(soup)
        offer.pret = get_price(soup)

        offer.judet = "bucuresti-ilfov" if request in ["Bucuresti", "bucuresti", "Ilfov", "ilfov"] else request.judet
        offer.oras = request.oras
        offer.zona = get_zona(soup)

        geolocation: Location = get_geolocation(self, offer)
        offer.lat = geolocation.lat if geolocation and geolocation.lat else None
        offer.lng = geolocation.lng if geolocation and geolocation.lng else None

        offer.tip_proprietate = request.proprietate
        offer.tip_tranzactie = request.tranzactie
        offer.tip_vanzator = request.vanzator

        offer.descriere = get_description(soup)
        offer.data_postarii = get_date_posted(soup) or datetime.now()

        offer.suprafata = details.get("suprafata")
        offer.numar_camere = details.get("numar_camere") or request.camere
        offer.etaj = details.get("etaj")
        offer.compartimentare = details.get("compartimentare")
        offer.an_constructie = details.get("an_constructie")

        offer.imagini = get_imagini(soup)

        return offer
