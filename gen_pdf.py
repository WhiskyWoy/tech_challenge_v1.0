import pandas as pd
import numpy as np
import streamlit as st
import matplotlib.pyplot as plt
from fpdf import FPDF
import lorem
from pandas.plotting import table
import textwrap

# read csv
df = pd.read_csv("commonalities_and_differences.csv", sep='\t')
print(df)
# Define a function to add line breaks
def add_line_breaks(text):
    return '\n'.join(textwrap.wrap(text, width=70))

# Apply the function to each cell in the DataFrame
df = df.applymap(add_line_breaks)
print(df)

text = lorem.text()
pdf = FPDF()
pdf.add_page()

#pdf.set_font("Arial", size=12)
pdf.add_font('DejaVu', '', 'fonts/DejaVuSansCondensed.ttf', uni=True)
pdf.add_font('DejaVu', 'B', 'fonts/DejaVuSans-Bold.ttf', uni=True)
pdf.set_font('DejaVu', 'B', 16)

pdf.cell(200, 10, txt="Event Summary", ln=1, align="C")
pdf.set_font('DejaVu', '', 12)
pdf.cell(200, 10, txt=" ", ln=1, align="C")
#pdf.multi_cell(200, 10, txt=text.tolist()[0], ln=1, align="L")
pdf.multi_cell(150, 10, txt=text, align="L")
pdf.cell(200, 10, txt=" ", ln=1, align="C")
pdf.cell(200, 10, txt=" ", ln=1, align="C")
pdf.cell(200, 10, txt=" ", ln=1, align="C")
pdf.set_font('DejaVu', 'B', 16)
pdf.cell(200, 10, txt="Table of Facts", ln=1, align="C")
pdf.set_font('DejaVu', '', 14)
pdf.cell(200, 10, txt=" ", ln=1, align="C")

fig, ax = plt.subplots(figsize=(20, 10)) # set size frame
ax.xaxis.set_visible(False)  # hide the x axis
ax.yaxis.set_visible(False)  # hide the y axis
ax.set_frame_on(False)  # no visible frame
tabla = table(ax, df, loc='center', cellLoc='center')  # where df is your data frame
tabla.auto_set_font_size(True) # Activate set fontsize manually
#tabla.set_fontsize(10) # if ++fontsize is necessary ++colWidths
tabla.scale(1.2, 4) # Table size
plt.savefig('mytable.png')

#new page
pdf.add_page(orientation='L')

pdf.image('mytable.png', x = 0, y = 0, w = 300, h = 200)

pdf.output("output.pdf")