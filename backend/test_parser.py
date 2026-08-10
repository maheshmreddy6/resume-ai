from app.services.pdf_parser import PDFParser


text = PDFParser.extract_text(
    "uploads/resume.pdf"
)

print(text)
