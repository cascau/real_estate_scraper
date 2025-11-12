from typing import Optional

import requests

from config.settings import GEOCODE_MAPS_URL, OLX_BASE_URL, OLX_SEARCH_PRIVATE, OLX_SEARCH_BUSINESS, GLOBAL_CURRENCY, \
    OLX_SEARCH_NEWEST, ROMIMO_URL, ROMIMO_SEARCH_NEWEST, ROMIMO_SEARCH_PRIVATE, ROMIMO_SEARCH_BUSINESS
from models.location import Location
from models.offer import Offer
from models.offer_request import OfferRequest


def get_geolocation_url(city: str):
    return GEOCODE_MAPS_URL + city


def get_geolocation_query(offer: Offer):
    oras = f",{offer.oras}" if offer.oras else ""
    zona = f",{offer.zona}" if offer.zona else ""
    return f"Romania{oras}{zona}"


def get_geolocation(self, offer: Offer) -> Optional[Location]:
    existing_geolocation = self.location_repository.find_location_by_judet_and_zona(offer)
    if existing_geolocation:
        return existing_geolocation

    query = get_geolocation_query(offer)
    url = get_geolocation_url(query)
    response = requests.get(url)
    json = response.json()[0] if response.status_code == 200 and len(response.json()) > 0 else None
    if not json:
        return None
    location: Location = Location(offer.judet, offer.zona, json["lat"], json["lon"])
    return self.location_repository.save_location(location)


def build_olx_card_search_url(req: OfferRequest, page: int = 1) -> str:
    url = OLX_BASE_URL
    url += "case-de" if req.proprietate == "case" else "apartamente-garsoniere-de"
    url += "-vanzare/" if req.tranzactie == "vanzare" else "-inchiriat/"
    url += req.camere + "/" if req.proprietate != "case" else ""
    url += req.judet + "-judet/"
    search = OLX_SEARCH_PRIVATE if req.vanzator == "private" else OLX_SEARCH_BUSINESS
    url += f"?currency={GLOBAL_CURRENCY}&{OLX_SEARCH_NEWEST}&{search}&page={page}"
    return url


def build_romimo_card_search_url(req: OfferRequest, page: int = 1) -> str:
    url = ROMIMO_URL
    if req.proprietate == "case":
        url += "case-vile/inchiriere/" if req.tranzactie == "inchiriat" else "case/vanzare/"
        url += req.judet
    else:
        url += "apartamente/"
        url += "garsoniera/" if req.proprietate == "garsoniera" else f"apartamente-{req.camere}/"
        url += f"{req.tranzactie}/{req.judet}"
    url += ROMIMO_SEARCH_NEWEST
    url += ROMIMO_SEARCH_PRIVATE if req.vanzator == "private" else ROMIMO_SEARCH_BUSINESS
    url += f"&page={page}"
    return url
