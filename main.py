import json, os, re
from typing import List, Dict, Any
from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from google.cloud import vision

# ---------- Load rules ----------
with open("rules.json") as f:
    RULES = json.load(f)

app = FastAPI(title="Ingredient Safety API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # for local testing; tighten for prod
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

client = vision.ImageAnnotatorClient()


# ---------- Helpers ----------
def run_ocr(image_bytes: bytes) -> str:
    image = vision.Image(content=image_bytes)
    resp = client.text_detection(image=image)
    if resp.error.message:
        raise RuntimeError(resp.error.message)
    text = (getattr(resp.full_text_annotation, "text", None) or "").strip()
    if not text and resp.text_annotations:
        text = resp.text_annotations[0].description.strip()
    return text or ""


def normalize(text: str) -> str:
    text = text.lower()
    return re.sub(r"\s+", " ", text).strip()


def parse_ingredients(full_text: str) -> List[str]:
    """
    Extract ingredient list:
    - Prefer text after 'ingredients:'
    - Stop before nutrition/allergen blurbs
    - Split & clean
    """
    section = full_text

    # Prefer text after "ingredients:"
    m = re.search(r"\bingredients\s*:\s*(.+)", full_text, flags=re.I)
    if m:
        section = m.group(1)

    # Stop before other sections (nutrition, contains, etc.)
    stop_pattern = re.compile(
        r"\b("
        r"contains|may contain|allergen info|allergy information|"
        r"nutrition facts|nutritional information|daily value|"
        r"directions|storage|manufactured by|distributed by|"
        r"vitamin|calcium|iron|potassium|calories"
        r")\b",
        flags=re.I,
    )
    stop_hit = stop_pattern.search(section)
    if stop_hit:
        section = section[:stop_hit.start()]

    # Split on commas/semicolons
    raw = [s.strip() for s in re.split(r"[;,]", section)]

    items: List[str] = []
    for s in raw:
        # Remove parenthetical/bracketed content
        s = re.sub(r"\([^)]*\)", "", s)
        s = re.sub(r"\[[^\]]*\]", "", s)
        # Keep letters, spaces, hyphens
        s = re.sub(r"[^a-z\s\-]", "", s.lower()).strip()
        # Drop leading "and"/"with"
        s = re.sub(r"^(and|with)\s+", "", s)
        if not s or len(s) < 2:
            continue

        # Skip obviously non-ingredient fragments
        if len(s.split()) > 5 and any(
            kw in s
            for kw in [
                "daily value",
                "nutrition",
                "vitamin",
                "calcium",
                "iron",
                "potassium",
                "calories",
                "mcg",
                "mg",
            ]
        ):
            continue

        items.append(s)

    # Alias + dedupe
    aliases = {
        "hfcs": "high fructose corn syrup",
        "skimmed milk": "milk",
        "milk powder": "milk",
        "dextrose monohydrate": "dextrose",
        "lecithin": "soy lecithin",
    }
    norm = [aliases.get(i, i) for i in items]

    out, seen = [], set()
    for i in norm:
        if i not in seen:
            seen.add(i)
            out.append(i)
            if len(out) >= 100:  # safety cap
                break
    return out


def evaluate(items: List[str], conditions: List[str]) -> Dict[str, Any]:
    hits = []
    score = 100
    weight = {"avoid": 40, "caution": 15}
    label = "Safe"

    seen = set()  # (ingredient, condition, severity)

    for cond in conditions:
        cfg = RULES.get(cond, {})
        for sev in ("avoid", "caution"):
            for kw in cfg.get(sev, []):
                for it in items:
                    if kw in it:
                        key = (it, cond, sev)
                        if key in seen:
                            continue  # already counted this combo
                        seen.add(key)
                        hits.append({
                            "ingredient": it,
                            "condition": cond,
                            "severity": sev,
                            "why": f"Matched '{kw}'"
                        })
                        score -= weight[sev]

    score = max(0, score)
    if any(h["severity"] == "avoid" for h in hits):
        label = "Avoid"
    elif any(h["severity"] == "caution" for h in hits):
        label = "Caution"

    return {"verdict": label, "score": score, "hits": hits}



def default_links(ingredient: str):
    q = ingredient.replace(" ", "%20")
    return [
        {
            "title": "OpenFoodFacts",
            "url": f"https://world.openfoodfacts.org/ingredient/{q}",
        },
        {
            "title": "PubChem",
            "url": f"https://pubchem.ncbi.nlm.nih.gov/#query={q}",
        },
        {
            "title": "MedlinePlus",
            "url": f"https://medlineplus.gov/search/?query={q}",
        },
    ]


def parse_conditions(raw: str) -> List[str]:
    raw = (raw or "").strip()
    if not raw:
        return []
    if raw.startswith("["):
        try:
            arr = json.loads(raw)
            return [str(x).strip() for x in arr if str(x).strip()]
        except Exception:
            pass
    return [c.strip() for c in raw.split(",") if c.strip()]


# ---------- Routes ----------
@app.get("/")
def home():
    return {"ok": True, "message": "Ingredient Safety API. See /docs"}


@app.post("/analyze")
async def analyze(image: UploadFile = File(...), conditions: str = Form("")):
    image_bytes = await image.read()
    raw_text = normalize(run_ocr(image_bytes))

    if not raw_text:
        return {
            "verdict": "Unknown",
            "score": 0,
            "reasons": [],
            "ingredients": [],
            "error": "No text detected. Try a clearer, closer photo of the ingredients.",
            "disclaimer": "Informational only; not medical advice.",
        }

    items = parse_ingredients(raw_text)
    conds = parse_conditions(conditions)
    result = evaluate(items, conds)

    ingredients_out = [
        {"name": it, "links": default_links(it)} for it in items
    ]

    return {
        "verdict": result["verdict"],
        "score": result["score"],
        "reasons": result["hits"],
        "ingredients": ingredients_out,
        "disclaimer": "Informational only; not medical advice.",
    }
