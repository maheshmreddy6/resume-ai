import re


def clean_text(text: str) -> str:
    """
    Clean extracted PDF text.
    """

    if not text:
        return ""

    # Remove extra spaces
    text = re.sub(
        r"\s+",
        " ",
        text
    )

    # Remove unwanted characters
    text = re.sub(
        r"[^\w\s.,@+\-#()]",
        "",
        text
    )

    return text.strip()