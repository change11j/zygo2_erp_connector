import os
from PIL import ImageGrab, ImageEnhance
import pytesseract
import cv2
import numpy as np


class RemoteOCR:
    def __init__(self):
        pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
        print(f"Tesseract version: {pytesseract.get_tesseract_version()}")

    def capture_region(self):
        """Capture specified region"""
        try:
            # Capture region (1060,760 to 1165,775)
            screenshot = ImageGrab.grab(bbox=(1060, 760, 1200, 780))
            # Print image size and mode for debugging
            print(f"Screenshot size: {screenshot.size}, mode: {screenshot.mode}")
            return screenshot
        except Exception as e:
            print(f"Screenshot error: {e}")
            return None

    def preprocess_image(self, image):
        """Preprocess image to improve OCR accuracy"""
        try:
            # Convert to OpenCV format
            img_cv = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)

            # Convert to grayscale
            gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)

            # Resize image (make it larger)
            scale_factor = 2
            width = int(gray.shape[1] * scale_factor)
            height = int(gray.shape[0] * scale_factor)
            enlarged = cv2.resize(gray, (width, height), interpolation=cv2.INTER_CUBIC)

            # Enhance contrast
            enhanced = cv2.convertScaleAbs(enlarged, alpha=1.5, beta=0)

            # Apply adaptive thresholding
            binary = cv2.adaptiveThreshold(
                enhanced,
                255,
                cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                cv2.THRESH_BINARY,
                11,
                2
            )

            # Add border
            bordered = cv2.copyMakeBorder(
                binary,
                10, 10, 10, 10,
                cv2.BORDER_CONSTANT,
                value=[255, 255, 255]
            )

            print(f"Processed image size: {bordered.shape}")
            return bordered

        except Exception as e:
            print(f"Image processing error: {e}")
            return None

    def extract_text(self, image):
        """Perform OCR recognition"""
        try:
            # Try different PSM modes
            psm_modes = [6, 7, 8, 13]
            results = []

            for psm in psm_modes:
                custom_config = f'--oem 3 --psm {psm}'
                text = pytesseract.image_to_string(
                    image,
                    config=custom_config,
                    lang='eng'  # explicitly specify English
                )
                if text.strip():
                    results.append(text.strip())
                print(f"PSM {psm} result: '{text.strip()}'")

            return results[0] if results else None

        except Exception as e:
            print(f"OCR error: {e}")
            return None


def main():
    # Create OCR processor
    ocr = RemoteOCR()

    # Capture screenshot
    print("\nCapturing specified region...")
    image = ocr.capture_region()
    if image is None:
        return

    # Save original screenshot for debugging
    image.save("debug_screenshot.png")
    print("Original screenshot saved to debug_screenshot.png")

    # Process image
    print("\nProcessing image...")
    processed_image = ocr.preprocess_image(image)
    if processed_image is None:
        return

    # Save processed image for debugging
    cv2.imwrite("debug_processed.png", processed_image)
    print("Processed image saved to debug_processed.png")

    # Perform OCR
    print("\nPerforming OCR recognition...")
    text = ocr.extract_text(processed_image)

    if text:
        print(f"Recognition result: '{text}'")
    else:
        print("No text recognized")


if __name__ == "__main__":
    main()