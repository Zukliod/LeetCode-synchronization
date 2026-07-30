import requests

from config import (
    LINKEDIN_ACCESS_TOKEN,
    LINKEDIN_AUTHOR_URN
)

from utils import (
    log,
    warning,
    success,
    error
)


def publish_post(content: str) -> bool:
    """
    Publish generated content to LinkedIn.
    """

    if (
        not LINKEDIN_ACCESS_TOKEN
        or
        not LINKEDIN_AUTHOR_URN
    ):

        warning(
            "LinkedIn credentials missing."
        )

        return False

    log("Publishing to LinkedIn...")

    url = (
        "https://api.linkedin.com/v2/ugcPosts"
    )

    headers = {

        "Authorization":
            f"Bearer {LINKEDIN_ACCESS_TOKEN}",

        "Content-Type":
            "application/json",

        "X-Restli-Protocol-Version":
            "2.0.0"

    }

    payload = {

        "author":
            f"urn:li:person:{LINKEDIN_AUTHOR_URN}",

        "lifecycleState":
            "PUBLISHED",

        "specificContent": {

            "com.linkedin.ugc.ShareContent": {

                "shareCommentary": {

                    "text": content

                },

                "shareMediaCategory":
                    "NONE"

            }

        },

        "visibility": {

            "com.linkedin.ugc.MemberNetworkVisibility":
                "PUBLIC"

        }

    }

    try:

        response = requests.post(
            url,
            headers=headers,
            json=payload,
            timeout=15
        )

        response.raise_for_status()

        success(
            "LinkedIn post published."
        )

        return True

    except Exception as e:

        error(
            f"LinkedIn publish failed : {e}"
        )

        return False
