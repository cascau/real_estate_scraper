import random
from concurrent.futures import ThreadPoolExecutor, as_completed

from core.logger_config import setup_logger
from core.requester import Requester
from db.offer_repository import OfferRepository
from db.postgres_client import PostgresClient
from models.offer_request import OfferRequest

from services.olx_scraper import OLXScraper
from services.olx_offer_parser import OLXURLOfferParser

logger = setup_logger("[SCRAPER_MANAGER]")


class ScraperManager:
    def __init__(self):
        self.db_client = PostgresClient()
        self.repo = OfferRepository(self.db_client)

    def get_all_sources(self):
        """Returnează toți scrapperii activi din sistem."""
        # Poți adăuga aici alte surse (StoriaScraper, ImobiliareScraper, etc.)
        return [
            {
                "name": "OLX",
                "scraper": OLXScraper,
                "parser": OLXURLOfferParser,
            },
        ]

    def run_scraper(self, offer_request: OfferRequest, source_name: str):
        """Rulează un scraper complet pentru o anumită sursă."""
        logger.info(f"🔍 Pornim scraping pentru sursa: {source_name} | {offer_request}")

        requester = Requester(min_delay=1.0, max_delay=2.0, cache_enabled=True)
        scraper = self.get_scraper_by_name(source_name)(requester)
        parser = self.get_parser_by_name(source_name)(requester)

        urls = scraper.get_all_offers(max_pages=5)
        logger.info(f"🌐 {source_name}: găsite {len(urls)} oferte")

        saved_count = 0
        error_count = 0

        with ThreadPoolExecutor(max_workers=10) as executor:
            future_to_url = {
                executor.submit(parser.parse_offer, url, offer_request): url for url in urls
            }

            for future in as_completed(future_to_url):
                url = future_to_url[future]
                try:
                    offer = future.result()
                    self.repo.save_offer(offer)
                    saved_count += 1
                    logger.info(f"[{source_name}] 💾 Salvat: {offer.titlu}")
                except Exception as e:
                    error_count += 1
                    logger.error(f"[{source_name}] ❌ Eroare pentru {url}: {e}")

        logger.info(f"✅ {source_name}: {saved_count} salvate, {error_count} erori\n")

    def  get_scraper_by_name(self, source_name: str):
        return next(
            (s["scraper"] for s in self.get_all_sources() if s["name"] == source_name),
            None,
        )

    def get_parser_by_name(self, source_name: str):
        return next(
            (s["parser"] for s in self.get_all_sources() if s["name"] == source_name),
            None,
        )
