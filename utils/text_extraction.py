"""
Text Extraction Utilities
==========================
Read textual content from PDF, DOCX and plain-text files.
Used by the Content-Mining command to search *inside* documents.
"""

from __future__ import annotations
import os


def extract_text(filepath: str) -> str:
    """
    Return the full text content of a file.
    Supports: .txt, .pdf, .docx
    Returns empty string on failure.
    """
    ext = os.path.splitext(filepath)[1].lower()

    try:
        if ext == ".txt":
            return _read_txt(filepath)
        elif ext == ".pdf":
            return _read_pdf(filepath)
        elif ext == ".docx":
            return _read_docx(filepath)
    except Exception as e:
        print(f"  [WARN] Could not read {filepath}: {e}")
    return ""


def _read_txt(path: str) -> str:
    encodings = ["utf-8", "latin-1", "cp1252"]
    for enc in encodings:
        try:
            with open(path, "r", encoding=enc) as f:
                return f.read()
        except (UnicodeDecodeError, UnicodeError):
            continue
    return ""


def _read_pdf(path: str) -> str:
    from PyPDF2 import PdfReader

    reader = PdfReader(path)
    pages = []
    for page in reader.pages:
        text = page.extract_text()
        if text:
            pages.append(text)
    return "\n".join(pages)


def _read_docx(path: str) -> str:
    from docx import Document

    doc = Document(path)
    return "\n".join(para.text for para in doc.paragraphs if para.text.strip())
