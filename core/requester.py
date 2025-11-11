# core/requester.py
import random
import time

import diskcache as dc
import requests
from requests.exceptions import RequestException, ConnectionError

from core.logger_config import setup_logger
from core.user_agents import get_random_user_agent

logger = setup_logger(__name__)


class Requester:
    def __init__(self, min_delay=1.0, max_delay=3.0, cache_enabled=True, cache_expire=60 * 60 * 24, max_retries=3):
        """
        cache_expire: durata cache-ului în secunde (default: 24h)
        """
        self.session = requests.Session()
        self.min_delay = min_delay
        self.max_delay = max_delay
        self.max_retries = max_retries
        self.cache_enabled = cache_enabled
        self.cache_expire = cache_expire

        if cache_enabled:
            self.cache = dc.Cache("./.cache_olx")
            logger.info(f"🗄️ Cache initialized: {self.cache.directory}")

        self.headers = {
            "User-Agent": get_random_user_agent(),
            "Accept-Language": "ro-RO,ro;q=0.9,en-US;q=0.8,en;q=0.7",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
            "Referer": "https://www.google.com/",
        }

    def get(self, url: str, retry_count=0):
        """Trimite un GET cu retry logic și caching."""
        if self.cache_enabled and url in self.cache:
            logger.debug(f"💾 Cache hit: {url}")
            return self.cache[url]

        try:
            delay = random.uniform(self.min_delay, self.max_delay)
            logger.debug(f"Sleeping for {delay:.2f}s before request...")
            time.sleep(delay)

            response = self.session.get(url, headers=self.headers, timeout=10)
            if response.status_code == 429:
                raise RequestException("Too Many Requests (429)")

            response.raise_for_status()
            logger.debug(f"✅ Successfully fetched {url} [Status: {response.status_code}]")

            if self.cache_enabled:
                self.cache.set(url, response, expire=self.cache_expire)

            return response

        except (ConnectionError, RequestException) as e:
            return self._retry(url, retry_count, e)

    def _retry(self, url, retry_count, error):
        if retry_count >= self.max_retries:
            logger.error(f"❌ Max retries reached for {url}. Giving up.")
            raise error

        backoff = (2 ** retry_count) + random.uniform(0.2, 1.0)
        logger.info(f"⏳ Retry #{retry_count + 1} for {url} after {backoff:.2f}s")
        time.sleep(backoff)
        return self.get(url, retry_count + 1)
