import fitz  # PyMuPDF
import re

def clean_text(text):
    """Remove unwanted characters and clean up extra spaces."""
    cleaned_text = re.sub(r'[^\w\s.,\-\[\]\(\)]', '', text)  # Keep alphanumeric, punctuation, and spacing
    cleaned_text = re.sub(r'\s+', ' ', cleaned_text)  # Remove extra spaces
    return cleaned_text.strip()

def merge_consecutive_highlights(highlights):
    """Merge consecutive highlights that belong together and remove duplications."""
    merged_highlights = []
    current_highlight = highlights[0]

    for i in range(1, len(highlights)):
        # If the current highlight overlaps or is a substring of the next one, merge them
        if highlights[i].startswith(current_highlight[-10:].strip()) or current_highlight in highlights[i]:
            current_highlight = current_highlight + " " + highlights[i]
        else:
            merged_highlights.append(current_highlight.strip())
            current_highlight = highlights[i]

    merged_highlights.append(current_highlight.strip())  # Add the last highlight
    return [clean_text(highlight) for highlight in merged_highlights]

def extract_text_by_words(pdf_path, start_page, end_page):
    # Open the PDF file
    doc = fitz.open(pdf_path)

    results = []  # Store extracted text here

    # Loop through the specified page range
    for page_num in range(start_page - 1, end_page):  # Page numbers are zero-indexed in PyMuPDF
        page = doc.load_page(page_num)

        highlights = []
        annot = page.first_annot
        while annot:
            if annot.type[0] == 8:  # Annotation type 8 is for highlight
                vertices = annot.vertices  # Extract the vertices of the highlight
                for i in range(0, len(vertices), 4):  # Process quads (sets of 4 points)
                    # Get the minimum and maximum x, y coordinates to form a valid rectangle
                    x0 = min(vertices[i][0], vertices[i+1][0], vertices[i+2][0], vertices[i+3][0])
                    y0 = min(vertices[i][1], vertices[i+1][1], vertices[i+2][1], vertices[i+3][1])
                    x1 = max(vertices[i][0], vertices[i+1][0], vertices[i+2][0], vertices[i+3][0])
                    y1 = max(vertices[i][1], vertices[i+1][1], vertices[i+2][1], vertices[i+3][1])

                    # Expand the bounding box slightly to ensure we capture all nearby text
                    expansion = 2  # Adjust this value if necessary
                    rect = fitz.Rect(x0 - expansion, y0 - expansion, x1 + expansion, y1 + expansion)

                    # Extract words and filter them by the bounding box
                    words = page.get_text("words")  # Extract all words from the page with coordinates
                    extracted_words = [w[4] for w in words if rect.contains(fitz.Point(w[0], w[1]))]  # Check if word is within the rect

                    if extracted_words:
                        highlight_text = " ".join(extracted_words)
                        cleaned_highlight_text = clean_text(highlight_text)
                        highlights.append(cleaned_highlight_text)

                    # Debugging information
                    print(f"Highlight found on page {page_num + 1} with coordinates: ({x0}, {y0}, {x1}, {y1})")
                    print(f"Extracted words: {extracted_words}")

            annot = annot.next

        # Merge consecutive highlights that belong to the same sentence or paragraph
        if highlights:
            merged_highlights = merge_consecutive_highlights(highlights)
            results.append({
                "page": page_num + 1,
                "highlights": merged_highlights
            })

    return results

# Path to the PDF file
pdf_file = "conlaw.pdf"  # Replace this with the actual path to the PDF

# Pages 576 to 579
start_page = 576
end_page = 579

# Extract and print the text by area for debugging
results = extract_text_by_words(pdf_file, start_page, end_page)

# Output the results for verification
for result in results:
    print(f"\nPage {result['page']} Highlights:")
    for idx, highlight in enumerate(result['highlights'], 1):
        print(f"Highlight {idx}: {highlight}\n")
