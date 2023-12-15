from ironpdf import *

pdf = PdfDocument.FromFile("Rechnung Arichtekt und Büromöbel 12 2023 Conner Trompf.pdf")
# Extract all pages to a folder as image files
pdf.RasterizeToImageFiles("pdfs/*.png",DPI=96)