import fitz  # PyMuPDF

def extract_highlights(pdf_path, start_page, end_page):
    # Open the PDF file
    doc = fitz.open(pdf_path)

    highlights = []  # Store highlights here

    # Loop through specified page range
    for page_num in range(start_page - 1, end_page):  # Page numbers are zero-indexed in PyMuPDF
        page = doc.load_page(page_num)
        annot = page.first_annot
        while annot:
            if annot.type[0] == 8:  # Annotation type 8 is for highlight
                highlight = annot.info["content"]
                highlights.append((page_num + 1, highlight))  # Store page number and highlight text
            annot = annot.next

    return highlights

# Path to the PDF file
pdf_file = "conlaw.pdf"

# Pages 576 to 579
start_page = 576
end_page = 579

# Extract and print the highlights
highlights = extract_highlights(pdf_file, start_page, end_page)

for page, text in highlights:
    print(f"Page {page}: {text}")
