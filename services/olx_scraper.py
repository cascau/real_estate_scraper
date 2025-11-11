from typing import List
from bs4 import BeautifulSoup
from core.requester import Requester
from config import settings
from core.logger_config import setup_logger

logger = setup_logger(__name__)


class OLXScraper:
    def __init__(self, requester: Requester):
        self.requester = requester

    def parse_page(self, html: str) -> List[str]:
        soup = BeautifulSoup(html, "html.parser")
        offers: List[str] = []
        cards = soup.select('div[data-cy="l-card"]')
        for card in cards:
            a_tag = card.find('a', href=True)
            if a_tag:
                url = a_tag['href']
                if url.startswith('/'):
                    url = settings.OLX_URL + url
                if settings.OLX_URL in url:
                    offers.append(url)
        return offers

    def get_all_offers(self, max_pages: int = 50) -> List[str]:
        page = 1
        all_urls: List[str] = []

        while page <= max_pages:
            page_url = settings.build_olx_card_search_url(page)
            logger.info(f"Scraping page {page_url}")
            resp = self.requester.get(page_url)
            if resp is None:
                logger.warning(f"Request returned None for page {page} — stopping.")
                break

            urls = self.parse_page(resp.text)
            if not urls:
                logger.info(f"No offers found on page {page} — stopping.")
                break

            logger.info(f"Page {page}: found {len(urls)} offers")
            all_urls.extend(urls)
            page += 1

        # deduplicate while preserving order
        return list(dict.fromkeys(all_urls))
