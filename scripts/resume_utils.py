import os
import re

from config import RESUME_FILE

from utils import (
    log,
    success,
    warning
)


def update_resume_markdown(total_solved: int):

    if not os.path.exists(RESUME_FILE):

        warning(f"{RESUME_FILE} not found.")

        return None

    log("Updating resume.md...")

    with open(
        RESUME_FILE,
        "r",
        encoding="utf-8"
    ) as file:

        content = file.read()

    pattern = (
        r"(<!-- LEETCODE_START -->)"
        r"(.*?)"
        r"(<!-- LEETCODE_END -->)"
    )

    replacement = (
        "\\1"
        f"Solved {total_solved}+ "
        "algorithmic problems on LeetCode"
        "\\3"
    )

    updated, count = re.subn(
        pattern,
        replacement,
        content,
        flags=re.DOTALL
    )

    if count == 0:

        warning(
            "LeetCode placeholders not found."
        )

        return content

    with open(
        RESUME_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        file.write(updated)

    success(
        "resume.md updated successfully."
    )

    return updated
