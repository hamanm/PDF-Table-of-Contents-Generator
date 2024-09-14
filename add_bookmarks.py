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


# PyMuPDF allows us to read the labels assigned to each page. 
# We can create a mapping between page labels and page indices.
# Here's how to do it:
def get_page_label_map(doc):
    page_label_map = {}
    for i in range(len(doc)):
        page_label = doc.get_page_label(i)
        if page_label is not None:
            page_label_map[page_label.strip()] = i
    return page_label_map
# The above function creates a dictionary where the keys are the page labels (e.g., 'A', 'i', '1') and the values are the page indices in the PDF.


#We need to modify parse_page_number to use the page_label_map for accurate mapping.
def parse_page_number(page_str, page_label_map):
    page_str = page_str.strip()
    # Try to find the page label directly
    if page_str in page_label_map:
        return page_label_map[page_str]
    else:
        # Clean up page string (remove spaces)
        page_str_clean = page_str.replace(' ', '')
        if page_str_clean in page_label_map:
            return page_label_map[page_str_clean]
        else:
            # As a last resort, try matching numerically
            for label, index in page_label_map.items():
                # Try matching Arabic numerals
                if label.isdigit() and label == page_str:
                    return index
                # Try matching Roman numerals
                if roman_to_int(label) == roman_to_int(page_str):
                    return index
            raise ValueError(f"Page '{page_str}' not found in page labels.")


# In the add_bookmarks Function we pass the page_label_map to the parse_page_number function.
def add_bookmarks(pdf_path, toc_path, output_path):
    # Read the table of contents from the CSV file
    with open(toc_path, newline='', encoding='utf-8') as csvfile:
        toc_reader = csv.DictReader(csvfile)
        toc_entries = list(toc_reader)

    # Open the PDF file
    doc = fitz.open(pdf_path)

    # Get the page label map
    page_label_map = get_page_label_map(doc)

    # Build the Table of Contents (ToC) list
    toc = []
    for entry in toc_entries:
        title = entry['Title'].strip()
        page_str = entry['Page']
        level = int(entry.get('Level', 1))

        try:
            page_number = parse_page_number(page_str, page_label_map)
        except ValueError as e:
            print(e)
            continue

        toc.append([level, title, page_number])

    # Set the ToC in the PDF
    doc.set_toc(toc)

    # Save the updated PDF
    doc.save(output_path)
    print(f"Bookmarks added successfully to {output_path}")

if __name__ == "__main__":
    pdf_path = 'input.pdf'        # Path to your input PDF
    toc_path = 'toc.csv'          # Path to the table of contents CSV
    output_path = 'output.pdf'    # Path to the output PDF with bookmarks

    add_bookmarks(pdf_path, toc_path, output_path)
