import fitz  # PyMuPDF

def extract_highlighted_text(pdf_path, start_page, end_page):
    doc = fitz.open(pdf_path)
    results = []

    for page_num in range(start_page - 1, end_page):
        page = doc.load_page(page_num)
        highlights = []

        annot = page.first_annot
        while annot:
            if annot.type[0] == 8:  # Highlight annotation
                try:
                    # Use the 'text' option to get the highlighted text
                    highlight_text = annot.get_text("text")
                    highlights.append(highlight_text.strip())
                except Exception as e:
                    print(f"Error extracting text from annotation on page {page_num + 1}: {e}")
            annot = annot.next

        results.append({
            "page": page_num + 1,
            "highlights": highlights
        })

    return results

# Usage
pdf_file = "conlaw.pdf"  # Replace with your PDF path
start_page = 576
end_page = 579

highlighted_texts = extract_highlighted_text(pdf_file, start_page, end_page)

for result in highlighted_texts:
    print(f"\nPage {result['page']} Highlights:")
    for highlight in result['highlights']:
        print(f"- {highlight}")
