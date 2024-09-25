import fitz  # PyMuPDF

def extract_highlights_and_text(pdf_path, start_page, end_page):
    # Open the PDF file
    doc = fitz.open(pdf_path)

    results = []  # Store highlights and text here

    # Loop through specified page range
    for page_num in range(start_page - 1, end_page):  # Page numbers are zero-indexed in PyMuPDF
        page = doc.load_page(page_num)
        page_text = page.get_text("text")  # Extract page text to confirm page access

        # Print some page text for verification
        print(f"--- Page {page_num + 1} Text ---")
        print(page_text[:500])  # Print first 500 characters of text to verify the correct page

        highlights = []
        annot = page.first_annot
        while annot:
            # Check if annotation is a highlight
            if annot.type[0] == 8:
                highlight = annot.info.get("content", "No content found")  # Safely extract highlight content
                highlights.append(highlight)
            annot = annot.next
        
        # Store results for this page
        results.append({
            "page": page_num + 1,
            "text": page_text[:500],  # Store first 500 characters of page text
            "highlights": highlights
        })

    return results

# Path to the PDF file
pdf_file = "conlaw.pdf"

# Pages 576 to 579
start_page = 576
end_page = 579

# Extract and print the highlights and text for debugging
results = extract_highlights_and_text(pdf_file, start_page, end_page)

# Output the results for verification
for result in results:
    print(f"\nPage {result['page']} Summary:")
    print(f"Text (first 500 chars): {result['text']}")
    print(f"Highlights: {result['highlights']}")
