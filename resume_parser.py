"""
resume_parser.py - Extract text from uploaded PDF resumes.
Uses pdfplumber for reliable text extraction from PDF files.
"""

import pdfplumber
import io
import logging

logger = logging.getLogger(__name__)


def extract_text_from_pdf(file_bytes: bytes) -> str:
    """
    Extract raw text from a PDF file given its bytes content.
    
    Args:
        file_bytes: The raw bytes of the uploaded PDF file.
    
    Returns:
        A string containing all extracted text from the PDF.
    
    Raises:
        ValueError: If the PDF is password-protected, empty, or unreadable.
    """
    try:
        text_parts = []

        # Open PDF from bytes using a BytesIO stream
        with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
            if len(pdf.pages) == 0:
                raise ValueError("The uploaded PDF has no pages.")

            for page_num, page in enumerate(pdf.pages, start=1):
                page_text = page.extract_text()
                if page_text:
                    text_parts.append(page_text)
                else:
                    logger.warning(f"[Parser] Page {page_num} yielded no text (may be image-based).")

        if not text_parts:
            raise ValueError(
                "Could not extract any text from the PDF. "
                "The file may be image-based or scanned. Please upload a text-based PDF."
            )

        full_text = "\n".join(text_parts)
        logger.info(f"[Parser] Successfully extracted {len(full_text)} characters from PDF.")
        return full_text

    except pdfplumber.pdfminer.pdfparser.PDFSyntaxError:
        raise ValueError("Invalid or corrupted PDF file. Please upload a valid PDF.")

    except Exception as e:
        if isinstance(e, ValueError):
            raise  # Re-raise our own ValueError
        logger.error(f"[Parser] Unexpected error: {e}")
        raise ValueError(f"Error reading PDF: {str(e)}")
