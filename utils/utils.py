from config.settings import GEOCODE_MAPS_URL


def get_geolocation_url(city: str):
    return GEOCODE_MAPS_URL + city

