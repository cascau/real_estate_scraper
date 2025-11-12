# main.py
import time
import schedule
from core.logger_config import setup_logger
from core.requester import Requester
from managers.scraper_manager import ScraperManager
from services.olx_scraper_full import OLXFullScraper

logger = setup_logger("[MAIN]")


def main():
    requester = Requester(min_delay=1.0, max_delay=2.0, cache_enabled=True)
    manager = ScraperManager()

    manager.register_scraper(OLXFullScraper(requester))

    for scraper in manager.scrapers:
        manager.run_scraper(scraper)

    schedule.every(3).minutes.do(lambda: [manager.run_scraper(s) for s in manager.scrapers])

    logger.info("Scheduler pornit. Rulează la fiecare 3 minute.")
    while True:
        schedule.run_pending()
        time.sleep(10)


if __name__ == "__main__":
    main()
