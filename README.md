# Drug Approval Overlap Analysis (CDSCO vs FDA)

An automated pipeline to clean, harmonize, and identify overlapping drug approvals between India's CDSCO and the U.S. FDA.

## Purpose

This pipeline was built to streamline the process of comparing two large regulatory drug datasets:
- **CDSCO**: Central Drugs Standard Control Organization (India)
- **FDA**: U.S. Food and Drug Administration

It standardizes and cleans raw drug lists, performs fuzzy and Jaccard similarity matching, and generates a final report of overlapping approved drugs.

## Prerequisites

- Python 3.8 or above
- Pip

## Installation

1. Clone this repository:
   ```bash
   git clone <repo-url>
   cd "OD Data Cleaning Pipeline"
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Data

Place your raw datasets in `data/raw` with the following filenames:
- `cdsco_drugs.csv`
- `fda_orphan_drugs.csv`

Download the latest CDSCO and FDA orphan drug lists from their respective websites and save them here.

## Pipeline Usage

### Run All Steps

Execute the full pipeline:
```bash
bash run_all.sh
```
This runs:
1. `src/data/clean.py` to clean and standardize raw data
2. `src/analysis/compare.py` to perform the comparison
3. Results are saved to `data/processed/overlap.csv`

### Run Individual Steps

1. Clean & Standardize:
   ```bash
   python -m src.data.clean
   ```
2. Compare CDSCO vs FDA:
   ```bash
   python -m src.analysis.compare --threshold 0.85 --jaccard-threshold 0.3 --out-file data/processed/overlap.csv
   ```
Use `--help` for additional options:
```bash
python -m src.analysis.compare --help
```

## Output

- Cleaned outputs: `data/processed/cleaned_cdsco.csv`, `data/processed/cleaned_fda.csv`
- Overlap report: `data/processed/overlap.csv`

## Running Tests

Run the unit test suite with:
```bash
pytest
```

## License

MIT License