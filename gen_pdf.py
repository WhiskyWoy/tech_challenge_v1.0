import streamlit as st
import pandas as pd
import lorem
from fpdf import FPDF



#text = st.session_state.event_summary['summary']
#df = st.session_state.fact_table 
df = pd.read_excel("fact_table.xlsx")
#use first column as index and drop it
df.set_index(df.columns[0], inplace=True)
text = lorem.text()

pdf = FPDF()
pdf.add_page()

#pdf.set_font("Arial", size=12)
pdf.add_font('DejaVu', '', 'DejaVuSansCondensed.ttf', uni=True)
pdf.add_font('DejaVu', 'B', 'DejaVuSans-Bold.ttf', uni=True)
pdf.set_font('DejaVu', 'B', 16)

pdf.cell(200, 10, txt="Event Summary", ln=1, align="C")
pdf.set_font('DejaVu', '', 14)
pdf.cell(200, 10, txt=" ", ln=1, align="C")
#pdf.cell(200, 10, txt=text.tolist()[0], ln=1, align="L")
pdf.multi_cell(200, 10, txt=text, align="L")
pdf.cell(200, 10, txt=" ", ln=1, align="C")
pdf.cell(200, 10, txt=" ", ln=1, align="C")
pdf.cell(200, 10, txt=" ", ln=1, align="C")
pdf.set_font('DejaVu', 'B', 16)
pdf.cell(200, 10, txt="Table of Facts", ln=1, align="C")
pdf.set_font('DejaVu', '', 14)
pdf.cell(200, 10, txt=" ", ln=1, align="C")

# Add a cell for each column header
for i in range(len(df.columns)):
    pdf.cell(40, 10, txt=df.columns[i], ln=0, align='C')

# Line break
pdf.ln(10)

# Add a cell for each item of data
for i in range(len(df)):
    for j in range(len(df.columns)):
        pdf.cell(40, 10, txt=str(df.iloc[i, j]), ln=0, align='C')
    pdf.ln(10)


pdf.output("output.pdf")