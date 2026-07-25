import logging
import requests
import time

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

logger = logging.getLogger(__name__)


def get_json(url, timeout=10, retries=3):
    for attempt in range(retries):
        try:
            response = requests.get(url, timeout=timeout)
            response.raise_for_status()
            return response.json()

        except Exception:
            if attempt == retries - 1:
                raise
            time.sleep(2)
