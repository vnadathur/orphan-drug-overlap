# Orphan Drug Approval Overlap (CDSCO vs FDA)
[![Python 3.8+](https://img.shields.io/badge/python-3.8%2B-blue)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green)](LICENSE)

An automated pipeline to clean, harmonize, and identify overlapping drug approvals between India's CDSCO and the U.S. FDA.

## Table of Contents

- [Purpose](#purpose)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Data](#data)
- [Pipeline Usage](#pipeline-usage)
- [Optional Utilities](#optional-utilities)
- [Output Files](#output-files)
- [Running Tests](#running-tests)
- [License](#license)

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
   git clone https://github.com/<your-org>/orphan-drug-overlap.git
   cd orphan-drug-overlap
   ```
2. (Optional) Create and activate a virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```
3. Install dependencies:
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

- Execute the full pipeline, producing a final `overlap.csv` with high-confidence matches only:
  ```bash
  bash run_all.sh --explode-combinations  # or omit flag to match on whole drug names
  ```

- Internally, this runs:
  1. `src/data/clean.py` to clean and standardize raw CSVs into Parquet files (`cdsco_clean.parquet`, `fda_clean.parquet`).
  2. `src/analysis/compare.py` to compute one-to-one matches using Jaro-Winkler, Jaccard, and RapidFuzz metrics.
  3. Saves the overlap report to `data/processed/overlap.csv`, containing columns:
     - **CDSCO Drug Name**, **FDA Drug Name**, **Similarity Score** (Jaro-Winkler), **Token Score**, **Ratio Score**, **Match Type**, approval dates and indications.

### Run Comparison Step Only

You can tune similarity thresholds with new flags:
```bash
python -m src.analysis.compare \
  --threshold 0.90 \
  --jaccard-threshold 0.2 \
  --token-threshold 80 \
  --ratio-threshold 80 \
  --out-file data/processed/overlap.csv \
  --use-exploded
```
- `--threshold`: Jaro-Winkler cutoff.
- `--jaccard-threshold`: Jaccard similarity cutoff for candidate filtering.
- `--token-threshold`: RapidFuzz token-set ratio cutoff.
- `--ratio-threshold`: Levenshtein ratio cutoff.

Use `--help` to see all options:
```bash
python -m src.analysis.compare --help
```

## Optional Utilities

Beyond the core pipeline, you can use the following helper scripts:

- **Generate Synonyms Mapping**  
  ```bash
  python synonyms_gen.py
  ```
  Generates `data/processed/synonyms.json` by fuzzy-matching unmatched CDSCO names to FDA canonical names.

- **Check Synonyms Coverage**  
  ```bash
  python synonyms_check.py
  ```
  Reports how many raw CDSCO names are matched via synonyms in your overlap results.

- **Threshold Sweep**  
  ```bash
  python threshold_sweep.py
  ```
  Evaluates different Jaro-Winkler and Jaccard thresholds and writes results to `data/processed/overlap_jw{jw:.2f}_jac{jacc:.2f}.csv`.

## Output Files

- **Parquet files**:
  - `data/processed/cdsco_clean.parquet`, `data/processed/fda_clean.parquet`
  - `data/processed/cdsco_exploded.parquet` (if using `--explode-combinations`)
- **Overlap report**:
  - `data/processed/overlap.csv` (final one-to-one matches with detailed similarity metrics)

## Running Tests

- Unit tests now include checks for the consensus matching helper (`is_high_confidence_match`) and end-to-end matching behavior. Run:
  ```bash
  pytest
  ```

## License

MIT License