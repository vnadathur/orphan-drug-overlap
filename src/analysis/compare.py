import argparse
import logging
from pathlib import Path

import pandas as pd
import textdistance
from ..config import CDSCO_CLEAN, FDA_CLEAN, PROC
from ..utils.text import normalize, jaccard

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s: %(message)s")

# Ensure output directory exists
PROC.mkdir(exist_ok=True, parents=True)

# Helper for robust fuzzy matching


def jaro(s1, s2):
    """Calculate Jaro-Winkler similarity between two strings."""
    if not isinstance(s1, str) or not isinstance(s2, str):
        return 0.0
    return textdistance.jaro_winkler(s1, s2)


def run(
    threshold: float = 0.90,
    jaccard_threshold: float = 0.3,
    out_file: Path | str | None = None,
):
    """Identify overlapping drugs between CDSCO and FDA datasets using fuzzy matching.
    threshold: Jaro-Winkler similarity threshold.
    jaccard_threshold: Jaccard similarity threshold for candidate filtering.
    out_file: output CSV file path."""
    # Determine output path
    if out_file is None:
        out_file = PROC / "overlap.csv"
    out_file = Path(out_file)
    out_file.parent.mkdir(parents=True, exist_ok=True)

    try:
        logging.info("Loading cleaned datasets")
        c = pd.read_parquet(CDSCO_CLEAN)
        f = pd.read_parquet(FDA_CLEAN)
    except Exception as e:
        logging.error(f"Error loading cleaned data: {e}")
        return

    logging.info("Normalizing drug names")
    c["drug_norm"] = c["Drug Name"].apply(normalize)
    f["drug_norm"] = f["Drug Name"].apply(normalize)

    # Remove entries with empty normalized names
    initial_c, initial_f = len(c), len(f)
    c = c[c["drug_norm"] != ""]
    f = f[f["drug_norm"] != ""]
    logging.info(
        f"Dropped {initial_c - len(c)} CDSCO and {initial_f - len(f)} FDA entries with empty names"
    )

    # Drop duplicate normalized names
    c = c.drop_duplicates(subset=["drug_norm"])
    f = f.drop_duplicates(subset=["drug_norm"])
    logging.info(f"Unique normalized names: CDSCO={len(c)}, FDA={len(f)}")

    # Fuzzy matching with Jaccard pre-filtering
    matches = []
    logging.info("Starting fuzzy matching")
    for _, row in c.iterrows():
        name = row["drug_norm"]
        candidates = f[
            f["drug_norm"].apply(lambda x: jaccard(name, x) >= jaccard_threshold)
        ]
        for _, fda_row in candidates.iterrows():
            score = jaro(name, fda_row["drug_norm"])
            if score >= threshold:
                matches.append(
                    {
                        "CDSCO Drug Name": row["Drug Name"],
                        "FDA Drug Name": fda_row["Drug Name"],
                        "Similarity Score": score,
                        "CDSCO Approval Date": row.get("Date of Approval", ""),
                        "FDA Approval Date": fda_row.get("Date of Approval", ""),
                        "CDSCO Indication": row.get("Indication", ""),
                        "FDA Indication": fda_row.get("Indication", ""),
                    }
                )

    # Compile and save results
    overlap_df = pd.DataFrame(matches).drop_duplicates().reset_index(drop=True)
    overlap_df.to_csv(out_file, index=False)
    logging.info(f"Overlap results written to {out_file}")


def main():
    """Parse command-line arguments and execute the drug matching process."""
    parser = argparse.ArgumentParser(
        description="Match CDSCO and FDA drug entries with fuzzy matching"
    )
    parser.add_argument(
        "--threshold",
        type=float,
        default=0.90,
        help="Jaro-Winkler similarity threshold",
    )
    parser.add_argument(
        "--jaccard-threshold",
        type=float,
        default=0.3,
        help="Jaccard similarity threshold for candidate filtering",
    )
    parser.add_argument(
        "--out-file",
        type=str,
        default=str(PROC / "overlap.csv"),
        help="Output CSV file path",
    )
    args = parser.parse_args()
    run(
        threshold=args.threshold,
        jaccard_threshold=args.jaccard_threshold,
        out_file=args.out_file,
    )


if __name__ == "__main__":
    main()
