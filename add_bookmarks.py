import fitz  # PyMuPDF

def extract_highlighted_text_by_blocks(pdf_path, start_page, end_page):
    # Open the PDF file
    doc = fitz.open(pdf_path)

    results = []  # Store highlighted text here

    # Loop through the specified page range
    for page_num in range(start_page - 1, end_page):  # Page numbers are zero-indexed in PyMuPDF
        page = doc.load_page(page_num)

        # Print some page text for verification
        page_text = page.get_text("text")
        print(f"--- Page {page_num + 1} Text ---")
        print(page_text[:500])  # Print first 500 characters of text to verify the correct page

        # Extract blocks of text from the page
        blocks = page.get_text("blocks")  # Returns a list of text blocks with coordinates

        highlights = []
        annot = page.first_annot
        while annot:
            if annot.type[0] == 8:  # Annotation type 8 is for highlight
                highlight_text = ""
                vertices = annot.vertices  # Extract the vertices of the highlight
                for i in range(0, len(vertices), 4):  # Process quads (sets of 4 points)
                    # Unpack the tuple vertices into individual coordinates
                    x0, y0 = vertices[i]      # First point (top-left corner)
                    x1, y1 = vertices[i + 2]  # Third point (bottom-right corner)

                    # Match the blocks of text that fall within the rectangle
                    for block in blocks:
                        block_x0, block_y0, block_x1, block_y1, block_text = block[:5]
                        # Check if the block falls within the highlighted region
                        if (x0 <= block_x0 <= x1 and y0 <= block_y0 <= y1) or (x0 <= block_x1 <= x1 and y0 <= block_y1 <= y1):
                            highlight_text += block_text + " "

                highlights.append(highlight_text.strip())  # Append the concatenated text
            annot = annot.next

        results.append({
            "page": page_num + 1,
            "text": page_text[:500],  # Store first 500 characters of page text
            "highlights": highlights
        })

    return results

# Path to the PDF file
pdf_file = "conlaw.pdf"  # Replace this with the actual path to the PDF

# Pages 576 to 579
start_page = 576
end_page = 579

# Extract and print the highlights and text for debugging
results = extract_highlighted_text_by_blocks(pdf_file, start_page, end_page)

# Output the results for verification
for result in results:
    print(f"\nPage {result['page']} Summary:")
    print(f"Text (first 500 chars): {result['text']}")
    print(f"Highlights: {result['highlights']}")
