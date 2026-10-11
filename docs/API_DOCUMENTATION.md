# Environmental Operation System (OES) — API Documentation

## Base URL
- **Production (Render):** `https://environmental-operation-system-h41o.onrender.com`
- **Prefix:** `/api/v1`

## Key Endpoints

### 1. Health & Readiness
`GET /api/v1/health`
Returns system operational state, loaded dataset records, and validation summary.

### 2. Ghats Ranking & Risk
`GET /api/v1/ghats/ranking`
Evaluates all 7 canonical Bhopal idol immersion ghats against CPCB Class B thresholds.

### 3. Dashboard Summary
`GET /api/v1/dashboard/summary`
Aggregates overall lake water quality statistics, critical violations, and priority alerts.

### 4. Executive Briefing
`POST /api/v1/reports/brief`
Generates bilingual (English/Hindi) structured operational action reports.
