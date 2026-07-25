from github_utils import fetch_leetcode_stats
from resume_utils import update_resume_markdown
from pdf_utils import compile_pdf_variant
from ai_utils import generate_linkedin_post
from linkedin_utils import publish_post


def main():
    stats = fetch_leetcode_stats()

    if not stats:
        return

    updated_resume = update_resume_markdown(stats["totalSolved"])

    if updated_resume:
        compile_pdf_variant(
            updated_resume,
            "Harshit_FullStack_Resume.pdf",
            "fullstack"
        )

        compile_pdf_variant(
            updated_resume,
            "Harshit_Backend_Resume.pdf",
            "backend"
        )

    post = generate_linkedin_post(stats)

    if post:
        publish_post(post)


if __name__ == "__main__":
    main()
