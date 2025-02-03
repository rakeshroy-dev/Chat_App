import pdfplumber

# Open the PDF file
with pdfplumber.open('C:\Users\chints14\Downloads\chat_history.pdf') as pdf:
    # Get the first page
    first_page = pdf.pages[0]
    # Extract text from the first page
    text = first_page.extract_text()
    print(text)