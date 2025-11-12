GLOBAL_CURRENCY = "EUR"
SCHEDULE_RERUN_PERIOD_MINS = 5

## GEOCODE MAPS API ##
GEOCODE_MAPS_API_KEY = "691334cd7e00f850150060wln0e646a"
GEOCODE_MAPS_URL = f"https://geocode.maps.co/search?api_key={GEOCODE_MAPS_API_KEY}&q="

## OLX ##
OLX_URL = "https://www.olx.ro"
OLX_BASE_URL = f"{OLX_URL}/imobiliare/"
OLX_SEARCH_NEWEST = "search%5Border%5D=created_at:desc"
OLX_SEARCH_PRIVATE = "search%5Bprivate_business%5D=private"
OLX_SEARCH_BUSINESS = "search%5Bprivate_business%5D=business"

## ROMIMO ##
ROMIMO_URL = "https://www.romimo.ro/"
ROMIMO_SEARCH_NEWEST = f"?ordered=desc&orderby=date&currency={GLOBAL_CURRENCY}"
ROMIMO_SEARCH_PRIVATE = "&commercial=false"
ROMIMO_SEARCH_BUSINESS = "&commercial=true"
