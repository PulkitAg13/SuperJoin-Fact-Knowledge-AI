import logging
from pathlib import Path
from typing import List, Dict, Any, Tuple
import fitz  # PyMuPDF

logger = logging.getLogger(__name__)

class PDFExtractor:
    @staticmethod
    def extract_pages(pdf_path: str, max_pages: int = 100) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
        """
        Extracts text page by page from a PDF file.
        Returns:
            pages: List of dicts with page_number (1-indexed), text, char_count
            issues: List of issues detected during extraction (e.g. scanned page, low text density)
        """
        pages = []
        issues = []

        path = Path(pdf_path)
        if not path.exists():
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")

        try:
            doc = fitz.open(str(path))
            total_pages = len(doc)
            pages_to_process = min(total_pages, max_pages)

            for page_idx in range(pages_to_process):
                page_num = page_idx + 1
                try:
                    page = doc[page_idx]
                    text = page.get_text("text") or ""
                    
                    # Clean text slightly (normalize whitespace)
                    clean_text = "\n".join(line.strip() for line in text.splitlines() if line.strip())
                    char_count = len(clean_text)

                    # Detection of scanning / low text extraction quality
                    # If page has very little text (< 40 chars) but has images, it might be scanned
                    images = page.get_images()
                    if char_count < 40 and len(images) > 0:
                        issues.append({
                            "category": "OCR_FAILURE",
                            "severity": "WARNING",
                            "page_number": page_num,
                            "description": f"Page {page_num} contains {len(images)} image(s) but negligible text ({char_count} chars). Scanned page OCR may be needed.",
                            "raw_snippet": clean_text[:200]
                        })
                    elif char_count < 20:
                        # Empty page or non-textual layout
                        issues.append({
                            "category": "LOW_TEXT_DENSITY",
                            "severity": "INFO",
                            "page_number": page_num,
                            "description": f"Page {page_num} has extremely low text density ({char_count} chars).",
                            "raw_snippet": clean_text[:200]
                        })

                    # Detection of potential tabular formatting anomalies
                    # Tables often have lots of numbers separated by tabs/spaces or repeated pipes
                    if clean_text.count("\t") > 5 or (clean_text.count("|") > 4 and clean_text.count("\n") > 5):
                        # Detect if table parsing might be disjointed
                        lines = clean_text.splitlines()
                        num_like_lines = sum(1 for l in lines if any(c.isdigit() for c in l) and len(l.split()) > 3)
                        if num_like_lines > 5:
                            issues.append({
                                "category": "TABLE_PARSING_WARNING",
                                "severity": "INFO",
                                "page_number": page_num,
                                "description": f"Page {page_num} contains tabular data structures which may require careful context association.",
                                "raw_snippet": "\n".join(lines[:6])
                            })

                    pages.append({
                        "page_number": page_num,
                        "text": clean_text,
                        "char_count": char_count,
                        "image_count": len(images)
                    })
                except Exception as page_err:
                    logger.error(f"Error extracting page {page_num}: {page_err}")
                    issues.append({
                        "category": "EXTRACTION_ERROR",
                        "severity": "ERROR",
                        "page_number": page_num,
                        "description": f"Failed to extract page {page_num}: {str(page_err)}",
                        "raw_snippet": ""
                    })

            doc.close()
        except Exception as e:
            logger.error(f"Failed to open PDF document {pdf_path}: {e}")
            issues.append({
                "category": "PDF_CORRUPTION",
                "severity": "ERROR",
                "page_number": 1,
                "description": f"Corrupted or unreadable PDF: {str(e)}",
                "raw_snippet": ""
            })
            raise

        return pages, issues
