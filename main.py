import time
import random
import schedule

from core.logger_config import setup_logger
from managers.scraper_manager import ScraperManager
from models.offer_request import OfferRequest

logger = setup_logger("[MAIN]")


def get_offer_requests() -> list[OfferRequest]:
    vanzatori = ["private", "business"]
    proprietati = ["garsoniera", "apartament"]
    tranzactii = ["vanzare"]
    camere = ["1", "2", "3"]
    judete = ["Bucuresti-Ilfov"]
    orase = ["Bucuresti"]

    requests = [
        OfferRequest(vanzator, prop, tranz, cam, judet, oras)
        for vanzator in vanzatori
        for prop in proprietati
        for tranz in tranzactii
        for cam in camere
        for judet in judete
        for oras in orase
    ]
    random.shuffle(requests)
    return requests


def main():
    manager = ScraperManager()
    sources = [s["name"] for s in manager.get_all_sources()]
    offer_requests = get_offer_requests()

    for src in sources:
        for req in offer_requests:
            logger.info(f"📆 Programăm {src} - {req.oras}, {req.judet}")
            schedule.every(5).minutes.do(manager.run_scraper, req, src)

    # Rulează prima dată imediat
    for src in sources:
        for req in offer_requests:
            manager.run_scraper(req, src)

    while True:
        schedule.run_pending()
        time.sleep(10)


if __name__ == "__main__":
    main()
