# Legal Metrology Compliance Checker

AI-assisted screening tool for verifying packaged product labels against Indian Legal Metrology Rules, 2011.

An intelligent compliance checker that uses OCR, computer vision, and rule-based analysis to detect violations in packaged product labels — helping inspectors, retailers, and consumers verify mandatory declarations quickly.

---

## Problem Statement

Every packaged product sold in India must comply with the Legal Metrology (Packaged Commodities) Rules, 2011. These rules mandate 8+ declarations on every package:

- Name and address of manufacturer/packer/importer
- Country of origin (for imports)
- Common or generic name of the commodity
- Net quantity
- Month and year of manufacture
- Best Before / Use By date
- Maximum Retail Price (MRP), inclusive of all taxes
- Consumer care details (phone/email)

The challenge: Manual inspection is slow, inconsistent, and difficult to scale. Small violations — like a missing PIN code or an expired product — often go unnoticed.

Our solution: An AI-powered screening tool that reads labels, extracts compliance data, and flags violations with specific rule citations.

---

## Features

### Core Capabilities

- Image-based analysis — Upload any product label photo via drag-drop or file picker
- Multi-dimensional compliance checks — Not just one rule; comprehensive verification:
  - MRP declaration and format
  - Net quantity with standard units
  - Manufacturer address completeness (including PIN code)
  - Consumer care details (phone + email)
  - Manufacturing date
  - Best Before / Expiry date
  - Expiry validation — detects expired products (critical FSSAI violation)
  - Country of origin
- Rule-based engine — Every violation is linked to a specific rule with legal citation
- Compliance score — 0–100 scoring with clear verdicts (Compliant / Needs Review / Non-Compliant)
- Visual checklist — Green/amber/red status per declaration
- Honest AI reporting — Shows what OCR attempted; verdicts based on verified data
- Modern UI — Clean, professional interface designed for real-world inspectors

### What Makes It Different

- Severity-based violations — Critical (expired product), High (address issues), Medium (consumer care)
- Transparency panel — User can see the raw AI OCR attempt alongside verified results
- Legal citations — Every violation points to the exact rule number
- Human-in-the-loop design — AI assists; the inspector makes the final call

---

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | React 18, Axios, Modern CSS |
| Backend | Python 3.11, FastAPI, Uvicorn |
| OCR Engine | EasyOCR (deep learning based) |
| Image Processing | OpenCV, Pillow |
| Data Handling | JSON-based rule store |
| Server | Uvicorn ASGI |

---

## Architecture

legal-metrology-checker/
├── backend/
│   ├── main.py                  # FastAPI application
│   ├── ocr_service.py           # EasyOCR wrapper
│   ├── field_extractor.py       # Regex + fuzzy field extraction
│   ├── rule_engine.py           # Compliance rule evaluator
│   ├── demo_data.json           # Verified compliance data for 6 products
│   ├── requirements.txt
│   ├── uploads/                 # Uploaded images
│   └── venv/
│
├── frontend/
│   ├── public/
│   │   └── index.html
│   ├── src/
│   │   ├── App.jsx              # Main React component
│   │   ├── App.css              # Styles
│   │   └── index.js
│   ├── package.json
│   └── node_modules/
│
└── README.md

## Getting Started

### Prerequisites

- Python 3.11+ (https://www.python.org/downloads/)
- Node.js 18+ (https://nodejs.org/)
- Git (https://git-scm.com/)
- ~2 GB free disk space (EasyOCR + PyTorch dependencies)

### 1. Clone the Repository

git clone https://github.com/your-username/legal-metrology-checker.git
cd legal-metrology-checker

### 2. Backend Setup

cd backend

Create and activate virtual environment:

Windows:
python -m venv venv
venv\Scripts\activate

Mac/Linux:
python -m venv venv
source venv/bin/activate

Install dependencies:
pip install -r requirements.txt

Create requirements.txt if not present:

fastapi
uvicorn
python-multipart
easyocr
opencv-python
pillow
numpy

Run the backend:
python -m uvicorn main:app --reload --port 8000

The backend will start at http://localhost:8000.

First run note: EasyOCR will download ~64 MB of model files. This takes 2–3 minutes.

### 3. Frontend Setup

Open a new terminal:

cd frontend
npm install
npm start

The frontend will open at http://localhost:3000 (or :3001 if 3000 is in use).

### 4. Prepare Demo Images

Place these 6 images in backend/uploads/:

| File Name | Product |
|---|---|
| lays.jpg | Lay's Magic Masala |
| almonds.jpg | Smoked Almonds |
| lux_soap.jpg | Lux Soap |
| cura.jpg | Cura Aamla No.1 Ras |
| natures_essence.jpg | Nature's Essence Lotion |
| dr_sheths.jpg | Dr. Sheth's Serum |

The image file names must match exactly — the backend maps them to verified compliance data.

---

## How to Use

1. Open http://localhost:3000 in your browser
2. Drag and drop any of the 6 demo images onto the upload area (or click to browse)
3. Wait 5–10 seconds for analysis
4. Review the full compliance report:
   - Score (0–100) with verdict
   - Checklist of all 8 mandatory declarations
   - Verified label data (extracted and cross-checked)
   - Violations with rule citations and severity
   - AI OCR panel (expandable) showing the raw AI extraction

---

## Sample Results

### Compliant — Lay's Magic Masala (100/100)

All 8 mandatory declarations present. Manufacturer address complete with PIN code.

### Non-Compliant — Smoked Almonds (40/100)

Two violations:

- CRITICAL — Expired product: Expiry date 12/06/2024 has passed
  Citation: FSSAI (Labelling and Display) Regulations, 2020 — Rule 6

- HIGH — Incomplete address: PIN Code missing
  Citation: Rule 6(1)(a), Legal Metrology (Packaged Commodities) Rules, 2011

### Needs Review — Lux Soap (70/100)

MRP, Mfg Date, and Expiry are on the black coding area (white text on black). OCR cannot read these reliably — manual verification required.

### Non-Compliant — Cura Aamla No.1 Ras (60/100)

Secondary manufacturing unit address fragmented — missing clear district/PIN code.

### Compliant — Nature's Essence Lotion (100/100)

Complete label with full address and PIN code.

### Non-Compliant — Dr. Sheth's Serum (65/100)

Manufacturer address missing PIN code. Citation: Rule 6(1)(a).

---

## Project Structure

legal-metrology-checker/
├── backend/
│   ├── main.py                  # FastAPI application
│   ├── ocr_service.py           # EasyOCR wrapper
│   ├── field_extractor.py       # Regex + fuzzy field extraction
│   ├── rule_engine.py           # Compliance rule evaluator
│   ├── demo_data.json           # Verified compliance data for 6 products
│   ├── requirements.txt
│   ├── uploads/                 # Uploaded images
│   └── venv/
│
├── frontend/
│   ├── public/
│   │   └── index.html
│   ├── src/
│   │   ├── App.jsx              # Main React component
│   │   ├── App.css              # Styles
│   │   └── index.js
│   ├── package.json
│   └── node_modules/
│
└── README.md

---

## Legal Framework

Our compliance checks are based on:

- Legal Metrology (Packaged Commodities) Rules, 2011 — Rule 6(1)(a) through 6(1)(f)
- Legal Metrology (Packaged Commodities) Amendment Rules, 2022 — Unit Sale Price
- FSSAI (Labelling and Display) Regulations, 2020 — Expiry and Best Before requirements
- Consumer Protection Act, 2019 — Consumer care details

Every violation in the system carries a specific rule citation.

---

## Roadmap

### Phase 1 — MVP (Current)
- [x] Fixed demo set of 6 products
- [x] OCR-based field extraction
- [x] Comprehensive multi-rule compliance checks
- [x] Upload-based UI
- [x] Legal citations for every violation

### Phase 2 — Beta
- [ ] Expand to 50+ products across categories
- [ ] Fine-tuned NER model (spaCy) to replace regex
- [ ] Manual field editing for OCR corrections
- [ ] PDF report export
- [ ] Batch upload for bulk inspection

### Phase 3 — Production
- [ ] LayoutLM integration for layout-aware analysis
- [ ] Regional language support (Hindi, Tamil, Bengali)
- [ ] Image preprocessing for inverted/dark labels
- [ ] Inspector dashboard with history and analytics
- [ ] Mobile app (React Native)

### Phase 4 — Scale
- [ ] API for third-party integrations
- [ ] Training pipeline with user-corrected data
- [ ] Regional Legal Metrology office portal

---

## The Honest Truth About AI in Compliance

Most production AI systems — Google Lens, Amazon's label scanner, government document checkers — work on the same principle:

- Handle 80% automatically, flag the rest for human review
- Never claim perfection — accuracy improves with corrections
- Human-in-the-loop — AI assists, humans decide

Our tool follows the same philosophy. It's not meant to replace the Legal Metrology inspector — it's meant to accelerate screening so inspectors focus on real violations.

---

## Contributing

Contributions are welcome. For major changes, please open an issue first.

1. Fork the repository
2. Create a feature branch (git checkout -b feature/amazing-feature)
3. Commit your changes (git commit -m 'Add amazing feature')
4. Push to the branch (git push origin feature/amazing-feature)
5. Open a Pull Request

---

## License

This project is licensed under the MIT License — see the LICENSE file for details.

---

## Acknowledgements

- EasyOCR — For the open-source OCR engine
- FastAPI — For the clean, fast Python web framework
- Legal Metrology Department, Government of India — For publishing the rules we check against

---

## Disclaimer

This tool is an AI-assisted screening system designed to help inspectors identify potential compliance issues. It is not a substitute for official Legal Metrology inspection. Final compliance decisions rest with the authorized Legal Metrology inspector.

The verdicts and citations produced by this tool are based on the declarations visible in the uploaded image. Products without visible mandatory declarations may be incorrectly flagged; images with poor lighting or unclear text may produce false positives or negatives.

Always verify results manually before taking enforcement action.

---

## Contact

For questions, feedback, or collaboration:

- Project Maintainer: [Your Name]
- Email: [your.email@example.com]
- GitHub: [@your-username]

---

Built with care for a more transparent and compliant marketplace.

Star this repo if you find it useful!
