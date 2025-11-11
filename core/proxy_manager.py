import random
import requests

from core.logger_config import setup_logger

logger = setup_logger(__name__)


class ProxyManager:
    def __init__(self,
                 proxy_source="https://api.proxyscrape.com/v2/?request=getproxies&protocol=http&timeout=3000&country=all"):
        self.proxy_source = proxy_source
        self.proxies = []
        self.load_proxies()

    def load_proxies(self):
        """Încarcă lista de proxy-uri din sursa specificată."""
        try:
            resp = requests.get(self.proxy_source, timeout=10)
            if resp.status_code == 200:
                self.proxies = [p.strip() for p in resp.text.split("\n") if p.strip()]
                logger.info(f"🌍 Loaded {len(self.proxies)} proxies from {self.proxy_source}")
            else:
                logger.warning(f"⚠️ Proxy source returned {resp.status_code}")
        except Exception as e:
            logger.error(f"❌ Failed to load proxies: {e}")
            self.proxies = []

    def get_random_proxy(self) -> dict:
        """Returnează un proxy random în formatul pentru requests."""
        if not self.proxies:
            logger.warning("⚠️ No proxies loaded, returning None")
            return {}

        proxy = random.choice(self.proxies)
        return {
            "http": f"http://{proxy}",
            "https": f"http://{proxy}",
        }
