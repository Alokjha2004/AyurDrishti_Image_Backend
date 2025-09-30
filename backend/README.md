# AyurDrishti Backend (FastAPI)

## Run locally
```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

## Endpoints
- `POST /api/identify` (form-data: file=<image>)
- `POST /api/ayurveda-chat` (form-data: message=<text>)
- `GET /`

## Deploy (Railway/Render)
Use the provided Dockerfile. Set port 8000.

cd .\backend\
python -m venv .venv

venv\Scripts\activate  
upper wla error de toh niche wla

.\.venv\Scripts\Activate.ps1

pip install -r requirements.txt

uvicorn main:app --reload
