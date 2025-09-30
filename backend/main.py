import io, os, json, time
from typing import Optional, Dict, Any
from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
from PIL import Image
import requests

load_dotenv()

app = FastAPI(title="AyurDrishti Backend (PlantNet + JSON DB)", version="2.0.1")

# CORS - allow all for dev (tighten in production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Config from .env
PLANTNET_API_KEY = os.getenv("PLANTNET_API_KEY", "").strip()
PLANTNET_PROJECT = os.getenv("PLANTNET_PROJECT", "all").strip() or "all"
MOCK_MODE = os.getenv("MOCK_MODE", "false").lower() == "true"

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
os.makedirs(DATA_DIR, exist_ok=True)
PLANTS_JSON_PATH = os.path.join(DATA_DIR, "plants.json")

if not os.path.exists(PLANTS_JSON_PATH):
    with open(PLANTS_JSON_PATH, "w", encoding="utf-8") as f:
        json.dump({}, f, ensure_ascii=False, indent=2)

DISCLAIMER = "Informational Ayurveda-style tips only. Not medical advice."

# Helpers
def _read_db() -> Dict[str, Any]:
    with open(PLANTS_JSON_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def _write_db(db: Dict[str, Any]):
    with open(PLANTS_JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(db, f, ensure_ascii=False, indent=2)

def _normalize_scientific(name: Optional[str]) -> Optional[str]:
    if not name:
        return None
    return name.strip().lower()

def plantnet_identify(image_bytes: bytes, organ: str = "leaf") -> Dict[str, Any]:
    """
    Call PlantNet API v2 identify endpoint.
    If MOCK_MODE or no API key, returns a demo response for testing.
    """
    if MOCK_MODE or not PLANTNET_API_KEY:
        # Mock data for local testing
        return {
            "status": "mock",
            "results": [{
                "score": 0.91,
                "species": {
                    "scientificNameWithoutAuthor": "ocimum tenuiflorum",
                    "scientificNameAuthorship": "",
                    "genus": {"scientificNameWithoutAuthor": "Ocimum"},
                    "family": {"scientificNameWithoutAuthor": "Lamiaceae"},
                    "commonNames": ["Tulsi", "Holy Basil"]
                }
            }]
        }

    endpoint = f"https://my-api.plantnet.org/v2/identify/{PLANTNET_PROJECT}"
    params = {"api-key": PLANTNET_API_KEY}
    files = [("images", ("upload.jpg", image_bytes, "image/jpeg"))]
    # ✅ FIXED: removed include-related-images
    data = {"organs": organ}

    resp = requests.post(endpoint, params=params, files=files, data=data, timeout=30)
    if resp.status_code != 200:
        raise RuntimeError(f"PlantNet API error {resp.status_code}: {resp.text[:200]}")
    return resp.json()

def enrich_with_local_db(scientific: str) -> Dict[str, Any]:
    db = _read_db()
    key = _normalize_scientific(scientific)
    info = db.get(key, {})
    base = {
        "common_name": info.get("common_name", ""),
        "medicinal_uses": info.get("uses", []),
        "contraindications": info.get("contra", []),
        "notes": info.get("notes", ""),
        "source": info.get("source", "local-db"),
    }
    return base

def upsert_db_entry(scientific: str, payload: Dict[str, Any]):
    db = _read_db()
    key = _normalize_scientific(scientific)
    entry = db.get(key, {})
    entry.update(payload)
    entry.setdefault("updated_at", int(time.time()))
    db[key] = entry
    _write_db(db)

# Routes
@app.get("/")
def root():
    return {"ok": True, "service": "AyurDrishti Backend v2", "mock": MOCK_MODE}

@app.post("/api/identify")
async def identify(file: UploadFile = File(...), organ: str = Form("leaf")):
    # validate image
    try:
        raw = await file.read()
        _ = Image.open(io.BytesIO(raw)).convert("RGB")
    except Exception:
        return JSONResponse({"error": "Invalid image"}, status_code=400)

    # call PlantNet (or mock)
    try:
        result = plantnet_identify(raw, organ=organ)
    except Exception as e:
        return JSONResponse({"error": f"Identify failed: {e}"}, status_code=500)

    # parse best candidate
    results = result.get("results", [])
    if not results:
        return {"predictions": [], "message": "No match found"}

    top = results[0]
    score = float(top.get("score", 0.0))
    species = top.get("species", {}) or {}
    sci = species.get("scientificNameWithoutAuthor") or species.get("scientificName") or ""
    family = (species.get("family") or {}).get("scientificNameWithoutAuthor", "")
    genus = (species.get("genus") or {}).get("scientificNameWithoutAuthor", "")
    common_names = species.get("commonNames", []) or []

    # enrich from local DB
    enrich = enrich_with_local_db(sci)

    # upsert skeleton entry so DB grows
    upsert_db_entry(sci, {
        "common_name": enrich.get("common_name") or (common_names[0] if common_names else ""),
        "uses": enrich.get("medicinal_uses", []),
        "contra": enrich.get("contraindications", []),
        "family": family,
        "genus": genus,
        "source": enrich.get("source") or "plantnet+local",
    })

    response = {
        "scientific_name": sci,
        "common_names": common_names,
        "family": family,
        "genus": genus,
        "confidence": round(score, 4),
        "enriched": enrich,
        "raw_provider": "plantnet" if not MOCK_MODE else "mock",
    }
    return response

# Simple Ayurveda chat (rule-based)
TIPS = {
    "cold": "Garam pani me haldi ya tulsi wali chai, din me 2-3 bar. Rest karein. Thandi cheezon se parhez.",
    "cough": "Honey + ginger warm water (1 tsp madh + adrak), din me 2 bar. Steam lein.",
    "digestion": "Jeera-ajwain warm water, halka khana, zyada tel-masala se parhez.",
    "daily": "Subah garam pani, 10-15 min walk/yoga, 2-3L paani, early dinner."
}

def detect_lang(text: str) -> str:
    hindi_chars = sum('\u0900' <= ch <= '\u097F' for ch in text)
    if hindi_chars > 0:
        return "hi"
    if any(w in text.lower() for w in ["hoga", "kya", "nahi", "thik", "sardi", "khansi"]):
        return "hinglish"
    return "en"

@app.post("/api/ayurveda-chat")
async def ayurveda_chat(message: str = Form(...)):
    t = (message or "").strip().lower()
    if any(k in t for k in ["cold", "sardi", "flu", "nose"]):
        tip = TIPS["cold"]
    elif any(k in t for k in ["cough", "khansi"]):
        tip = TIPS["cough"]
    elif any(k in t for k in ["gas", "acidity", "digestion"]):
        tip = TIPS["digestion"]
    elif any(k in t for k in ["daily", "wellness", "healthy", "fitness"]):
        tip = TIPS["daily"]
    else:
        tip = "General tip: subah garam pani, halka nashta, halki walk. Zyada specific sawal poochiye."
    return {"answer": tip, "lang": detect_lang(message), "disclaimer": DISCLAIMER}
