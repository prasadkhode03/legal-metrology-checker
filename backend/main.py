from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import shutil
import os

from ocr_service import extract_text
from field_extractor import extract_fields
from rule_engine import evaluate

app = FastAPI(title="Legal Metrology Compliance Checker")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")

# Fixed demo set: filename -> product id
DEMO_IMAGE_MAP = {
    "lays.jpg": "lays",
    "almonds.jpg": "almonds",
    "lux_soap.jpg": "lux_soap",
    "cura.jpg": "cura",
    "natures_essence.jpg": "natures_essence",
    "dr_sheths.jpg": "dr_sheths",
}


@app.get("/")
def root():
    return {"message": "Legal Metrology Compliance Checker API is alive"}


@app.post("/api/analyze")
async def analyze(file: UploadFile = File(...)):
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Please upload an image file.")

    filename = os.path.basename(file.filename or "unknown.jpg")
    file_path = os.path.join(UPLOAD_DIR, filename)

    # Save the uploaded file
    with open(file_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    # Lookup demo product
    product_id = DEMO_IMAGE_MAP.get(filename)
    if not product_id:
        raise HTTPException(
            status_code=400,
            detail=(
                f"Image '{filename}' not recognized. "
                f"Please use one of the demo images: {', '.join(DEMO_IMAGE_MAP.keys())}"
            ),
        )

    # Get the VERIFIED compliance report
    report = evaluate(product_id)

    # Run live OCR in background for the "AI Attempt" panel
    try:
        ocr_results = extract_text(file_path)
        ai_fields = extract_fields(ocr_results)
        report["ai_extracted_fields"] = ai_fields
    except Exception as e:
        report["ai_extracted_fields"] = {}
        report["ai_error"] = str(e)

    report["image_url"] = f"/uploads/{filename}"
    return report