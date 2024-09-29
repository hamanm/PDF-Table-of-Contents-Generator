import fitz  # PyMuPDF
import re
import os

def extract_toc(page):
    """
    Extract text from a page and return lines.
    """
    text = page.get_text("text")
    lines = text.split('\n')
    return lines

def parse_toc(lines):
    """
    Parse TOC lines to extract titles and page numbers.
    This function is flexible to handle different TOC formats.
    """
    toc_entries = []
    # Adjusted regex to capture titles followed by page numbers with mixed separators (spaces, dots, dashes)
    toc_pattern = re.compile(r'^(.*?)\s+[-.]*\s+(\d+)$')

    for line in lines:
        match = toc_pattern.match(line)
        if match:
            title = match.group(1).strip()
            page_num = int(match.group(2).strip())
            toc_entries.append((title, page_num))
    return toc_entries

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
        start_page = toc_pages[0] + 1
        end_page = min(start_page + 9, doc.page_count)
        return start_page, end_page
    else:
        return None, None

def add_links_to_toc(pdf_path, toc_start, toc_end):
    """
    Add internal links to the TOC entries in the PDF, for the user-confirmed range.
    Debugs the link creation process by printing out every step.
    """
    doc = fitz.open(pdf_path)
    toc_pages = []
    for i in range(toc_start - 1, toc_end):
        toc_pages.append(doc.load_page(i))

    all_lines = []
    for page in toc_pages:
        all_lines.extend(extract_toc(page))

    toc_entries = parse_toc(all_lines)

    if not toc_entries:
        print(f"No TOC entries found in pages {toc_start} to {toc_end}.")
        return

    print(f"Found {len(toc_entries)} TOC entries in pages {toc_start} to {toc_end}.")

    # Debugging for each TOC entry, showing line, page number, and success message
    for page_num, page in enumerate(toc_pages, start=toc_start):
        blocks = page.get_text("blocks")
        for block in blocks:
            block_text = block[4].strip()

            # Print out every block it reads, even if no match is found
            print(f"Checking block: '{block_text}' on page {page_num}")

            match = re.match(r'^(.*?)\s+[-.]*\s+(\d+)$', block_text)
            if match:
                title = match.group(1).strip()
                target_page = int(match.group(2).strip()) - 1
                rect = fitz.Rect(block[:4])
                print(f"'{title}' found on page {page_num}")
                print(f"Creating link to page {target_page + 1}...")
                
                try:
                    # Add a link annotation with the kind 'LINK_GOTO' to specify internal link
                    page.insert_link({"from": rect, "page": target_page, "kind": fitz.LINK_GOTO})
                    print(f"Link successfully created for '{title}' to page {target_page + 1}")
                except Exception as e:
                    print(f"Error creating link for '{title}': {e}")
            else:
                print(f"No match found for block on page {page_num}")

    output_path = os.path.splitext(pdf_path)[0] + "_linked.pdf"
    doc.save(output_path)
    doc.close()
    print(f"Saved linked PDF as {output_path}.")

def is_affirmative(response):
    """
    Check if the response is an affirmative (yes, y, 1, true, etc.)
    """
    affirmative_responses = {'yes', 'y', '1', 'true', 'yeah', 'sure', 'ok'}
    return response.strip().lower() in affirmative_responses

if __name__ == "__main__":
    pdf_path = r"C:\Users\ES\Documents\PDF Table of Contents Generator\crim.pdf"
    doc = fitz.open(pdf_path)

    detected_start, detected_end = find_toc_range(doc)

    if detected_start and detected_end:
        print(f"Detected TOC range: Pages {detected_start} to {detected_end}.")
        confirm = input("Is this range correct? (yes/no): ").strip().lower()

        if not is_affirmative(confirm):
            toc_start = int(input("Enter the starting page number for the TOC: ").strip())
            toc_end = int(input("Enter the ending page number for the TOC: ").strip())
        else:
            toc_start, toc_end = detected_start, detected_end
    else:
        print("Could not automatically detect TOC.")
        toc_start = int(input("Enter the starting page number for the TOC: ").strip())
        toc_end = int(input("Enter the ending page number for the TOC: ").strip())

    add_links_to_toc(pdf_path, toc_start, toc_end)
