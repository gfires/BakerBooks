# Baker Expense Report Helper — Architecture Synopsis

> **Purpose of this document:** A concise reference for Claude instances (or any new contributor) to quickly understand the codebase structure, data flow, and domain without reading every file.

---

## What This App Does

Baker College P-Card holders use this tool to:
1. Reconcile **expected expenses** (pasted from email) against **actual transactions** (from a Google Sheet).
2. Generate **affidavit PDFs** for expenses that require documentation.

---

## Stack

| Layer | Tech |
|---|---|
| Backend | Python 3.13+, FastAPI 0.115+, Uvicorn |
| Frontend | React 19, TypeScript, Vite 7 |
| PDF | ReportLab (overlay on template), pypdf |
| Drag-and-drop | @dnd-kit/core |
| Sheets parsing | openpyxl (via Google Sheets xlsx export) |

---

## File Structure

```
expense-report-automation/
├── synopsis.md                          ← THIS FILE
├── models.py                            ← Core dataclasses: ReportItem, ExpectedExpense
├── parser.py                            ← Google Sheets parser + PROGRAM_MAP
├── reconcile.py                         ← Two-phase matching algorithm
├── package.json                         ← Root scripts (npm run dev = backend + frontend concurrently)
├── requirements.txt                     ← Root Python deps
│
├── backend/
│   ├── api.py                           ← FastAPI app; all HTTP endpoints
│   ├── models.py                        ← Pydantic request/response schemas (DTOs)
│   ├── pdf_generator.py                 ← Affidavit PDF generation (ReportLab)
│   ├── requirements.txt                 ← Backend-specific deps
│   └── templates/
│       ├── blank_affidavit.pdf          ← PDF template (text overlaid at runtime)
│       └── fonts/AguafinaScript-Regular.ttf  ← Cursive font for signature field
│
└── frontend/
    └── src/
        ├── main.tsx                     ← React entry point
        ├── App.tsx                      ← Root component; owns top-level state
        ├── api.ts                       ← All fetch calls (reconcile, generate-affidavit, health)
        ├── types.ts                     ← TypeScript interfaces mirroring backend schemas
        ├── utils/parseExpenses.ts       ← Frontend parser for expected expense text
        ├── components/
        │   ├── ExpenseForm.tsx          ← Input form (cardholder, date, sheet URL, expense text)
        │   ├── ResultsView.tsx          ← Reconciliation results + drag-and-drop manual matching
        │   └── AffidavitsModal.tsx      ← Batch affidavit download modal
        └── styles/
            ├── App.css
            └── Modal.css
```

---

## Key Domain Concepts

### ExpectedExpense
User-pasted text representing what *should* appear on the P-Card statement.
Format: `MM/DD/YY - Vendor - $Price` or `MM/DD/YY - $Price - Vendor`

### ReportItem
An actual transaction row pulled from the Google Sheet ("Purchases 2023-2024").
Key fields: `description`, `activity` (budget code), `date`, `price`, `vendor`, `receipts`, `flyer`, `needsAffidavit`.

### Reconciliation
Two-phase matching (`reconcile.py`):
1. **Exact match** — price identical, actual date >= expected date
2. **Fuzzy match** — price within $1.00 tolerance, vendor name ≥75% similar (SequenceMatcher), actual date >= expected date

Result is three lists: `matched_pairs`, `unmatched_expected`, `unmatched_actual`.

### Affidavit
A PDF based on `blank_affidavit.pdf` with overlaid text: vendor, price, expense date, cardholder signature (first 2 words of name in AguafinaScript font), and today's date.
Only generated for rows where the sheet column P value is "No" (i.e., `needsAffidavit = True`).

---

## API Endpoints (`backend/api.py`)

| Method | Path | Purpose |
|---|---|---|
| POST | `/reconcile` | Main flow: parse sheets + match expenses |
| POST | `/api/generate-affidavit` | Generate and stream affidavit PDF |
| GET | `/health` | Health check |

### `/reconcile` request shape
```json
{
  "cardholder_name": "Gavin Firestone",
  "start_date": "2024-01-01",
  "expected_expenses": "01/15/24 - Vendor Name - $25.00\n...",
  "sheet_link": "https://docs.google.com/spreadsheets/d/..."
}
```

### `/reconcile` response shape
```json
{
  "matched_pairs": [{ "expected": {...}, "actual": {...} }],
  "unmatched_expected": [...],
  "unmatched_actual": [...]
}
```

---

## Data Flow

### Reconciliation
```
User fills ExpenseForm
  → POST /reconcile
    → parser.py: download sheet via ?format=xlsx export, filter by cardholder + date
    → reconcile.py: parse expected text, run two-phase match
  → ReconcileResponse returned
→ App.tsx passes to ResultsView
→ User can drag "Extra Actual" cards onto "Missing Expected" drop zones (manual pairing)
→ Affidavit download button per matched item with needsAffidavit=true
```

### Affidavit Generation (two paths)
1. **From ResultsView**: Per matched expense with `needsAffidavit=true` → POST `/api/generate-affidavit`
2. **From "Generate Affidavits" button**: Parses expense text locally (`parseExpenses.ts`), opens `AffidavitsModal`, downloads each PDF on demand

---

## Google Sheets Schema (`parser.py`)

Sheet name: `"Purchases"`

| Column | Field | Notes |
|---|---|---|
| A | Timestamp | Used as date filter (>= start_date) |
| B | Name | Purchaser name → description |
| C | Items purchased | → description |
| D | Vendor | |
| E | Event | → description |
| F | Price | Parsed with `parse_price()` |
| G | P-Card holder | Filtered by `cardholder_name` |
| H | Budget category | Mapped via `PROGRAM_MAP` → activity code (e.g. "Cab Retreat" → "6100") |
| I | Endowment | Appended to description when budget is "Other" |
| J | Flyer link | |
| K | Receipts | Comma-separated URLs |
| L | Needs Affidavit | "No" → `needsAffidavit = True` |

---

## Frontend State (`App.tsx`)

```typescript
results: ReconcileResponse | null   // from /reconcile
loading: boolean
error: string | null
cardholderName: string              // passed to ResultsView for PDF requests
```

`ResultsView` owns local state:
```typescript
manualPairings: Map<string, ReportItem>  // expectedId → actual (drag-and-drop pairings)
```

---

## Hardcoded Cardholders (`ExpenseForm.tsx`)
- Gavin Firestone
- Gopi Amin
- Sami Johnson
- Allie Meachum
- Jesse Romero
- Vero Paz Agreda

To add a cardholder, update the `<select>` options in [frontend/src/components/ExpenseForm.tsx](frontend/src/components/ExpenseForm.tsx).

---

## Dev Setup

```bash
npm run dev           # starts both backend (port 8000) and frontend (port 5173) concurrently
npm run dev:backend   # uvicorn backend/api.py --reload --port 8000
npm run dev:frontend  # cd frontend && npm run dev
```

Vite proxies `/reconcile`, `/health`, and `/api/*` to `http://localhost:8000`.

---

## Key File Cross-Reference

| Task | File(s) |
|---|---|
| Add/change API endpoint | [backend/api.py](backend/api.py) |
| Change matching logic (tolerance, threshold) | [reconcile.py](reconcile.py) |
| Change sheet parsing / column mapping | [parser.py](parser.py) |
| Change PDF layout or content | [backend/pdf_generator.py](backend/pdf_generator.py) |
| Add a cardholder | [frontend/src/components/ExpenseForm.tsx](frontend/src/components/ExpenseForm.tsx) |
| Change request/response shape | [backend/models.py](backend/models.py) + [frontend/src/types.ts](frontend/src/types.ts) |
| Change drag-and-drop behavior | [frontend/src/components/ResultsView.tsx](frontend/src/components/ResultsView.tsx) |
| Change affidavit batch modal | [frontend/src/components/AffidavitsModal.tsx](frontend/src/components/AffidavitsModal.tsx) |
| Core dataclasses (non-HTTP) | [models.py](models.py) |
