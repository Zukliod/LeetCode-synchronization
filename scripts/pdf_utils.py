import re
import markdown
from xhtml2pdf import pisa

from utils import (
    log,
    success
)


def compile_pdf_variant(
    md_content: str,
    output_pdf: str,
    filter_type: str
):
    """
    Generates ATS-friendly PDF resumes.
    """

    log(f"Generating {output_pdf}")

    content = md_content

    if filter_type == "fullstack":

        content = re.sub(
            r"<!-- BACKEND_ONLY_START -->.*?<!-- BACKEND_ONLY_END -->",
            "",
            content,
            flags=re.DOTALL
        )

        content = (
            content
            .replace("<!-- FULLSTACK_ONLY_START -->", "")
            .replace("<!-- FULLSTACK_ONLY_END -->", "")
        )

    elif filter_type == "backend":

        content = re.sub(
            r"<!-- FULLSTACK_ONLY_START -->.*?<!-- FULLSTACK_ONLY_END -->",
            "",
            content,
            flags=re.DOTALL
        )

        content = (
            content
            .replace("<!-- BACKEND_ONLY_START -->", "")
            .replace("<!-- BACKEND_ONLY_END -->", "")
        )

    content = re.sub(
        r"<!-- LEETCODE_START -->|<!-- LEETCODE_END -->",
        "",
        content
    )

    html = markdown.markdown(
        content,
        extensions=["tables"]
    )

    template = f"""
<!DOCTYPE html>
<html>

<head>

<meta charset="utf-8">

<style>

@page {{
size: letter;
margin:0.5in;
}}

body {{
font-family: Helvetica, Arial;
font-size:10pt;
line-height:1.4;
}}

h1 {{
font-size:18pt;
}}

h2 {{
font-size:12pt;
border-bottom:1px solid black;
}}

h3 {{
font-size:10pt;
}}

</style>

</head>

<body>

{html}

</body>

</html>
"""

    with open(output_pdf, "wb") as pdf:

        pisa.CreatePDF(
            template,
            dest=pdf
        )

    success(f"{output_pdf} created.")
