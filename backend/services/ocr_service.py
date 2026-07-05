import io
from PIL import Image
from google.cloud import vision
from typing import Tuple
import logging

from config import settings

logger = logging.getLogger(__name__)

class OCRService:
    DEMO_TEXT = """DocuLens AI demo upload

Topic: Study Notes

Main ideas:
- Photos can be converted into searchable notes.
- OCR extracts raw text from the image.
- The formatting step organizes raw text into headings, bullet points, and Markdown.

Example formula: F = ma

Next steps:
1. Review the formatted note.
2. Edit anything that needs cleanup.
3. Save it under the right course."""

    def __init__(self):
        """Initialize OCR using explicit credentials or Google ADC."""
        self.client = None
        try:
            # The Google client resolves credentials through Application Default
            # Credentials (ADC), including GOOGLE_APPLICATION_CREDENTIALS when set.
            self.client = vision.ImageAnnotatorClient()
        except Exception as e:
            if not settings.enable_demo_ai_fallback:
                raise
            logger.warning(f"Google Vision client unavailable; demo OCR fallback enabled: {e}")
    
    def preprocess_image(self, image_bytes: bytes) -> bytes:
        """
        Preprocess an image to improve OCR accuracy.
        - Resize large images
        - Improve input consistency
        """
        try:
            img = Image.open(io.BytesIO(image_bytes))
            
            # Resize the image if it is too large.
            max_size = 2048
            if max(img.size) > max_size:
                ratio = max_size / max(img.size)
                new_size = tuple(int(dim * ratio) for dim in img.size)
                img = img.resize(new_size, Image.Resampling.LANCZOS)
            
            # Convert RGBA images to RGB.
            if img.mode == 'RGBA':
                img = img.convert('RGB')
            
            # Serialize the processed image to bytes.
            output = io.BytesIO()
            img.save(output, format='JPEG', quality=95)
            return output.getvalue()
            
        except Exception as e:
            logger.error(f"Image preprocessing failed: {str(e)}")
            return image_bytes  # Return the original image.
    
    def demo_extract_text(self) -> Tuple[str, float]:
        """Return deterministic OCR text for local demos without cloud credentials."""
        return self.DEMO_TEXT, 0.99

    def extract_text(self, image_bytes: bytes) -> Tuple[str, float]:
        """
        Extract text from an image.
        
        Returns:
            Tuple[str, float]: Extracted text and average confidence.
        """
        if self.client is None:
            if settings.enable_demo_ai_fallback:
                logger.warning("Using demo OCR fallback")
                return self.demo_extract_text()
            raise Exception("Google Vision OCR is not configured")

        try:
            # Preprocess the image.
            processed_image = self.preprocess_image(image_bytes)
            
            # Create the Vision API image object.
            image = vision.Image(content=processed_image)
            
            # Run document text detection.
            response = self.client.document_text_detection(image=image)
            
            # Check for API errors.
            if response.error.message:
                raise Exception(response.error.message)
            
            # Extract the full text.
            text = response.full_text_annotation.text
            
            # Calculate average confidence.
            confidence = 0.0
            if response.text_annotations:
                confidences = [
                    annotation.confidence 
                    for annotation in response.text_annotations[1:]  # Skip the first full-text annotation.
                    if hasattr(annotation, 'confidence')
                ]
                if confidences:
                    confidence = sum(confidences) / len(confidences)
            
            logger.info(f"OCR succeeded: extracted {len(text)} characters with confidence {confidence:.2f}")
            return text, confidence
            
        except Exception as e:
            logger.error(f"OCR failed: {str(e)}")
            if settings.enable_demo_ai_fallback:
                logger.warning("Using demo OCR fallback after OCR failure")
                return self.demo_extract_text()
            raise Exception(f"OCR processing failed: {str(e)}")
    
    def extract_text_with_structure(self, image_bytes: bytes) -> dict:
        """
        Extract text while preserving structural information such as paragraphs
        and positions for future advanced features.
        """
        if self.client is None:
            if settings.enable_demo_ai_fallback:
                text, confidence = self.demo_extract_text()
                return {"full_text": text, "blocks": [{"text": text, "confidence": confidence}]}
            raise Exception("Google Vision OCR is not configured")

        try:
            processed_image = self.preprocess_image(image_bytes)
            image = vision.Image(content=processed_image)
            response = self.client.document_text_detection(image=image)
            
            if response.error.message:
                raise Exception(response.error.message)
            
            # Extract structured information.
            pages = response.full_text_annotation.pages
            blocks = []
            
            for page in pages:
                for block in page.blocks:
                    block_text = ""
                    for paragraph in block.paragraphs:
                        para_text = ""
                        for word in paragraph.words:
                            word_text = "".join([
                                symbol.text for symbol in word.symbols
                            ])
                            para_text += word_text + " "
                        block_text += para_text.strip() + "\n"
                    
                    blocks.append({
                        "text": block_text.strip(),
                        "confidence": block.confidence
                    })
            
            return {
                "full_text": response.full_text_annotation.text,
                "blocks": blocks
            }
            
        except Exception as e:
            logger.error(f"Structured OCR failed: {str(e)}")
            if settings.enable_demo_ai_fallback:
                text, confidence = self.demo_extract_text()
                return {"full_text": text, "blocks": [{"text": text, "confidence": confidence}]}
            raise Exception(f"Structured OCR processing failed: {str(e)}")

# Create the singleton service instance.
ocr_service = OCRService()
