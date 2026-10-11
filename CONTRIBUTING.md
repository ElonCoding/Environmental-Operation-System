# Contributing to Environmental Operation System (OES)

Thank you for contributing to OES!

## Development Setup
1. Clone repo: `git clone https://github.com/ElonCoding/Environmental-Operation-System.git`
2. Backend:
   ```bash
   pip install -r backend/requirements.txt
   uvicorn backend.app.main:app --reload
   ```
3. Frontend:
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

## Pull Request Guidelines
- Ensure all tests pass: `pytest backend/tests/`
- Ensure frontend builds cleanly: `npm run build`
