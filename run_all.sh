#!/usr/bin/env bash
set -e

# Process command line options
USE_EXPLODED=false

# Parse arguments
while [[ $# -gt 0 ]]; do
  key="$1"
  case $key in
    --explode-combinations)
      USE_EXPLODED=true
      shift
      ;;
    *)
      # Keep other arguments for passing to the compare module
      ARGS="$ARGS $1"
      shift
      ;;
  esac
done

echo "1️⃣  Cleaning & standardising..."
if [ "$USE_EXPLODED" = true ]; then
    python -m src.data.clean --explode-combinations
    echo "2️⃣  CDSCO vs FDA comparison (using exploded combination drugs)..."
    python -m src.analysis.compare --use-exploded $ARGS
else
    python -m src.data.clean
    echo "2️⃣  CDSCO vs FDA comparison (standard mode)..."
    python -m src.analysis.compare $ARGS
fi

echo "✅  Pipeline complete. Overlap file saved to data/processed/overlap.csv"
