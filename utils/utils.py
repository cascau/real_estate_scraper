from config.settings import GEOCODE_MAPS_URL, OLX_BASE_URL, OLX_SEARCH_PRIVATE, OLX_SEARCH_BUSINESS, GLOBAL_CURRENCY, \
    OLX_SEARCH_NEWEST
from models.offer_request import OfferRequest


def get_geolocation_url(city: str):
    return GEOCODE_MAPS_URL + city

def build_olx_card_search_url(req: OfferRequest, page: int = 1) -> str:

    url = OLX_BASE_URL
    url += "case-de" if req.proprietate == "case" else "apartamente-garsoniere-de"
    url += "-vanzare/" if req.tranzactie == "vanzare" else "-inchiriat/"
    url += req.camere + "/" if req.proprietate != "case" else ""
    url += req.judet + "-judet/"
    search = OLX_SEARCH_PRIVATE if req.vanzator == "private" else OLX_SEARCH_BUSINESS
    url += f"?currency={GLOBAL_CURRENCY}&{OLX_SEARCH_NEWEST}&{search}&page={page}"
    return url