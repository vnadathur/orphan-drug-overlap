"""
Full cleaning pipeline:
* standardise dates
* normalise drug names / indications
* enforce column schema
"""

from __future__ import annotations
import pandas as pd, re, unicodedata
from .load import load_raw
from .impute import impute
from ..config import CDSCO_CLEAN, FDA_CLEAN, PROC

PROC.mkdir(exist_ok=True, parents=True)

DATE_PAT = re.compile(r"(\d{1,2})[/-](\d{1,2})[/-](\d{2,4})")


def _norm_date(s: str) -> str | pd.NaT:
    """Normalize date strings to a consistent format (MM/DD/YYYY)."""
    if pd.isna(s) or not str(s).strip():
        return pd.NaT
    s = str(s).strip()
    if re.match(r"^\d{4}$", s):  # year only
        return f"01/01/{s}"
    if re.match(r"^\d{2}/\d{4}$", s):  # mm/yyyy
        m, y = s.split("/")
        return f"{m.zfill(2)}/01/{y}"
    m = DATE_PAT.search(s.replace(".", "/").replace("-", "/"))
    if m:
        d, mth, yr = m.groups()
        yr = yr.zfill(4) if len(yr) == 4 else f"19{yr}" if int(yr) > 30 else f"20{yr}"
        return f"{mth.zfill(2)}/{d.zfill(2)}/{yr}"
    return pd.NaT


def _norm_text(x: str) -> str:
    """Normalize text by removing extra spaces and accents."""
    if pd.isna(x):
        return ""
    x = unicodedata.normalize("NFKD", x)
    x = re.sub(r"\s+", " ", x).strip()
    return x


def _strip_forms(drug: str) -> str:
    """Remove dosage forms and strengths from drug names."""
    drug = _norm_text(drug)
    drug = re.sub(
        r"\b(tablet|capsule|injection|cream|ointment|spray|solution|gel|drops?|suspension|eye|ear|nasal|intranasal|oral|iv|im|vial|ampoule|sachet|mg|mcg|g|%|w\/v|w\/w|v\/v)\b.*",
        "",
        drug,
        flags=re.I,
    )
    drug = re.sub(r"[\d.,]+(mg|mcg|g|%)+.*", "", drug, flags=re.I)
    drug = drug.strip(",;- ").title()
    return drug


def clean():
    """Load, clean, and standardize CDSCO and FDA datasets, then save cleaned data."""
    try:
        cdsco, fda = load_raw()
    except FileNotFoundError as e:
        print(f"Error loading raw data: {e}")
        return

    # Standardize CDSCO columns
    cdsco = cdsco.rename(
        columns={
            "Drug Name": "Drug Name",
            "Indication": "Indication",
            "Date of Approval": "Date of Approval",
            "Strength": "Strength",
        }
    )
    cdsco["Date of Approval"] = cdsco["Date of Approval"].apply(_norm_date)
    cdsco["Drug Name"] = cdsco["Drug Name"].apply(_strip_forms)
    cdsco["Indication"] = cdsco["Indication"].apply(_norm_text)

    # Log missing fields and impute if necessary for CDSCO
    cdsco = impute(cdsco, "CDSCO")

    # Standardize FDA columns to match CDSCO schema
    fda = fda.rename(
        columns={
            "Generic Name": "Drug Name",
            "Approved Labeled Indication": "Indication",
            "Marketing Approval Date": "Date of Approval",
            "Orphan Designation": "Orphan",
            "Sponsor Company": "Sponsor",
            "Sponsor Country": "Country",
        }
    )
    fda["Date of Approval"] = fda["Date of Approval"].apply(_norm_date)
    fda["Drug Name"] = fda["Drug Name"].apply(_strip_forms)
    fda["Indication"] = fda["Indication"].apply(_norm_text)
    if "Orphan" in fda:
        fda["Orphan"] = (
            fda["Orphan"]
            .astype(str)
            .str.lower()
            .str.contains("yes|designat|approved")
            .astype(int)
        )

    # Log missing fields and impute if necessary for FDA
    fda = impute(fda, "FDA")

    # Drop duplicate drug entries to minimize duplicates after cleaning
    cdsco = cdsco.drop_duplicates(subset=["Drug Name"])
    fda = fda.drop_duplicates(subset=["Drug Name"])

    cdsco.to_parquet(CDSCO_CLEAN, index=False)
    fda.to_parquet(FDA_CLEAN, index=False)
    print("✅ cleaned data written to", PROC)


if __name__ == "__main__":
    clean()
