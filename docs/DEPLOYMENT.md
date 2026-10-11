# Deployment Architecture Guide

## 1. Frontend (Vercel)
- **Production URL:** `https://frontend-green-eight-6sryntgmnu.vercel.app`
- **Framework:** Vite + React + TypeScript + Tailwind CSS
- **Configuration:** `vercel.json` provides SPA routing rewrites.

## 2. Backend (Render)
- **Production URL:** `https://environmental-operation-system-h41o.onrender.com`
- **Runtime:** Python 3.11
- **Command:** `uvicorn backend.app.main:app --host 0.0.0.0 --port $PORT`
