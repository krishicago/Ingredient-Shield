# 🛡️ Ingredient Shield  
### OCR-Powered Ingredient Risk Analysis for Allergies & Health Conditions

Ingredient Shield is an AI-powered system that extracts ingredient lists from product images using **Google Cloud Vision OCR**, parses them with a custom ingredient normalization engine, and evaluates risk based on user-selected health conditions (e.g., soy allergy, diabetes).  
The application returns a clear safety verdict, score, risk factors, and research links — all served through a **FastAPI backend** and a **clean web UI**.

---

## 📌 Features

- 🔍 **Google Vision OCR** to extract ingredients from any food label  
- 🧪 **Ingredient Parsing Engine** (regex cleanup, alias mapping, deduplication)  
- ⚠️ **Rule-Based Risk Model** driven by `rules.json`  
- 🛡 **Safety Verdict System:** Safe / Caution / Avoid  
- 📊 **100-Point Score** with severity-based deductions  
- 📝 **Risk Explanation** mapped to each matched ingredient  
- 🔗 **Research Shortcuts** to OpenFoodFacts, PubChem, MedlinePlus  
- 💻 **Modern Two-Column UI** with upload, preview, and results panel  

---

## 🧱 System Architecture

User Upload Image
↓
Frontend (index.html)
↓ POST /analyze
FastAPI Backend
↓
Google Vision OCR → Parsed Ingredients → Rule Engine
↓
Safety Verdict + Score + Summary + Research Links
↓
Frontend Results UI


---

## ⚙️ Setup Instructions

### 1️⃣ Clone the repository
```bash
git clone https://github.com/<your-username>/ingredient-shield.git
cd ingredient-shield

### 2️⃣ Install Dependencies
pip install -r requirements.txt

### 3️⃣ Configure Google Cloud Vision
GOOGLE_APPLICATION_CREDENTIALS="service-account.json"

Load environment variables:
export $(grep -v '^#' .env | xargs)

###4️⃣ Run the backend
uvicorn main:app --reload

###5️⃣ Test API (Swagger UI)
Open:
http://127.0.0.1:8000/docs

###6️⃣ Use the Frontend
Open index.html in your browser.


```


🧪 Sample API Usage

POST /analyze

```
curl -X POST "http://127.0.0.1:8000/analyze" \
  -F "image=@sample.jpg" \
  -F 'conditions=["soy_allergy","diabetes"]'

```
---
## 🔍 API returns:

- verdict
- score
- reasons
- ingredients with research links
- ocr_text
- disclaimer
git clone https://github.com/<your-username>/ingredient-shield.git
cd ingredient-shield
