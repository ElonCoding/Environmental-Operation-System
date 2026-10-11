# Environmental Operation System (OES) 🌿

### Bhopal Water Quality Intelligence & Ghat Prioritization

Environmental Operation System (OES) is a data-driven decision-support platform concept for
analyzing historical water-quality observations from monitored
idol-immersion ghats in Bhopal. It is designed to help civic teams
explore measurements, compare them with applicable water-quality
criteria, identify locations that may need follow-up, and prepare
evidence-backed action briefs.

> **Important:** Environmental Operation System (OES) is a decision-support prototype, not an
> official pollution classification system, regulatory determination,
> health assessment, or substitute for field inspection. Rankings are
> only as reliable as the underlying observations, metadata, and
> criteria used.

------------------------------------------------------------------------

## Table of contents

-   [The problem](#the-problem)
-   [Our solution](#our-solution)
-   [Key features](#key-features)
-   [How it works](#how-it-works)
-   [Technology stack](#technology-stack)
-   [Architecture](#architecture)
-   [Data sources and integrity](#data-sources-and-integrity)
-   [Getting started](#getting-started)
-   [Environment configuration](#environment-configuration)
-   [API overview](#api-overview)
-   [Testing and quality checks](#testing-and-quality-checks)
-   [Limitations](#limitations)
-   [Roadmap](#roadmap)
-   [Contributing](#contributing)
-   [License](#license)
-   [Acknowledgements](#acknowledgements)

------------------------------------------------------------------------

## The problem

Water-quality information can be difficult to interpret when readings
are spread across multiple dates, locations, parameters, and reports.
Officials need a practical way to understand:

-   Which monitored ghats show the most significant measured concerns?
-   Which observations support that assessment?
-   How do measurements compare with the relevant official criteria?
-   Are results recent and complete enough to support a decision?
-   What follow-up checks or actions should be considered?

A dashboard alone is not enough. Decisions should be explainable,
traceable to source evidence, and transparent about uncertainty.

## Our solution

Environmental Operation System (OES) brings historical readings and reference criteria into one
interactive interface. It is intended to combine deterministic data
analysis with clear visualizations and concise, source-grounded
reporting.

The system aims to provide:

1.  **Explore:** Browse monitored ghats and available observations.
2.  **Compare:** Inspect water-quality parameters and applicable
    criteria.
3.  **Prioritize:** Review a transparent, rule-based ranking of
    locations for further investigation.
4.  **Explain:** See the measurements, assumptions, data gaps, and
    criteria behind each result.
5.  **Report:** Prepare a concise English or Hindi action brief for
    review by a responsible official.

## Key features

The items below describe the intended product scope. Update this section
to match what is actually implemented and tested in your repository.

-   **Executive dashboard:** Summaries of monitored locations, available
    observations, data completeness, and measured criterion exceedances.
-   **Ghat prioritization:** A transparent, configurable ranking based
    on available measurements and applicable criteria.
-   **Interactive map:** Location markers for ghats with verified
    coordinates, with a list-based fallback where coordinates are
    unavailable.
-   **Parameter analysis:** Charts and tables for available parameters
    such as dissolved oxygen, biochemical oxygen demand (BOD), and pH.
-   **Historical comparisons:** Filters for year, ghat, sampling phase,
    festival, and parameter when those fields exist in the source data.
-   **Evidence panel:** Source readings, units, dates, criteria, and
    source-page references where available.
-   **Bilingual action briefs:** English and Hindi summaries grounded in
    verified data, with suggestions clearly separated from official
    orders.
-   **Responsive interface:** A dashboard intended to work on desktop
    and mobile screens.
-   **API-first design:** A frontend connected to a Python backend for
    data processing and risk analysis.

## How it works

``` text
Official datasets and source documents
                |
                v
      Data loading and validation
                |
                v
 Cleaning, normalization, and site matching
                |
                v
  Criteria comparison and risk calculation
                |
                v
       FastAPI backend endpoints
                |
                v
 React dashboard, map, charts, and reports
```

### Prioritization principles

The risk engine should be deterministic and explainable. It should:

-   Compare only compatible parameters, units, intended uses, and
    applicable criteria.
-   Document the source and rationale for each threshold and weight.
-   Show measured exceedances separately from any composite
    prioritization score.
-   Consider data completeness and recency without treating missing
    values as safe.
-   Preserve uncertainty where a location match, measurement, or
    interpretation is unclear.
-   Display the evidence and assumptions behind every ranking.

A composite score is a prioritization aid, not an official CPCB
classification. Do not claim that the score predicts health outcomes or
establishes legal compliance.

## Technology stack

  -----------------------------------------------------------------------
  Layer                   Technology              Purpose
  ----------------------- ----------------------- -----------------------
  Frontend                React, TypeScript, Vite Interactive web
                                                  interface

  Styling                 Tailwind CSS            Responsive design and
                                                  layout

  Mapping                 Leaflet, OpenStreetMap  Geographic exploration
                                                  when verified
                                                  coordinates are
                                                  available

  Charts                  Recharts                Trends and parameter
                                                  comparisons

  Backend                 Python, FastAPI         API and application
                                                  logic

  Data processing         Pandas, NumPy           Validation, cleaning,
                                                  and analysis

  Validation              Pydantic                Typed API inputs and
                                                  outputs

  Testing                 pytest; frontend test   Regression and
                          tooling as configured   integration checks

  Deployment              Any compatible static   Public demo deployment
                          frontend and Python API 
                          host                    
  -----------------------------------------------------------------------

Use the actual versions and packages declared in `package.json` and the
backend dependency file as the source of truth.

## Architecture

A recommended repository layout is:

``` text
Environmental-Operation-System/
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── services/
│   │   └── types/
│   ├── package.json
│   └── .env.example
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── api/
│   │   ├── services/
│   │   ├── schemas/
│   │   └── data/
│   ├── tests/
│   └── requirements.txt
├── docs/
├── .gitignore
├── LICENSE
└── README.md
```

This is a suggested structure. Keep the existing structure if Claude has
already generated the project, and adjust these paths to match the
actual repository.

## Data sources and integrity

The project is intended to use the datasets and source documents
supplied with the official Visarjan Ghat Watch challenge.

**Challenge repository:**\
https://github.com/Vishal4742/bhopal-impact-lab-2026-problem-statements

**Track 2 --- Visarjan Ghat Watch:**\
https://github.com/Vishal4742/bhopal-impact-lab-2026-problem-statements/tree/main/track-2-visarjan-ghat-watch

If included in the challenge files, the expected data may include:

-   `bhopal_ghats_2023_2025.csv` --- historical ghat water-quality
    observations.
-   `cpcb_water_quality_criteria.csv` --- reference water-quality
    criteria.

Confirm the exact filenames, column definitions, provenance, and usage
terms from the downloaded challenge files before relying on them. Cite
the original source documents in the application and final submission.

### Data-handling rules

-   Preserve original observations and source references.
-   Treat blank or unavailable values as missing, not zero.
-   Preserve and correctly interpret `BDL` (below detection limit) and
    `ND` (not detected) according to source documentation.
-   Do not silently merge uncertain site names.
-   Retain dates, units, sampling phase, and other relevant metadata.
-   Compare a value with a criterion only when the parameter, unit,
    intended use, and comparison direction are appropriate.
-   Clearly identify stale, incomplete, or ambiguous data.
-   Never fabricate readings, coordinates, citations, or results to make
    a dashboard appear complete.

## Getting started

### Prerequisites

Install:

-   Git
-   Node.js and npm (use a version compatible with the frontend
    dependencies)
-   Python 3.10 or newer, subject to the project's dependency
    requirements

### 1. Clone the repository

``` bash
git clone https://github.com/<YOUR-USERNAME>/<YOUR-REPOSITORY>.git
cd <YOUR-REPOSITORY>
```

Replace the placeholder URL and folder name with your actual GitHub
repository.

### 2. Configure the backend

Open a terminal in the backend directory:

``` bash
cd backend
python -m venv .venv
```

Activate the environment.

**Windows PowerShell:**

``` powershell
.venv\Scripts\Activate.ps1
```

**Windows Command Prompt:**

``` bat
.venv\Scripts\activate.bat
```

**macOS/Linux:**

``` bash
source .venv/bin/activate
```

Install dependencies:

``` bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

If the project does not yet contain `requirements.txt`, create it from
the packages actually used by the backend. Do not install arbitrary
packages without checking the implementation.

Start the API using the entry point in your project. For the suggested
layout:

``` bash
uvicorn app.main:app --reload --port 8000
```

The API should be available at:

-   API base: `http://localhost:8000`
-   Interactive API docs: `http://localhost:8000/docs`
-   Health check: `http://localhost:8000/api/health`

These URLs depend on the routes and entry point actually implemented.

### 3. Configure the frontend

Open a second terminal:

``` bash
cd frontend
npm install
```

Create a local environment file from `.env.example` if the project
provides one. For a Vite frontend, a typical local setting is:

``` env
VITE_API_BASE_URL=http://localhost:8000
```

Start the frontend:

``` bash
npm run dev
```

Open the local URL printed by Vite, commonly `http://localhost:5173`.

### 4. Verify the full workflow

Before presenting the project, check that:

1.  The dashboard loads without console errors.
2.  The frontend can reach the backend.
3.  The data files are found and parsed correctly.
4.  Filters change the results and charts.
5.  A ghat detail view shows the correct observations and units.
6.  Every ranking can be explained using its supporting evidence.
7.  Missing and below-detection-limit values are handled transparently.
8.  The report reflects the selected ghat and date range.
9.  The interface displays useful error and empty states when data or
    the API is unavailable.

## Environment configuration

Do not commit `.env` files containing secrets. Keep `.env.example`
limited to placeholder values.

  Variable              Purpose                Example
  --------------------- ---------------------- -------------------------
  `VITE_API_BASE_URL`   Backend API base URL   `http://localhost:8000`

Add other variables only when the implementation needs them. If an LLM
provider is used to generate narrative summaries, keep its secret key in
the backend environment; never expose it through a `VITE_` variable or
ship it to the browser. The app's core risk calculation should work
without a paid LLM service.

## API overview

The following endpoints are recommended for the application. Document
only the endpoints that exist in the running backend.

  ------------------------------------------------------------------------
  Method                  Endpoint                 Purpose
  ----------------------- ------------------------ -----------------------
  `GET`                   `/api/health`            Check API availability

  `GET`                   `/api/summary`           Retrieve dashboard
                                                   summary metrics

  `GET`                   `/api/ghats`             List monitored ghats

  `GET`                   `/api/ghats/{ghat_id}`   Retrieve one ghat's
                                                   details

  `GET`                   `/api/readings`          Query observations
                                                   using supported filters

  `GET`                   `/api/risk-ranking`      Retrieve explainable
                                                   prioritization results

  `POST`                  `/api/action-brief`      Generate an
                                                   evidence-backed action
                                                   brief
  ------------------------------------------------------------------------

Example health check:

``` bash
curl http://localhost:8000/api/health
```

For exact query parameters, request fields, response schemas, and
example payloads, use the backend's interactive documentation at
`/docs`.

## Testing and quality checks

Run the tests configured in your repository. Example commands for a
typical Python backend and npm frontend are:

``` bash
# From backend/
pytest
```

``` bash
# From frontend/
npm run build
```

Also verify that:

-   Criteria boundary conditions are tested.
-   Units and comparison directions are correct.
-   Missing data does not receive an unjustified low-risk score.
-   Duplicate records and uncertain site matches are surfaced.
-   API validation errors return useful responses.
-   The frontend handles backend downtime gracefully.
-   No API keys, private information, or large generated files are
    committed.

Only report tests as passing after running them successfully.

## Limitations

-   Historical observations do not necessarily describe current
    conditions.
-   Sampling frequency, location coverage, and data completeness may
    vary.
-   A result for one sampling point should not automatically be
    generalized to an entire water body.
-   A criterion comparison is meaningful only when its designated use,
    units, sampling method, and comparison rules are appropriate.
-   A composite prioritization score simplifies complex environmental
    conditions and must be interpreted alongside the original
    measurements.
-   AI-generated summaries can be wrong; any narrative output must be
    grounded in retrieved records and reviewed before official use.
-   The platform does not replace new sampling, laboratory verification,
    field inspections, or decisions by authorized officials.

## Roadmap

-   [ ] Verify all dataset schemas and source citations.
-   [ ] Implement and test the deterministic risk engine.
-   [ ] Add interactive ghat ranking and parameter filters.
-   [ ] Add verified map coordinates with a list fallback.
-   [ ] Add historical trend analysis.
-   [ ] Add evidence-linked Hindi and English action briefs.
-   [ ] Add downloadable and print-friendly reports.
-   [ ] Add automated backend and frontend tests.
-   [ ] Deploy the frontend and backend.
-   [ ] Record a demo showing a complete officer workflow.

Mark an item complete only when the feature is implemented and verified.

## Contributing

Contributions that improve data quality, accessibility, reproducibility,
scientific transparency, or usability are welcome.

1.  Fork the repository.
2.  Create a feature branch.
3.  Make a focused change.
4.  Run the relevant tests and build checks.
5.  Open a pull request with a description of the change and its
    validation.

Do not submit fabricated environmental data or unsupported claims.

## License

This project is intended to use the MIT License. Add a `LICENSE` file
containing the full MIT license text and the appropriate copyright
holder before describing the repository as MIT-licensed. Confirm that
third-party datasets and documents permit the intended reuse; a software
license does not automatically relicense those materials.

## Acknowledgements

-   Organizers and contributors to the Bhopal Impact Lab 2026 challenge.
-   Central Pollution Control Board (CPCB) for applicable water-quality
    reference materials, where included in the challenge sources.
-   The original publishers of all datasets and reports used by the
    project.
-   Open-source maintainers of React, Vite, FastAPI, Pandas, NumPy,
    Leaflet, Recharts, and related dependencies.

------------------------------------------------------------------------

**Environmental Operation System (OES) --- Turning water-quality data into transparent,
evidence-backed priorities.**
