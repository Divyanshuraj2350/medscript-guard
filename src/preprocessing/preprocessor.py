import re

DRUG_MAPPINGS = {
    "paracetamol": "acetaminophen",
    "tylenol": "acetaminophen",
    "advil": "ibuprofen",
    "motrin": "ibuprofen",
    "aleve": "naproxen",
    "naprosyn": "naproxen",
    "glucophage": "metformin",
    "coumadin": "warfarin",
    "zithromax": "azithromycin",
    "amoxil": "amoxicillin",
}

ABBREVIATIONS = {
    "QD": "once daily",
    "BID": "twice daily",
    "TID": "three times daily",
    "QID": "four times daily",
    "PRN": "as needed",
    "PO": "by mouth",
    "SL": "under the tongue",
    "IV": "intravenously",
}


def preprocess(text: str) -> str:
    """Preprocess input text:
    1. Expand medical abbreviations (whole words only).
    2. Normalize drug name variants.
    3. Lowercase the entire string.
    4. Strip all special characters except letters, digits, spaces, and forward slashes.
    """
    # 1. Expand medical abbreviations (whole words only)
    for abbr, expansion in ABBREVIATIONS.items():
        pattern = r"\b" + re.escape(abbr) + r"\b"
        text = re.sub(pattern, expansion, text, flags=re.IGNORECASE)

    # 2. Normalize drug name variants
    for drug, canonical in DRUG_MAPPINGS.items():
        pattern = r"\b" + re.escape(drug) + r"\b"
        text = re.sub(pattern, canonical, text, flags=re.IGNORECASE)

    # 3. Lowercase the entire string
    text = text.lower()

    # 4. Strip all special characters except letters, digits, spaces, and forward slashes
    text = re.sub(r"[^a-z0-9/\s]", "", text)

    return text
