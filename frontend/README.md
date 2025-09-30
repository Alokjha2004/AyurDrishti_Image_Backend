# AyurDrishti Frontend (React + Vite + Tailwind)

## Run locally
```bash
npm install
# Set backend URL in .env
echo VITE_API_BASE=http://localhost:8000 > .env
npm run dev
```

## Deploy (Vercel)
- Root directory: frontend
- Build command: npm run build
- Output: dist
- Env var: VITE_API_BASE=<your-backend-url>
