from config import LEETCODE_USERNAME
from utils import get_json, logger


def fetch_leetcode_stats(username=LEETCODE_USERNAME):

    logger.info("Fetching LeetCode Stats...")

    url = (
        f"https://leetcode-api-faisalshohag.vercel.app/"
        f"{username}"
    )

    try:

        data = get_json(url)

        stats = {
            "totalSolved": data.get("totalSolved", 0),
            "easySolved": data.get("easySolved", 0),
            "mediumSolved": data.get("mediumSolved", 0),
            "hardSolved": data.get("hardSolved", 0),
            "ranking": data.get("ranking", "N/A")
        }

        return stats

    except Exception as e:

        logger.error(f"Unable to fetch LeetCode Stats: {e}")

        return None
