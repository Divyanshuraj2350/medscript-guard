import re
import json
import os

# Load drug list from RxNorm (11,943 drugs)
_drug_list_path = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(
        os.path.abspath(__file__)))),
    "data", "clean_drug_list.json"
)

with open(_drug_list_path) as f:
    RXNORM_DRUGS = set(json.load(f))

# Core Indian/common drugs always included
CORE_DRUGS = [
    "warfarin", "aspirin", "metformin", "amoxicillin", "ibuprofen",
    "acetaminophen", "paracetamol", "lisinopril", "ciprofloxacin",
    "azithromycin", "tramadol", "potassium", "alcohol", "ssri",
    "antacids", "naproxen", "omeprazole", "atorvastatin", "amlodipine",
    "simvastatin", "nimesulide", "dolo", "crocin", "combiflam",
    "brufen", "disprin", "ecosprin", "pan", "pantoprazole",
    "ranitidine", "domperidone", "ondansetron", "metoclopramide",
    "cetirizine", "levocetirizine", "montelukast", "salbutamol",
    "prednisolone", "dexamethasone", "cephalexin", "clarithromycin",
    "erythromycin", "doxycycline", "tetracycline", "metronidazole",
    "fluconazole", "acyclovir", "enalapril", "ramipril", "telmisartan",
    "losartan", "atenolol", "metoprolol", "propranolol", "digoxin",
    "furosemide", "spironolactone", "hydrochlorothiazide", "glibenclamide",
    "glimepiride", "glipizide", "sitagliptin", "insulin", "thyroxine",
    "levothyroxine", "diclofenac", "ketorolac", "etoricoxib", "celecoxib",
    "codeine", "morphine", "fentanyl", "alprazolam", "clonazepam",
    "diazepam", "lorazepam", "amitriptyline", "escitalopram", "sertraline",
    "fluoxetine", "risperidone", "olanzapine", "haloperidol", "phenytoin",
    "carbamazepine", "valproate", "levetiracetam", "rosuvastatin",
    "fenofibrate", "heparin", "clopidogrel", "enoxaparin",
    "hydroxychloroquine", "chloroquine", "rifampicin", "isoniazid",
    "pyrazinamide", "ethambutol", "albendazole", "ivermectin"
]

# Merge both lists
ALL_DRUGS = RXNORM_DRUGS.union(set(CORE_DRUGS))

# Brand name to generic mapping
BRAND_TO_GENERIC = {
    "dolo": "paracetamol",
    "crocin": "paracetamol",
    "combiflam": "ibuprofen",
    "brufen": "ibuprofen",
    "disprin": "aspirin",
    "ecosprin": "aspirin",
    "pan": "pantoprazole",
    "glycomet": "metformin",
    "glucophage": "metformin",
    "coumadin": "warfarin",
    "tylenol": "acetaminophen",
    "advil": "ibuprofen",
    "motrin": "ibuprofen",
    "augmentin": "amoxicillin",
    "zithromax": "azithromycin",
    "cipro": "ciprofloxacin",
    "flagyl": "metronidazole",
    "lasix": "furosemide",
    "tenormin": "atenolol",
    "lopressor": "metoprolol",
    "norvasc": "amlodipine",
    "lipitor": "atorvastatin",
    "crestor": "rosuvastatin",
    "glucophage": "metformin",
    "januvia": "sitagliptin",
    "synthroid": "levothyroxine",
    "ventolin": "salbutamol",
    "allegra": "fexofenadine",
    "zyrtec": "cetirizine",
    "nexium": "esomeprazole",
    "prilosec": "omeprazole"
}

DOSAGE_PATTERN = re.compile(
    r'\b(\d+\.?\d*)\s*(mg|ml|mcg|g|units?|iu|drops?|mmol)\b',
    re.IGNORECASE
)

FREQUENCY_PATTERN = re.compile(
    r'\b(once daily|twice daily|three times daily|four times daily|'
    r'every \d+ hours?|as needed|daily|weekly|monthly|'
    r'once a day|twice a day|three times a day|'
    r'od|bd|tds|qid|sos|prn|stat)\b',
    re.IGNORECASE
)

AGE_PATTERN = re.compile(
    r'\b(?:age|aged)?\s*(\d{1,3})\s*'
    r'(?:years?(?:\s*old)?|y/?o|yr)?\b',
    re.IGNORECASE
)

FREQ_MAP = {
    "od": "once daily",
    "bd": "twice daily",
    "tds": "three times daily",
    "qid": "four times daily",
    "sos": "as needed",
    "prn": "as needed",
    "stat": "immediately"
}


def extract_entities(text: str) -> list:
    if not text:
        return []
    try:
        result = []
        matched_positions = set()
        text_lower = text.lower()

        # Brand names first — map to generic
        for brand, generic in BRAND_TO_GENERIC.items():
            pattern = re.compile(
                r'\b' + re.escape(brand) + r'\b', re.IGNORECASE
            )
            match = pattern.search(text)
            if match:
                result.append({
                    "entity": "DRUG",
                    "value": generic,
                    "score": 1.0
                })
                matched_positions.add(match.start())

        # Then all known drug names
        for drug in ALL_DRUGS:
            if len(drug) < 4:
                continue
            try:
                pattern = re.compile(
                    r'\b' + re.escape(drug) + r'\b', re.IGNORECASE
                )
                match = pattern.search(text)
                if match and match.start() not in matched_positions:
                    result.append({
                        "entity": "DRUG",
                        "value": drug,
                        "score": 1.0
                    })
                    matched_positions.add(match.start())
            except re.error:
                continue

        # DOSAGES
        for match in DOSAGE_PATTERN.finditer(text):
            result.append({
                "entity": "DOSAGE",
                "value": match.group(0),
                "score": 1.0
            })

        # FREQUENCIES
        for match in FREQUENCY_PATTERN.finditer(text):
            val = match.group(0).lower()
            result.append({
                "entity": "FREQUENCY",
                "value": FREQ_MAP.get(val, val),
                "score": 1.0
            })

        # AGE — first valid match between 1 and 120
        for match in AGE_PATTERN.finditer(text):
            age_val = int(match.group(1))
            if 1 <= age_val <= 120:
                result.append({
                    "entity": "PATIENT_AGE",
                    "value": match.group(0).strip(),
                    "score": 1.0
                })
                break

        return result
    except Exception as e:
        print(f"NER error: {e}")
        return []
