from typing import List

from bs4 import BeautifulSoup

from config.settings import ROMIMO_URL
from core.logger_config import setup_logger
from core.requester import Requester
from models.offer_request import OfferRequest
from utils import utils

logger = setup_logger(__name__)


class RomimoScraper:
    def __init__(self, requester: Requester):
        self.requester = requester

    def parse_page(self, html: str) -> List[str]:
        soup = BeautifulSoup(html, 'html.parser')
        offers: List[str] = []
        cards = soup.select('div[class="article-item"]')
        for card in cards:
            links = card.select("a")
            if links and links[0] and links[0]['href'] and ROMIMO_URL in links[0]['href']:
                offers.append(links[0]['href'])
        return offers

    def get_all_offers(self, offer_request: OfferRequest, max_pages: int = 5) -> List[str]:
        page = 1
        all_urls: List[str] = []

        while page <= max_pages:
            page_url = utils.build_romimo_card_search_url(offer_request, page)
            logger.info(f"Scraping page {page_url}")
            resp = self.requester.get(page_url)
            if resp is None:
                logger.warning(f"Request returned None for page {page} - stopping.")
                break

            urls = self.parse_page(resp.text)
            if not urls:
                logger.info(f"No offers found for page {page} - stopping.")
                break

            logger.info(f"Page {page}: found {len(urls)} offers")
            all_urls.extend(urls)
            page += 1

        # deduplicate while preserving order
        return list(dict.fromkeys(all_urls))
