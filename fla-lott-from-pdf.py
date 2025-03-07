
import pdfplumber

pdf_path = "fla-lottery-results.pdf"

with pdfplumber.open(pdf_path) as pdf:
    for page in pdf.pages:
        text = page.extract_text()
        print(text)  # Print raw text to inspect structure
