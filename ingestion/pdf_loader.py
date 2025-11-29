import os
import fitz  # PyMuPDF

def load_pdfs(pdf_dir):
    """
    Loads PDFs from a directory and returns a list of dicts:
    [{ "filename": str, "text": str }]
    """
    pdf_texts = []

    for fname in os.listdir(pdf_dir):
        if not fname.lower().endswith(".pdf"):
            continue
        path = os.path.join(pdf_dir, fname)
        doc_text = ""

        try:
            with fitz.open(path) as doc:
                for page in doc:
                    doc_text += page.get_text("text") + "\n"
        except Exception as e:
            print(f"⚠️ Error reading {fname}: {e}")
            continue

        pdf_texts.append({
            "filename": fname,
            "text": doc_text.strip()
        })

    return pdf_texts
