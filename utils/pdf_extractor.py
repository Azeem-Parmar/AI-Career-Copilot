import pdfplumber

def extract_resume_text(uploaded_file):

    resume_text = ""

    with pdfplumber.open(uploaded_file) as pdf:

        for page in pdf.pages:

            text = page.extract_text()

            if text:
                resume_text += text

    return resume_text, len(pdf.pages)