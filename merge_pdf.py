import PyPDF2

# Create a PDF file merger object
merger = PyPDF2.PdfMerger()

# List of PDF files to merge
pdf_files = ["output.pdf", "pdfs/brief_plaintiff_highlighted.pdf", "pdfs/brief_defendant_highlighted.pdf"]

# Loop through the PDF files and add each one to the merger
for pdf_file in pdf_files:
    with open(pdf_file, "rb") as fileobj:
        merger.append(fileobj)

# Write the merged PDF to a new file
with open("merged.pdf", "wb") as outfile:
    merger.write(outfile)