"""
file_utils.py — Helper functions for extracting plain text from uploaded files
Supports: .txt, .pdf, .md, .csv, .json
Handles validation: file size limit, unsupported extensions, empty files.
"""

import io
import os
from typing import Tuple

try:
    import pypdf
    HAS_PYPDF = True
except ImportError:
    HAS_PYPDF = False

# Maximum file size allowed (5MB)
MAX_FILE_SIZE_BYTES = 5 * 1024 * 1024
ALLOWED_EXTENSIONS = {".txt", ".pdf", ".md", ".csv", ".json", ".log"}


def extract_text_from_file(filename: str, file_bytes: bytes) -> Tuple[str, str]:
    """
    Extracts readable plain text from uploaded file bytes.
    Returns a tuple of (extracted_text, error_message).
    If extraction succeeds, error_message is "".
    If extraction fails, extracted_text is "" and error_message describes the problem.
    """
    if not file_bytes:
        return "", "The uploaded file is empty."

    if len(file_bytes) > MAX_FILE_SIZE_BYTES:
        return "", f"File size exceeds limit of 5MB (Received: {len(file_bytes) / (1024*1024):.2f}MB)."

    ext = os.path.splitext(filename.lower())[1]
    if ext not in ALLOWED_EXTENSIONS:
        return "", f"Unsupported file type '{ext}'. Supported formats: {', '.join(sorted(ALLOWED_EXTENSIONS))}."

    try:
        if ext in {".txt", ".md", ".csv", ".json", ".log"}:
            # Handle text formats with UTF-8 / fallback encoding
            try:
                text = file_bytes.decode("utf-8")
            except UnicodeDecodeError:
                text = file_bytes.decode("latin-1", errors="replace")
            
            if not text.strip():
                return "", "File contains no readable text."
            return text.strip(), ""

        elif ext == ".pdf":
            if not HAS_PYPDF:
                return "", "PDF text extraction requires the 'pypdf' package. Run 'pip install pypdf' to enable PDF parsing."
            # Extract text page-by-page from PDF
            pdf_reader = pypdf.PdfReader(io.BytesIO(file_bytes))
            extracted_pages = []
            
            for i, page in enumerate(pdf_reader.pages):
                page_text = page.extract_text()
                if page_text and page_text.strip():
                    extracted_pages.append(f"--- Page {i+1} ---\n" + page_text.strip())
            
            full_text = "\n\n".join(extracted_pages).strip()
            
            if not full_text:
                return "", "Could not extract readable text from PDF. It may be scanned or image-only."
            
            return full_text, ""

    except Exception as e:
        return "", f"Failed to parse file '{filename}': {str(e)}"

    return "", "Unknown extraction error."
