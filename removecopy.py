import fitz  # PyMuPDF

def remove_text_from_pdf(pdf_path, output_pdf_path, text_to_remove):
    # Open the PDF
    doc = fitz.open(pdf_path)

    # Loop through all pages
    for page_num in range(doc.page_count):
        page = doc.load_page(page_num)
        
        # Search for the text and get its position
        text_instances = page.search_for(text_to_remove)
        
        # Redact each instance of the text
        for inst in text_instances:
            page.add_redact_annot(inst, fill=(1, 1, 1))  # Mark the text for redaction (fill with white color)
        
        # Apply the redaction to remove the text
        page.apply_redactions()
    
    # Save the modified PDF to a new file
    doc.save(output_pdf_path)
    doc.close()
    print(f"Text '{text_to_remove}' has been redacted and saved to '{output_pdf_path}'.")

# Path to the original PDF
pdf_path = "conlaw.pdf"  # Replace this with your actual PDF file path

# Path to save the modified PDF
output_pdf_path = "conlaw_modified.pdf"

# Text to remove
text_to_remove = "© [2022] Emond Montgomery Publications. All Rights Reserved"

# Call the function to remove the text
remove_text_from_pdf(pdf_path, output_pdf_path, text_to_remove)
