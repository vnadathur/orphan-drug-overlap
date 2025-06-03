#!/usr/bin/env bash
set -e
echo "1️⃣  Cleaning & standardising..."
python -m src.data.clean
echo "2️⃣  CDSCO vs FDA comparison..."
python -m src.analysis.compare "$@"
echo "✅  Pipeline complete. Overlap file saved to data/processed/overlap.csv"
