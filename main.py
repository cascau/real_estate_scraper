# main.py
import random
import time
import schedule

from config.settings import SCHEDULE_RERUN_PERIOD_MINS
from core.logger_config import setup_logger
from core.requester import Requester
from managers.scraper_manager import ScraperManager
from services.olx_scraper_full import OLXFullScraper
from services.romimo_scraper_full import RomimoFullScraper

logger = setup_logger("[MAIN]")


def main():
    run_scrapers()


def run_scrapers():
    requester = Requester(min_delay=1.0, max_delay=2.0, cache_enabled=True)
    manager = ScraperManager()

    manager.register_scraper(OLXFullScraper(requester))
    manager.register_scraper(RomimoFullScraper(requester))
    random.shuffle(manager.scrapers)

    for scraper in manager.scrapers:
        manager.run_scraper(scraper)

    (schedule.every(SCHEDULE_RERUN_PERIOD_MINS).minutes
     .do(lambda: [manager.run_scraper(s) for s in manager.scrapers]))

    logger.info(f"Scheduler pornit. Rulează la fiecare {SCHEDULE_RERUN_PERIOD_MINS} minute.")
    while True:
        schedule.run_pending()
        time.sleep(10)


if __name__ == "__main__":
    main()
