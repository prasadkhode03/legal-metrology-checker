import easyocr
import cv2
import numpy as np
import os

# Load the OCR model once when the module is imported.
# 'en' = English. gpu=False means use CPU (safer, works on all laptops).
print("Loading EasyOCR model... (this happens once, ~10 seconds)")
reader = easyocr.Reader(['en'], gpu=False)
print("EasyOCR model loaded.")


def preprocess_image(image_path: str) -> str:
    """
    Improve image quality for better OCR.
    Returns path to the preprocessed image.
    """
    img = cv2.imread(image_path)
    if img is None:
        raise ValueError(f"Could not read image: {image_path}")

    # Resize small images so text is big enough for OCR
    h, w = img.shape[:2]
    if w < 1000:
        scale = 1000 / w
        img = cv2.resize(img, (int(w * scale), int(h * scale)), interpolation=cv2.INTER_CUBIC)

    # Convert to grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Denoise while keeping edges sharp
    gray = cv2.bilateralFilter(gray, 9, 75, 75)

    # Save preprocessed version next to the original
    base, ext = os.path.splitext(image_path)
    preprocessed_path = f"{base}_preprocessed{ext}"
    cv2.imwrite(preprocessed_path, gray)

    return preprocessed_path


def extract_text(image_path: str):
    """
    Run OCR on the image.
    Returns a list of dicts: {text, bbox, confidence}
    bbox = [[x1,y1],[x2,y2],[x3,y3],[x4,y4]] (4 corners of the text box)
    """
    preprocessed_path = preprocess_image(image_path)

    results = reader.readtext(preprocessed_path)

    output = []
    for bbox, text, conf in results:
        output.append({
            "text": text,
            "bbox": [[int(x), int(y)] for x, y in bbox],
            "confidence": round(float(conf), 3),
        })

    return output