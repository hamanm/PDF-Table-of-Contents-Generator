import fitz  # PyMuPDF
import re
import unicodedata

def clean_text(text):
    """
    Remove unwanted characters and clean up extra spaces.
    """
    # Remove non-printable characters
    text = ''.join(c for c in text if unicodedata.category(c)[0] != 'C')
    
    # Replace soft hyphens and other hyphen-related issues
    text = text.replace('\xad', '').replace('\u2002', ' ').replace('—', '-').replace('…', '...')
    
    # Remove any remaining unwanted characters
    text = re.sub(r'[^\w\s.,\-()\[\]"]', '', text)
    
    # Fix multiple spaces
    text = re.sub(r'\s+', ' ', text)
    
    return text.strip()

def expand_rect(rect, expansion):
    """
    Manually expand a rectangle by a given number of pixels.
    
    Parameters:
    - rect: fitz.Rect object
    - expansion: Number of pixels to expand on each side
    
    Returns:
    - Expanded fitz.Rect object
    """
    return fitz.Rect(rect.x0 - expansion, rect.y0 - expansion, rect.x1 + expansion, rect.y1 + expansion)

def intersection_area(rect1, rect2):
    """
    Calculate the area of intersection between two rectangles.
    
    Parameters:
    - rect1: fitz.Rect object
    - rect2: fitz.Rect object
    
    Returns:
    - Intersection area as float
    """
    intersection = rect1 & rect2
    return intersection.get_area()

def extract_highlights(pdf_path, start_page, end_page, expansion=1, threshold=0.8):
    """
    Extract highlighted text by mapping highlight positions to page lines.
    
    Parameters:
    - pdf_path: Path to the PDF file.
    - start_page: Starting page number (1-based).
    - end_page: Ending page number (inclusive).
    - expansion: Pixels to expand the highlight bounding box to capture surrounding text.
    - threshold: Minimum overlap ratio (0 to 1) to include a line.
    
    Returns:
    - List of dictionaries containing page numbers and their corresponding highlights.
    """
    doc = fitz.open(pdf_path)
    results = []

    for page_num in range(start_page - 1, end_page):
        page = doc.load_page(page_num)
        annot = page.first_annot
        highlights = []
        text_dict = page.get_text("dict")
        page_lines = []
        for block in text_dict["blocks"]:
            if block["type"] == 0:  # Text block
                for line in block["lines"]:
                    # Concatenate all spans in the line
                    line_text = " ".join([span["text"] for span in line["spans"]])
                    # Bounding box of the line
                    bbox = fitz.Rect(line["bbox"])
                    page_lines.append({
                        "text": line_text,
                        "rect": bbox
                    })
        
        print(f"\n--- Page {page_num +1} Highlights ---")

        while annot:
            if annot.type[0] == 8:  # Highlight annotation
                highlight_text = ""
                try:
                    # Attempt to access quads
                    quads = annot.quads
                    for quad in quads:
                        # Create rectangle from quad points
                        x0 = min([point.x for point in quad])
                        y0 = min([point.y for point in quad])
                        x1 = max([point.x for point in quad])
                        y1 = max([point.y for point in quad])
                        rect = fitz.Rect(x0, y0, x1, y1)
                        # Manually expand the rectangle
                        expanded_rect = expand_rect(rect, expansion)
                        
                        # Extract lines within the expanded rectangle with overlap threshold
                        for line in page_lines:
                            line_rect = line["rect"]
                            intersect_area = intersection_area(expanded_rect, line_rect)
                            line_area = line_rect.get_area()
                            if line_area > 0:
                                overlap_ratio = intersect_area / line_area
                                if overlap_ratio >= threshold:
                                    highlight_text += line["text"] + " "
                except AttributeError:
                    # If 'quads' attribute is missing, use the annotation's rectangle
                    rect = annot.rect
                    # Manually expand the rectangle
                    expanded_rect = expand_rect(rect, expansion)
                    # Extract lines within the expanded rectangle with overlap threshold
                    for line in page_lines:
                        line_rect = line["rect"]
                        intersect_area = intersection_area(expanded_rect, line_rect)
                        line_area = line_rect.get_area()
                        if line_area > 0:
                            overlap_ratio = intersect_area / line_area
                            if overlap_ratio >= threshold:
                                highlight_text += line["text"] + " "
                
                # Clean the extracted text
                cleaned_text = clean_text(highlight_text)
                
                if cleaned_text:
                    highlights.append(cleaned_text)
                    print(f"Highlight {len(highlights)}: {cleaned_text}")
                
            annot = annot.next
        
        # Append to results if any highlights found
        if highlights:
            results.append({
                "page": page_num +1,
                "highlights": highlights
            })
        else:
            print("No highlights found on this page.")

    return results

if __name__ == "__main__":
    # Define the PDF path and page range
    pdf_file = "conlaw.pdf"  # Ensure this path is correct and the file is in the same directory
    start_page = 576
    end_page = 579
    
    # Extract and print the highlights
    extracted_highlights = extract_highlights(pdf_file, start_page, end_page)
    
    # Optional: Save results to a file
    # import json
    # with open("highlights.json", "w", encoding="utf-8") as f:
    #     json.dump(extracted_highlights, f, ensure_ascii=False, indent=4)
