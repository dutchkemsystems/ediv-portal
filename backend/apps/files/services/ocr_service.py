"""OCR Service for extracting text from images and scanned PDFs."""

import io
import logging
import os
import tempfile

from django.conf import settings
from PIL import Image

logger = logging.getLogger(__name__)

# Try to import OCR libraries
PYTESSERACT_AVAILABLE = False
CV2_AVAILABLE = False

try:
    import pytesseract

    PYTESSERACT_AVAILABLE = True
except ImportError:
    logger.info("pytesseract not available - OCR for images disabled")

try:
    import cv2

    import numpy as np

    CV2_AVAILABLE = True
except ImportError:
    logger.info("opencv not available - advanced image preprocessing disabled")


class OCRService:
    """Service for extracting text from images and scanned documents."""

    SUPPORTED_IMAGE_FORMATS = ["jpeg", "jpg", "png", "tiff", "tif", "bmp", "gif", "webp"]
    SUPPORTED_OCR_LANGUAGES = ["eng", "fra", "ara", "deu", "spa", "por", "ita", "nld", "swe", "dan"]

    @staticmethod
    def is_available():
        """Check if OCR is available."""
        return PYTESSERACT_AVAILABLE

    @staticmethod
    def extract_text_from_image(image_path, language="eng", preprocess="auto"):
        """
        Extract text from an image file using OCR.

        Args:
            image_path: Path to the image file
            language: Tesseract language code (default: eng)
            preprocess: Preprocessing mode ('auto', 'none', 'grayscale', 'threshold', 'denoise')

        Returns:
            dict: {text: str, confidence: float, word_count: int, language: str}
        """
        if not PYTESSERACT_AVAILABLE:
            return {
                "text": "",
                "confidence": 0,
                "word_count": 0,
                "language": language,
                "error": "OCR library not installed. Install pytesseract and Tesseract-OCR.",
            }

        try:
            img = Image.open(image_path)

            # Preprocess image for better OCR
            if preprocess != "none":
                img = OCRService._preprocess_image(img, preprocess)

            # Get detailed OCR data
            data = pytesseract.image_to_data(img, lang=language, output_type=pytesseract.Output.DICT)

            # Extract text
            text = pytesseract.image_to_string(img, lang=language).strip()

            # Calculate average confidence (excluding -1 entries)
            confidences = [int(c) for c in data["conf"] if int(c) > 0]
            avg_confidence = sum(confidences) / len(confidences) if confidences else 0

            # Count words
            word_count = len([w for w in text.split() if w.strip()])

            return {
                "text": text,
                "confidence": round(avg_confidence, 2),
                "word_count": word_count,
                "language": language,
                "error": None,
            }

        except Exception as e:
            logger.error(f"OCR extraction failed for {image_path}: {e}")
            return {
                "text": "",
                "confidence": 0,
                "word_count": 0,
                "language": language,
                "error": str(e),
            }

    @staticmethod
    def extract_text_from_image_bytes(image_bytes, filename="image.jpg", language="eng", preprocess="auto"):
        """Extract text from image bytes (e.g., from uploaded file)."""
        try:
            img = Image.open(io.BytesIO(image_bytes))
            # Save to temp file for processing
            with tempfile.NamedTemporaryFile(
                suffix=os.path.splitext(filename)[1] or ".jpg", delete=False
            ) as tmp:
                img.save(tmp.name)
                result = OCRService.extract_text_from_image(tmp.name, language, preprocess)
                os.unlink(tmp.name)
                return result
        except Exception as e:
            logger.error(f"OCR extraction from bytes failed: {e}")
            return {
                "text": "",
                "confidence": 0,
                "word_count": 0,
                "language": language,
                "error": str(e),
            }

    @staticmethod
    def extract_text_from_pdf(pdf_path, language="eng", pages=None, preprocess="auto"):
        """
        Extract text from a PDF file, handling both digital and scanned PDFs.

        For digital PDFs: uses PyPDF2 for text extraction.
        For scanned PDFs: converts pages to images and runs OCR.

        Args:
            pdf_path: Path to the PDF file
            language: Tesseract language code
            pages: List of page numbers to process (None = all)
            preprocess: Image preprocessing mode

        Returns:
            dict: {text: str, pages_processed: int, method: str, confidence: float}
        """
        result = {"text": "", "pages_processed": 0, "method": "none", "confidence": 0, "error": None}

        # First try digital text extraction
        try:
            from PyPDF2 import PdfReader

            reader = PdfReader(pdf_path)
            digital_text = ""
            for i, page in enumerate(reader.pages):
                if pages and i not in pages:
                    continue
                page_text = page.extract_text() or ""
                digital_text += page_text + "\n"

            if digital_text.strip() and len(digital_text.strip()) > 50:
                result["text"] = digital_text.strip()
                result["pages_processed"] = len(reader.pages)
                result["method"] = "digital"
                result["confidence"] = 100.0
                return result
        except Exception as e:
            logger.warning(f"Digital PDF extraction failed: {e}")

        # Fall back to OCR for scanned PDFs
        if not PYTESSERACT_AVAILABLE:
            result["error"] = "PDF appears to be scanned. OCR library not installed."
            return result

        try:
            import fitz  # PyMuPDF

            doc = fitz.open(pdf_path)
            ocr_text = ""
            total_confidence = 0
            pages_processed = 0

            for i, page in enumerate(doc):
                if pages and i not in pages:
                    continue

                # Convert page to image
                pix = page.get_pixmap(dpi=300)
                img = Image.open(io.BytesIO(pix.tobytes("png")))

                # Preprocess
                if preprocess != "none":
                    img = OCRService._preprocess_image(img, preprocess)

                # OCR
                page_text = pytesseract.image_to_string(img, lang=language).strip()
                ocr_text += page_text + "\n"

                # Confidence
                data = pytesseract.image_to_data(img, lang=language, output_type=pytesseract.Output.DICT)
                confidences = [int(c) for c in data["conf"] if int(c) > 0]
                if confidences:
                    total_confidence += sum(confidences) / len(confidences)
                pages_processed += 1

            doc.close()

            result["text"] = ocr_text.strip()
            result["pages_processed"] = pages_processed
            result["method"] = "ocr"
            result["confidence"] = round(total_confidence / pages_processed, 2) if pages_processed > 0 else 0

        except ImportError:
            # PyMuPDF not available, try pdf2image + pytesseract
            try:
                from pdf2image import convert_from_path

                images = convert_from_path(pdf_path, dpi=300)
                ocr_text = ""
                total_confidence = 0
                pages_processed = 0

                for i, img in enumerate(images):
                    if pages and i not in pages:
                        continue

                    if preprocess != "none":
                        img = OCRService._preprocess_image(img, preprocess)

                    page_text = pytesseract.image_to_string(img, lang=language).strip()
                    ocr_text += page_text + "\n"

                    data = pytesseract.image_to_data(img, lang=language, output_type=pytesseract.Output.DICT)
                    confidences = [int(c) for c in data["conf"] if int(c) > 0]
                    if confidences:
                        total_confidence += sum(confidences) / len(confidences)
                    pages_processed += 1

                result["text"] = ocr_text.strip()
                result["pages_processed"] = pages_processed
                result["method"] = "ocr"
                result["confidence"] = round(total_confidence / pages_processed, 2) if pages_processed > 0 else 0

            except ImportError:
                result["error"] = "Install PyMuPDF or pdf2image for scanned PDF OCR support."

        except Exception as e:
            logger.error(f"PDF OCR extraction failed: {e}")
            result["error"] = str(e)

        return result

    @staticmethod
    def extract_tables_from_image(image_path, language="eng"):
        """
        Extract tabular data from an image using OCR with TSV output.

        Returns:
            dict: {rows: list, headers: list, text: str, confidence: float}
        """
        if not PYTESSERACT_AVAILABLE:
            return {"rows": [], "headers": [], "text": "", "confidence": 0, "error": "OCR not available"}

        try:
            img = Image.open(image_path)
            img = OCRService._preprocess_image(img, "auto")

            # Get TSV output for table detection
            tsv_data = pytesseract.image_to_data(img, lang=language, output_type=pytesseract.Output.DICT)

            # Group words by line
            lines = {}
            for i in range(len(tsv_data["text"])):
                word = tsv_data["text"][i].strip()
                if not word:
                    continue
                line_num = tsv_data["line_num"][i]
                block_num = tsv_data["block_num"][i]
                key = (block_num, line_num)
                if key not in lines:
                    lines[key] = []
                lines[key].append({
                    "text": word,
                    "x": tsv_data["left"][i],
                    "y": tsv_data["top"][i],
                    "width": tsv_data["width"][i],
                    "height": tsv_data["height"][i],
                    "conf": tsv_data["conf"][i],
                })

            # Sort lines by vertical position
            sorted_lines = sorted(lines.items(), key=lambda x: x[0][1])

            rows = []
            all_text = []
            confidences = []

            for (block, line), words in sorted_lines:
                # Sort words by horizontal position
                words.sort(key=lambda w: w["x"])
                row_text = " ".join(w["text"] for w in words)
                all_text.append(row_text)
                rows.append([w["text"] for w in words])
                confidences.extend([int(w["conf"]) for w in words if int(w["conf"]) > 0])

            # First row is likely headers
            headers = rows[0] if rows else []
            data_rows = rows[1:] if len(rows) > 1 else []

            avg_confidence = sum(confidences) / len(confidences) if confidences else 0

            return {
                "headers": headers,
                "rows": data_rows,
                "text": "\n".join(all_text),
                "confidence": round(avg_confidence, 2),
                "error": None,
            }

        except Exception as e:
            logger.error(f"Table extraction from image failed: {e}")
            return {"rows": [], "headers": [], "text": "", "confidence": 0, "error": str(e)}

    @staticmethod
    def _preprocess_image(img, mode="auto"):
        """
        Preprocess image for better OCR accuracy.

        Modes:
        - auto: Choose best preprocessing based on image analysis
        - grayscale: Convert to grayscale
        - threshold: Apply binary threshold
        - denoise: Remove noise
        """
        if not CV2_AVAILABLE:
            # Fallback: just convert to RGB
            if img.mode != "RGB":
                img = img.convert("RGB")
            return img

        try:
            # Convert PIL to OpenCV format
            import numpy as np

            img_array = np.array(img)

            if len(img_array.shape) == 3:
                gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
            else:
                gray = img_array

            if mode == "auto":
                # Analyze image to choose best preprocessing
                mean_intensity = gray.mean()
                std_intensity = gray.std()

                if std_intensity < 30:
                    # Low contrast - enhance
                    gray = cv2.equalizeHist(gray)
                    mode = "threshold"
                else:
                    mode = "grayscale"

            if mode == "grayscale":
                pass  # Already grayscale
            elif mode == "threshold":
                # Adaptive threshold for varying lighting
                gray = cv2.adaptiveThreshold(
                    gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
                )
            elif mode == "denoise":
                gray = cv2.fastNlMeansDenoising(gray, None, 10, 7, 21)

            # Convert back to PIL
            return Image.fromarray(gray)

        except Exception as e:
            logger.warning(f"Image preprocessing failed: {e}")
            if img.mode != "RGB":
                img = img.convert("RGB")
            return img

    @staticmethod
    def detect_language(image_path):
        """Detect the primary language in an image using OCR."""
        if not PYTESSERACT_AVAILABLE:
            return {"language": "eng", "confidence": 0}

        try:
            img = Image.open(image_path)
            # Use tesseract's OSD (orientation and script detection)
            osd = pytesseract.image_to_osd(img, output_type=pytesseract.Output.DICT)
            return {
                "language": osd.get("lang", "eng"),
                "confidence": osd.get("lang_conf", 0),
            }
        except Exception:
            return {"language": "eng", "confidence": 0}

    @staticmethod
    def get_supported_formats():
        """Return list of formats supported by OCR."""
        return {
            "images": OCRService.SUPPORTED_IMAGE_FORMATS,
            "pdf": True,
            "languages": OCRService.SUPPORTED_OCR_LANGUAGES,
        }
