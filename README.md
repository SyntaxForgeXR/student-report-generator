# 📊 Report Card Generator

A Streamlit web app that parses LMS exercise export files (CSV or XLSX) and generates visual report cards per student, plus a class-wide analytics overview.

---

## Project Structure

```
report_card_generator/
├── app.py            # Main Streamlit application
├── parser.py         # LMS file parsing logic
├── report_pdf.py     # PDF report card generator (fpdf2)
├── requirements.txt  # Python dependencies
└── README.md
```

---

## Setup

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Run the app

```bash
streamlit run app.py
```

The app will open at `http://localhost:8501`.

---

## Usage

1. **Upload** your LMS export CSV or XLSX from the sidebar.
2. Choose **Individual Report Card** to view a single student's card with gauge, score breakdown, and a downloadable PDF.
3. Choose **Class Overview** for aggregate charts: ranked bar chart, grade distribution, attempts analysis, and a full results table.

---

## Expected File Format

The LMS export must follow this structure:

```
"Exercise Name : <exercise>"       ← row 1 (metadata)
"Course Name : <course>"           ← row 2 (metadata)
Name,UserName,Registration Number,Email,Rank,Total Attempts,Marks Obtained,Total Marks,Percentage,Grade,Contact Number,Section,Standards   ← row 3 (headers)
...data rows...                    ← row 4+
```

### Required columns
`Name`, `UserName`, `Registration Number`, `Email`, `Rank`, `Total Attempts`, `Marks Obtained`, `Total Marks`, `Percentage`, `Grade`, `Contact Number`

### Optional columns
`Section`, `Standards` (shown if not blank/`-`)

---

## Roadmap

- [x] CSV + XLSX upload
- [x] Individual report card with gauge & breakdown chart
- [x] Class overview with bar, pie, and attempts charts
- [x] PDF download per student
- [ ] Batch PDF export (all students)
- [ ] Multi-exercise comparison (upload multiple files)
- [ ] LMS API integration (auto-fetch without manual upload)
- [ ] Email delivery of report cards

---

## Notes for Developers

- `parser.py` handles all file I/O and normalisation. Keep it decoupled from Streamlit so it can be reused in the future API pipeline.
- `report_pdf.py` uses `fpdf2` for zero-dependency PDF generation. If `fpdf2` is not installed, it falls back to a plain-text pseudo-PDF.
- Charts use Plotly for interactivity. To switch to static Matplotlib charts (e.g., for PDF embedding), replace the `go.Figure` calls in `app.py`.
