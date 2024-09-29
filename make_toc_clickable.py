import fitz  # PyMuPDF
import re
import os

def find_toc_range(doc):
    """
    Attempt to find the TOC by scanning the first 20 pages.
    This function returns a suggested TOC range.
    """
    print("Attempting to detect Table of Contents (TOC) range...")
    toc_pages = []
    
    # Scan through the first 20 pages to locate potential TOC pages
    for i in range(min(20, doc.page_count)):
        page = doc.load_page(i)
        text = page.get_text("text")
        if "TABLE OF CONTENTS" in text.upper():
            print(f"Potential TOC starting page detected: Page {i + 1}")
            toc_pages.append(i)
    
    if toc_pages:
        start_page = toc_pages[0] + 1  # Convert to 1-based index
        end_page = min(start_page + 9, doc.page_count)
        return start_page, end_page
    else:
        return None, None

def find_page_offset(doc):
    """
    Attempt to find the page offset by searching for 'Page 1' or similar indicators.
    Returns the page offset if found, else None.
    """
    print("\nAttempting to detect page offset (physical pages before logical page 1)...")
    for i in range(doc.page_count):
        page = doc.load_page(i)
        text = page.get_text("text").upper()
        
        # Look for 'PAGE 1' or similar indicators
        if re.search(r'\bPAGE\s*1\b', text) or re.search(r'\b1\b', text):
            print(f"Potential logical page 1 detected at physical page {i + 1}")
            return i  # Offset is the number of pages before logical page 1
    print("Could not automatically detect page offset.")
    return None

def is_affirmative(response):
    """
    Check if the response is an affirmative (yes, y, 1, true, etc.)
    """
    affirmative_responses = {'yes', 'y', '1', 'true', 'yeah', 'sure', 'ok'}
    return response.strip().lower() in affirmative_responses

def add_links_to_toc(pdf_path, toc_start, toc_end, page_offset):
    """
    Add internal links to the TOC entries in the PDF, accounting for page offset.
    Provides detailed debugging information for each TOC entry.
    """
    doc = fitz.open(pdf_path)
    toc_pages = []
    for i in range(toc_start - 1, toc_end):
        toc_pages.append(doc.load_page(i))

    count_links = 0
    for page_num, page in enumerate(toc_pages, start=toc_start):
        print(f"\nProcessing page {page_num}...")
        blocks = page.get_text("dict")["blocks"]
        for block in blocks:
            if block["type"] != 0:
                continue  # Skip non-text blocks
            for line in block["lines"]:
                # Combine all spans in the line to form the complete text
                line_text = " ".join([span["text"] for span in line["spans"]]).strip()
                print(f"\nChecking line: '{line_text}' on page {page_num}")
                
                # Enhanced regex to capture titles followed by page numbers with flexible separators
                match = re.match(r'^(.*?)\s*[\.\-]*\s*(\d+)$', line_text)
                if match:
                    title = match.group(1).strip()
                    logical_page = int(match.group(2).strip())
                    physical_page = logical_page + page_offset - 1  # Adjust for zero-based index
                    
                    # Validate the physical page number
                    if physical_page < 0 or physical_page >= doc.page_count:
                        print(f"Invalid physical page number {physical_page + 1} for TOC entry '{title}'. Skipping.")
                        continue
                    
                    # Get the bounding box for the entire line
                    spans = line["spans"]
                    if spans:
                        # Define the rectangle using the first and last span's bbox
                        bbox_start = spans[0]["bbox"]
                        bbox_end = spans[-1]["bbox"]
                        rect = fitz.Rect(bbox_start[0], bbox_start[1], bbox_end[2], bbox_end[3])
                    else:
                        rect = fitz.Rect(block["bbox"])
                    
                    print(f"Matched TOC entry: Title = '{title}', Logical Page = {logical_page}, Physical Page = {physical_page + 1}")
                    print(f"Creating link to physical page {physical_page + 1}...")
                    
                    try:
                        # Add a link annotation with the kind 'LINK_GOTO' to specify internal link
                        page.insert_link({
                            "from": rect, 
                            "page": physical_page, 
                            "kind": fitz.LINK_GOTO
                        })
                        print(f"Link successfully created for '{title}' to physical page {physical_page + 1}")
                        count_links += 1
                    except Exception as e:
                        print(f"Error creating link for '{title}': {e}")
                else:
                    print(f"No match found for line on page {page_num}")

    print(f"\nTotal links created: {count_links}")
    output_path = os.path.splitext(pdf_path)[0] + "_linked.pdf"
    doc.save(output_path)
    doc.close()
    print(f"Saved linked PDF as {output_path}.")

def get_user_page_offset():
    """
    Prompt the user to enter the page offset.
    """
    while True:
        try:
            offset = int(input("\nEnter the number of physical PDF pages that precede logical page 1 (e.g., if logical page 1 is physical page 21, enter 20): ").strip())
            if offset < 0:
                print("Please enter a non-negative integer.")
                continue
            return offset
        except ValueError:
            print("Invalid input. Please enter a numeric value.")

if __name__ == "__main__":
    # Set the path to the PDF file
    pdf_path = r"C:\Users\ES\Documents\PDF Table of Contents Generator\crim.pdf"
    
    if not os.path.isfile(pdf_path):
        print(f"File not found: {pdf_path}")
        exit(1)
    
    # Open the PDF
    try:
        doc = fitz.open(pdf_path)
    except Exception as e:
        print(f"Error opening PDF file: {e}")
        exit(1)

    # Step 1: Detect TOC range
    detected_start, detected_end = find_toc_range(doc)

    if detected_start and detected_end:
        print(f"\nDetected TOC range: Pages {detected_start} to {detected_end}.")
        confirm = input("Is this range correct? (yes/no): ").strip().lower()

        if not is_affirmative(confirm):
            print("\nPlease enter the correct TOC range manually.")
            try:
                toc_start = int(input("Enter the starting page number for the TOC: ").strip())
                toc_end = int(input("Enter the ending page number for the TOC: ").strip())
            except ValueError:
                print("Invalid input. Please enter numeric page numbers.")
                exit(1)
        else:
            toc_start, toc_end = detected_start, detected_end
    else:
        print("\nCould not automatically detect TOC.")
        try:
            toc_start = int(input("Enter the starting page number for the TOC: ").strip())
            toc_end = int(input("Enter the ending page number for the TOC: ").strip())
        except ValueError:
            print("Invalid input. Please enter numeric page numbers.")
            exit(1)

    # Step 2: Detect page offset
    detected_offset = find_page_offset(doc)

    if detected_offset is not None:
        # Suggest the detected offset to the user
        print(f"\nDetected page offset: {detected_offset} physical pages precede logical page 1.")
        confirm_offset = input("Is this offset correct? (yes/no): ").strip().lower()

        if not is_affirmative(confirm_offset):
            # Prompt the user to input the correct offset
            page_offset = get_user_page_offset()
        else:
            page_offset = detected_offset
    else:
        # Prompt the user to input the offset manually
        page_offset = get_user_page_offset()

    # Validate TOC range
    if toc_start < 1 or toc_end > doc.page_count or toc_start > toc_end:
        print("Invalid TOC range specified.")
        exit(1)

    # Add links to the TOC using the confirmed range and page offset
    add_links_to_toc(pdf_path, toc_start, toc_end, page_offset)
