import csv
import fitz  # PyMuPDF
import re

def roman_to_int(roman):
    roman_numerals = {
        'i': 1, 'ii': 2, 'iii': 3, 'iv': 4, 'v': 5,
        'vi': 6, 'vii': 7, 'viii': 8, 'ix': 9, 'x': 10,
        'xi': 11, 'xii': 12, 'xiii': 13, 'xiv': 14, 'xv': 15,
        'xvi': 16, 'xvii': 17, 'xviii': 18, 'xix': 19, 'xx': 20,
        # Extend as needed
    }
    return roman_numerals.get(roman.lower())

# This function handles Roman and Arabic numbers
def parse_page_number(page_str, offset=0):
    page_str = page_str.strip()
    if page_str.isdigit():
        # Return the adjusted page number for Arabic numerals
        return int(page_str) - 1 + offset
    else:
        # Handle Roman numerals
        page_num = roman_to_int(page_str)
        if page_num is not None:
            return page_num - 1 + offset
        raise ValueError(f"Page '{page_str}' not recognized.")

def add_bookmarks(pdf_path, toc_path, output_path, offset=0):
    # Read the table of contents from the CSV file
    with open(toc_path, newline='', encoding='utf-8') as csvfile:
        toc_reader = csv.DictReader(csvfile)
        toc_entries = list(toc_reader)

    # Open the PDF file
    doc = fitz.open(pdf_path)

    # Extract existing bookmarks
    existing_toc = doc.get_toc()

    # Build the Table of Contents (ToC) list
    toc = []
    for i, entry in enumerate(toc_entries, start=1):
        title = entry['Title'].strip()
        page_str = entry['Page']
        level = int(entry.get('Level', 1))

        try:
            page_number = parse_page_number(page_str, offset)
        except ValueError as e:
            print(f"Error in row {i}: {e}")
            continue

        # Check for bad hierarchy levels
        if toc and level > toc[-1][0] + 1:
            print(f"Error: Bad hierarchy at row {i}. Level {level} follows level {toc[-1][0]}")
            continue

        toc.append([level, title, page_number])

    # Merge existing ToC with new ToC
    merged_toc = existing_toc + toc

    # Set the merged ToC in the PDF
    doc.set_toc(merged_toc)

    # Save the updated PDF
    doc.save(output_path)
    print(f"Bookmarks added successfully to {output_path}")


if __name__ == "__main__":
    pdf_path = 'input.pdf'        # Path to your input PDF
    toc_path = 'readings.csv'          # Path to the table of contents CSV
    output_path = 'output.pdf'    # Path to the output PDF with bookmarks

    offset = 21  # Since Page 1 in the TOC is Page 21 in the PDF, set offset to 20
    
    add_bookmarks(pdf_path, toc_path, output_path, offset)
