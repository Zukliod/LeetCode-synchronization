from github_utils import fetch_leetcode_stats
from resume_utils import update_resume_markdown
from pdf_utils import compile_pdf_variant
from ai_utils import generate_linkedin_post
from linkedin_utils import publish_post

from config import (
    FULLSTACK_RESUME,
    BACKEND_RESUME
)

from utils import log


def main():

    log("Starting Daily Automation Pipeline...")

    stats = fetch_leetcode_stats()

    if not stats:
        return

    updated_md = update_resume_markdown(
        stats["totalSolved"]
    )

    if updated_md:

        compile_pdf_variant(
            updated_md,
            FULLSTACK_RESUME,
            "fullstack"
        )

        compile_pdf_variant(
            updated_md,
            BACKEND_RESUME,
            "backend"
        )

    post = generate_linkedin_post(stats)

    if post:

        print("\nGenerated LinkedIn Post:\n")
        print(post)

        publish_post(post)

    log("Automation Completed.")


if __name__ == "__main__":
    main()
