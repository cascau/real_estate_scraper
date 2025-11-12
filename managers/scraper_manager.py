# managers/scraper_manager.py
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List
from core.logger_config import setup_logger
from db.offer_repository import OfferRepository
from db.postgres_client import PostgresClient
from services.base_scraper import BaseScraper
from models.offer_request import OfferRequest

logger = setup_logger("[SCRAPER_MANAGER]")


class ScraperManager:
    def __init__(self, requester_factory=None):
        self.db_client = PostgresClient()
        self.repo = OfferRepository(self.db_client)
        self.scrapers: List[BaseScraper] = []
        self.requester_factory = requester_factory or (lambda: None)

    def register_scraper(self, scraper: BaseScraper):
        self.scrapers.append(scraper)

    def run_scraper(self, scraper: BaseScraper):
        logger.info(f"🔍 Pornim scraping pentru {scraper.source_name}")

        # pentru fiecare scraper, luăm lista lui de OfferRequest
        offer_requests: List[OfferRequest] = scraper.get_offer_requests()
        logger.info(f"{scraper.source_name} - {len(offer_requests)} request-uri generate")

        for req in offer_requests:
            logger.info(f"[{scraper.source_name}] Procesăm request: {req.__dict__}")
            urls = scraper.get_all_offers(req, max_pages=5)
            logger.info(f"[{scraper.source_name}] Găsite {len(urls)} oferte pentru request")

            saved_count = 0
            error_count = 0

            with ThreadPoolExecutor(max_workers=20) as executor:
                futures = {executor.submit(scraper.parse_offer, url, req): url for url in urls}
                for future in as_completed(futures):
                    url = futures[future]
                    try:
                        offer = future.result()
                        self.repo.save_offer(offer)
                        saved_count += 1
                        logger.info(f"[{scraper.source_name}] 💾 Salvat: {offer.titlu}")
                    except Exception as e:
                        error_count += 1
                        logger.exception(f"[{scraper.source_name}] ❌ Eroare la {url}: {e}")

            logger.info(f"[{scraper.source_name}] Final request: salvate={saved_count}, erori={error_count}")
