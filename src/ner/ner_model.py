import re

DRUG_NAMES = [
    # Western drugs already in system
    "warfarin", "aspirin", "metformin", "amoxicillin", "ibuprofen",
    "acetaminophen", "paracetamol", "lisinopril", "ciprofloxacin",
    "azithromycin", "tramadol", "potassium", "alcohol", "ssri", "antacids",
    "naproxen", "omeprazole", "atorvastatin", "amlodipine", "simvastatin",
    "nimesulide",

    # Indian brand name generics
    "dolo", "crocin", "combiflam", "brufen", "disprin",
    "ecosprin", "pan", "pantoprazole", "ranitidine", "domperidone",
    "ondansetron", "metoclopramide", "cetirizine", "levocetirizine",
    "montelukast", "salbutamol", "budesonide", "fluticasone",
    "prednisolone", "dexamethasone", "methylprednisolone",
    "amoxicillin", "ampicillin", "cloxacillin", "cephalexin",
    "azithromycin", "clarithromycin", "erythromycin", "doxycycline",
    "tetracycline", "metronidazole", "tinidazole", "fluconazole",
    "clotrimazole", "acyclovir", "oseltamivir",
    "enalapril", "ramipril", "telmisartan", "losartan", "amlodipine",
    "atenolol", "metoprolol", "propranolol", "digoxin", "furosemide",
    "spironolactone", "hydrochlorothiazide",
    "glibenclamide", "glimepiride", "glipizide", "sitagliptin",
    "insulin", "thyroxine", "levothyroxine",
    "calcium", "vitamin", "iron", "folic",
    "diclofenac", "ketorolac", "etoricoxib", "celecoxib",
    "codeine", "morphine", "tramadol", "fentanyl",
    "alprazolam", "clonazepam", "diazepam", "lorazepam",
    "amitriptyline", "escitalopram", "sertraline", "fluoxetine",
    "risperidone", "olanzapine", "haloperidol",
    "phenytoin", "carbamazepine", "valproate", "levetiracetam",
    "atorvastatin", "rosuvastatin", "fenofibrate",
    "heparin", "clopidogrel", "enoxaparin",
    "hydroxychloroquine", "chloroquine",
    "rifampicin", "isoniazid", "pyrazinamide", "ethambutol",
    "albendazole", "mebendazole", "ivermectin"
]

# Remove duplicates while preserving order
seen = set()
DRUG_NAMES = [x for x in DRUG_NAMES
              if not (x in seen or seen.add(x))]

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
    "motrin": "ibuprofen"
}

DOSAGE_PATTERN = re.compile(
    r'\b(\d+\.?\d*)\s*(mg|ml|mcg|g|units?|iu|drops?)\b',
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


def extract_entities(text: str) -> list:
    if not text:
        return []
    try:
        result = []

        # DRUGS — check brand names first, map to generic
        matched_positions = set()
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

        # Then check generic drug names
        for drug in DRUG_NAMES:
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

        # DOSAGES
        for match in DOSAGE_PATTERN.finditer(text):
            result.append({
                "entity": "DOSAGE",
                "value": match.group(0),
                "score": 1.0
            })

        # FREQUENCIES — also map Indian shorthand
        freq_map = {
            "od": "once daily", "bd": "twice daily",
            "tds": "three times daily", "qid": "four times daily",
            "sos": "as needed", "prn": "as needed", "stat": "immediately"
        }
        for match in FREQUENCY_PATTERN.finditer(text):
            val = match.group(0).lower()
            result.append({
                "entity": "FREQUENCY",
                "value": freq_map.get(val, val),
                "score": 1.0
            })

        # AGE
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
