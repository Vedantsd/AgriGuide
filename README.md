# AgriGuide

AgriGuide recommends the best crop to grow from your field's conditions. Enter pH, moisture,
temperature, rainfall and soil details by hand, or upload a soil test report PDF and let it
fill the form for you. A Statistics page runs regression, t-tests and F-tests on the crop
dataset.

**Stack:** HTML/CSS/JavaScript frontend, Flask backend, Neon Postgres database, pypdf for
report parsing, statsmodels and scipy for statistics.

## Features

- **Crop prediction.** Each crop's ideal ranges (pH, moisture, temperature, rainfall, N/P/K)
  are scored against your input. A value inside a crop's range scores 1.0 and the score falls
  off the further outside it is. Soil type and climate zone add match or mismatch weight.
  Crops are ranked by a weighted match percentage, and you get the top pick plus three
  alternatives.
- **Soil report upload.** `pypdf` reads a text-based PDF and extracts pH, moisture,
  temperature, rainfall, soil texture, climate zone, nitrogen, phosphorus and potassium.
  The form is auto-filled and fields that weren't found are listed.
- **Statistics page (`/stats`).**
  - Multiple linear regression of N, P or K on average pH, moisture, temperature and rainfall,
    with R², adjusted R², the overall F-test and a t-test for each coefficient.
  - Welch's two-sample t-test between two groups, plus a variance-ratio F-test.
  - One-way ANOVA (F-test) across all groups of a category (climate zone or soil type).

## Prerequisites

- Python 3.10 or newer (developed and tested on 3.12)
- A free [Neon](https://neon.tech) account with a Postgres project
- `psql` (optional, you can paste `schema.sql` into the Neon SQL Editor instead)

## Setup

**1. Get your Neon connection string.** In the Neon console, open your project, then
Connection Details, and copy the connection string.

**2. Configure the environment.**

```bash
cp .env.example .env
```

Open `.env` and set `DATABASE_URL` to your connection string.

**3. Install dependencies.**

```bash
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

**4. Create the table and load the data.**

```bash
psql "$DATABASE_URL" -f schema.sql
python seed_data.py
```

`schema.sql` drops and recreates the `crops` table, so run it again before re-seeding to
avoid duplicate rows. `seed_data.py` cleans `crops.csv` (trims text, converts numbers, fixes
swapped min/max values, removes invalid rows and duplicates, fills missing N/P/K with the
column average) and inserts 42 crops.

**5. Run the app.**

```bash
python app.py
```

Open http://127.0.0.1:5000.

## Try it with the sample report

1. On the Predict page, choose `samples/sample_soil_test_report.pdf`.
2. Click **Auto-fill**. All nine fields are filled in.
3. Click **Predict best crop**. The top result is Coconut.

The sample report contains fictional data and is for demonstration only.

## How soil report parsing works

- Only text-based PDFs work. Scanned or image-only PDFs have no extractable text and need
  OCR, which is not included. The app shows an error in that case.
- Values are found by label (pH, Moisture, Temperature, Rainfall, Nitrogen, Phosphorus,
  Potassium, Soil Texture or Soil Type, Climate Zone). The first number after a label is
  used, and bracketed text such as `(1:2.5 soil:water)` or `(P2O5)` is ignored.
- Values outside plausible ranges (for example pH above 14) are discarded.
- Temperature, rainfall and climate zone are not part of a standard soil analysis, so they
  are only filled if the report includes a site information section.
- N, P and K are assumed to be in kg/ha, matching the dataset. Convert ppm values first.
- Lab layouts vary. If a report parses poorly, adjust `FIELD_LABELS` in `soil_report.py`.
- Uploads are limited to 5 MB and must have a `.pdf` extension.

## Statistics notes

- The dataset has 42 rows and the regression uses 4 predictors, so treat the results as
  exploratory. A significant overall F-test does not mean the model predicts well on new data.
- Groups with fewer than 2 observations (for example the single Arid crop) are skipped in
  the t-test and ANOVA, and the result says so.
- Significance is judged at α = 0.05.

## Project structure

```
agriguide/
├── app.py                  Flask routes
├── db.py                   Neon Postgres connection helper
├── recommender.py          Crop scoring logic
├── soil_report.py          pypdf soil report parser
├── stats_analysis.py       Regression, t-test and F-tests
├── seed_data.py            Cleans crops.csv and loads it into Postgres
├── schema.sql              Table definition
├── crops.csv               Dataset (42 crops)
├── requirements.txt
├── .env.example
├── samples/
│   └── sample_soil_test_report.pdf
├── templates/
│   ├── base.html           Header, logo, navigation
│   ├── index.html          Predict page and PDF upload
│   └── stats.html          Statistics page
└── static/
    ├── style.css
    ├── script.js           Predict page logic
    ├── stats.js            Statistics page logic
    └── src/logo.png
```

## API reference

| Endpoint | Method | Purpose |
|---|---|---|
| `/api/options` | GET | Soil types and climate zones for the dropdowns |
| `/api/predict` | POST | JSON conditions in, top match and 3 alternatives out |
| `/api/upload-report` | POST | Multipart field `report` (PDF), returns extracted values |
| `/api/stats/meta` | GET | Variables and group values used by the stats page |
| `/api/stats/regression?target=nitrogen` | GET | Regression with F-test and t-tests |
| `/api/stats/ttest?variable=&group_col=&group_a=&group_b=` | GET | Welch t-test and variance F-test |
| `/api/stats/anova?variable=&group_col=` | GET | One-way ANOVA |

Example `/api/predict` body:

```json
{
  "ph": 6.4, "moisture": 74, "temperature": 27, "rainfall": 140,
  "soil_type": "Sandy Loam", "location": "Tropical",
  "nitrogen": 110, "phosphorus": 25, "potassium": 135
}
```

`ph`, `moisture`, `temperature` and `rainfall` are required. The rest are optional.

Valid `variable` values for the stats endpoints: `nitrogen`, `phosphorus`, `potassium`,
`ph_avg`, `moisture_avg`, `temp_avg`, `rainfall_avg`. Valid `group_col` values: `location`,
`soil_type`.

## Troubleshooting

| Problem | Fix |
|---|---|
| `DATABASE_URL is not set` | Copy `.env.example` to `.env` and paste your Neon connection string. |
| `relation "crops" does not exist` | Run `schema.sql`, then `seed_data.py`. |
| Duplicate crops in results | Run `schema.sql` again, then `seed_data.py` once. |
| "No text found in this PDF" | The PDF is a scan. Use a text-based PDF or enter values manually. |
| Some fields not filled after upload | The label wasn't found in the report. Fill them in by hand or adjust `FIELD_LABELS`. |
| Dropdowns are empty | The database has no rows yet, or the app can't reach it. Check `.env` and re-run the seed. |

## Deployment

Any host that runs Flask works (Render, Railway, Fly.io, a VM). Set `DATABASE_URL` as an
environment variable on the host rather than committing `.env`, and run the app with a
production server such as `pip install gunicorn` then `gunicorn app:app`, not `python app.py`
(which starts Flask's debug server).
