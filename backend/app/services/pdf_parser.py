from pathlib import Path

from pypdf import PdfReader

from app.utils.text_cleaner import clean_text


class PDFParser:

    @staticmethod
    def extract_text(file_path: str) -> str:
        """
        Extract text content from PDF file.
        """

        path = Path(file_path)

        if not path.exists():
            raise FileNotFoundError(
                "PDF file not found"
            )

        reader = PdfReader(file_path)

        extracted_text = ""

        for page_number, page in enumerate(reader.pages):
            page_text = page.extract_text()

            if page_text:
                extracted_text += page_text + "\n"

        cleaned_text = clean_text(
            extracted_text
        )

        return cleaned_text
