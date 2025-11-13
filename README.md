🛡️ Ingredient Shield
OCR-Driven Ingredient Parsing & Health-Condition Risk Assessment System

Ingredient Shield is a FastAPI-based backend that uses Google Cloud Vision OCR to extract ingredients from product label images, then evaluates them against user-selected health conditions using a rule-based risk engine. It returns structured safety analysis including a verdict, score, risk factors, and research shortcuts.

🔍 Features
Image OCR using Google Cloud Vision
Ingredient Parsing Engine (regex cleanup, normalization, alias mapping)
Configurable Rule Engine for allergies & conditions
Safety Score + Risk Verdict
Research Metadata with OpenFoodFacts, PubChem, and MedlinePlus links
Modern Web UI (two-column layout, upload + results panel)


API-driven architecture ready for deployment

🧱 System Architecture
User Upload → Frontend → FastAPI → Google Vision OCR
                         ↓
                Ingredient Parser
                         ↓
                   Rule Evaluator
                         ↓
              JSON Safety Assessment

🗂️ Tech Stack

Backend: FastAPI (Python)
OCR: Google Cloud Vision API
Frontend: HTML, CSS, JS
Rules Engine: JSON-based severity definitions
Environment: .env with GCP credentials



⚙️ Setup Instructions
1️⃣ Clone the repository
git clone https://github.com/<your-username>/ingredient-shield.git
cd ingredient-shield

2️⃣ Install dependencies
pip install -r requirements.txt

3️⃣ Configure Google Vision credentials

Create a file .env:
GOOGLE_APPLICATION_CREDENTIALS="service-account.json"


Load environment variables:
export $(grep -v '^#' .env | xargs)

4️⃣ Run the FastAPI server
uvicorn main:app --reload

5️⃣ Open API docs
http://127.0.0.1:8000/docs


This page allows you to upload images and test requests directly.
🧪 Example API Call
curl -X POST "http://127.0.0.1:8000/analyze" \
  -F "image=@sample.jpg" \
  -F 'conditions=["soy_allergy","diabetes"]'

🛡️ How Risk Evaluation Works
OCR text is normalized
Ingredient parser extracts a clean list

For each health condition:
avoid keywords subtract 40 points
caution keywords subtract 15 points

Verdict logic:
Any avoid → Avoid
Any caution → Caution
None → Safe

Returns structured output with:
verdict
score
reasons
ingredients
ocr_text

🚀 Roadmap

LLM-based ingredient classification

Nutrition facts OCR parsing

Ingredient database enrichment

User accounts + saved scans

Mobile-friendly UI

Docker deployment
