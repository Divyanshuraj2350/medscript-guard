import re
import itertools

INTERACTION_RULES = {
    frozenset({"warfarin", "aspirin"}): {"message": "High bleeding risk — both are blood thinners", "severity": "HIGH"},
    frozenset({"warfarin", "ecosprin"}): {"message": "High bleeding risk — ecosprin is aspirin", "severity": "HIGH"},
    frozenset({"warfarin", "disprin"}): {"message": "High bleeding risk — disprin is aspirin", "severity": "HIGH"},
    frozenset({"warfarin", "ibuprofen"}): {"message": "Increased bleeding and kidney damage risk", "severity": "HIGH"},
    frozenset({"warfarin", "diclofenac"}): {"message": "Increased bleeding risk with NSAIDs", "severity": "HIGH"},
    frozenset({"metformin", "alcohol"}): {"message": "Lactic acidosis risk — alcohol with metformin is dangerous", "severity": "HIGH"},
    frozenset({"ssri", "tramadol"}): {"message": "Serotonin syndrome risk — potentially fatal", "severity": "CRITICAL"},
    frozenset({"escitalopram", "tramadol"}): {"message": "Serotonin syndrome risk", "severity": "CRITICAL"},
    frozenset({"sertraline", "tramadol"}): {"message": "Serotonin syndrome risk", "severity": "CRITICAL"},
    frozenset({"fluoxetine", "tramadol"}): {"message": "Serotonin syndrome risk", "severity": "CRITICAL"},
    frozenset({"lisinopril", "potassium"}): {"message": "Hyperkalemia risk — dangerous potassium buildup", "severity": "MEDIUM"},
    frozenset({"enalapril", "potassium"}): {"message": "Hyperkalemia risk with ACE inhibitor", "severity": "MEDIUM"},
    frozenset({"ramipril", "potassium"}): {"message": "Hyperkalemia risk with ACE inhibitor", "severity": "MEDIUM"},
    frozenset({"ciprofloxacin", "antacids"}): {"message": "Antacids block ciprofloxacin absorption — antibiotic becomes ineffective", "severity": "MEDIUM"},
    frozenset({"aspirin", "ibuprofen"}): {"message": "Combined NSAIDs increase GI bleeding risk significantly", "severity": "HIGH"},
    frozenset({"diclofenac", "ibuprofen"}): {"message": "Two NSAIDs together — increased GI and kidney risk", "severity": "HIGH"},
    frozenset({"diclofenac", "aspirin"}): {"message": "Combined NSAIDs increase bleeding risk", "severity": "HIGH"},
    frozenset({"methotrexate", "aspirin"}): {"message": "Aspirin increases methotrexate toxicity risk", "severity": "CRITICAL"},
    frozenset({"methotrexate", "ibuprofen"}): {"message": "NSAIDs increase methotrexate toxicity", "severity": "CRITICAL"},
    frozenset({"digoxin", "furosemide"}): {"message": "Furosemide causes potassium loss which increases digoxin toxicity risk", "severity": "HIGH"},
    frozenset({"alprazolam", "alcohol"}): {"message": "CNS depression risk — dangerous sedation combination", "severity": "CRITICAL"},
    frozenset({"diazepam", "alcohol"}): {"message": "CNS depression risk — dangerous sedation combination", "severity": "CRITICAL"},
    frozenset({"codeine", "alcohol"}): {"message": "Respiratory depression risk", "severity": "HIGH"},
    frozenset({"morphine", "alcohol"}): {"message": "Respiratory depression risk — potentially fatal", "severity": "CRITICAL"},
    frozenset({"rifampicin", "warfarin"}): {"message": "Rifampicin reduces warfarin effectiveness — clot risk", "severity": "HIGH"},
    frozenset({"rifampicin", "oral contraceptive"}): {"message": "Rifampicin reduces contraceptive effectiveness", "severity": "HIGH"},
    frozenset({"hydroxychloroquine", "azithromycin"}): {"message": "Both prolong QT interval — cardiac arrhythmia risk", "severity": "HIGH"},
    frozenset({"clopidogrel", "omeprazole"}): {"message": "Omeprazole reduces clopidogrel effectiveness", "severity": "MEDIUM"},
    frozenset({"clopidogrel", "pantoprazole"}): {"message": "PPI may reduce clopidogrel effectiveness", "severity": "MEDIUM"},
}

DOSAGE_RANGES = {
    "aspirin": {"min": 50, "max": 325},
    "ecosprin": {"min": 50, "max": 325},
    "disprin": {"min": 50, "max": 325},
    "warfarin": {"min": 1, "max": 10},
    "metformin": {"min": 500, "max": 2000},
    "acetaminophen": {"min": 325, "max": 1000},
    "paracetamol": {"min": 325, "max": 1000},
    "dolo": {"min": 325, "max": 1000},
    "crocin": {"min": 325, "max": 1000},
    "ibuprofen": {"min": 200, "max": 800},
    "combiflam": {"min": 200, "max": 400},
    "brufen": {"min": 200, "max": 800},
    "diclofenac": {"min": 25, "max": 100},
    "nimesulide": {"min": 50, "max": 100},
    "amoxicillin": {"min": 250, "max": 1000},
    "azithromycin": {"min": 250, "max": 500},
    "ciprofloxacin": {"min": 250, "max": 750},
    "prednisolone": {"min": 5, "max": 60},
    "dexamethasone": {"min": 0.5, "max": 10},
    "atorvastatin": {"min": 10, "max": 80},
    "amlodipine": {"min": 2.5, "max": 10},
    "metoprolol": {"min": 25, "max": 200},
    "atenolol": {"min": 25, "max": 100},
}

AGE_CONTRAINDICATIONS = {
    "nimesulide": {
        "max_age": 12,
        "message": "Nimesulide banned for children under 12 in India — hepatotoxicity risk (CDSCO ruling)",
        "severity": "HIGH"
    },
    "aspirin": {
        "max_age": 16,
        "message": "Aspirin avoided under age 16 — risk of Reye syndrome (liver and brain damage)",
        "severity": "HIGH"
    },
    "ecosprin": {
        "max_age": 16,
        "message": "Ecosprin (aspirin) avoided under age 16 — Reye syndrome risk",
        "severity": "HIGH"
    },
    "disprin": {
        "max_age": 16,
        "message": "Disprin (aspirin) avoided under age 16 — Reye syndrome risk",
        "severity": "HIGH"
    },
    "tetracycline": {
        "max_age": 8,
        "message": "Tetracycline avoided under age 8 — permanently stains developing teeth",
        "severity": "HIGH"
    },
    "doxycycline": {
        "max_age": 8,
        "message": "Doxycycline avoided under age 8 — tooth staining and bone growth inhibition",
        "severity": "HIGH"
    },
    "codeine": {
        "max_age": 12,
        "message": "Codeine contraindicated under age 12 — respiratory depression risk in children",
        "severity": "CRITICAL"
    },
    "ibuprofen": {
        "max_age": 3,
        "message": "Ibuprofen not recommended under 3 months — kidney risk in infants",
        "severity": "HIGH"
    },
    "metoclopramide": {
        "max_age": 1,
        "message": "Metoclopramide avoided under age 1 — extrapyramidal side effects in infants",
        "severity": "HIGH"
    },
    "ciprofloxacin": {
        "max_age": 18,
        "message": "Fluoroquinolones avoided under 18 — cartilage damage in growing joints",
        "severity": "MEDIUM"
    },
}


def validate(prescription: dict) -> list:
    try:
        flags = []
        drugs = prescription.get("drugs", [])
        drug_names = [d["name"].lower() for d in drugs]
        patient_age = prescription.get("patient_age")

        # INTERACTION CHECK
        for drug_a, drug_b in itertools.combinations(drug_names, 2):
            pair = frozenset({drug_a, drug_b})
            if pair in INTERACTION_RULES:
                rule = INTERACTION_RULES[pair]
                flags.append({
                    "type": "INTERACTION",
                    "drugs_involved": [drug_a, drug_b],
                    "message": rule["message"],
                    "severity": rule["severity"]
                })

        # DOSAGE CHECK
        for drug in drugs:
            name = drug["name"].lower()
            if name in DOSAGE_RANGES and drug.get("dosage"):
                match = re.search(r'(\d+\.?\d*)', drug["dosage"])
                if match:
                    value = float(match.group(1))
                    limits = DOSAGE_RANGES[name]
                    if value < limits["min"] or value > limits["max"]:
                        flags.append({
                            "type": "DOSAGE_ERROR",
                            "drugs_involved": [name],
                            "message": f"Dosage {drug['dosage']} for {name} is outside safe range ({limits['min']}-{limits['max']}mg)",
                            "severity": "HIGH"
                        })

        # AGE CONTRAINDICATION CHECK
        if patient_age is not None:
            for drug in drugs:
                name = drug["name"].lower()
                if name in AGE_CONTRAINDICATIONS:
                    rule = AGE_CONTRAINDICATIONS[name]
                    if patient_age < rule["max_age"]:
                        flags.append({
                            "type": "AGE_CONTRAINDICATION",
                            "drugs_involved": [name],
                            "message": rule["message"],
                            "severity": rule["severity"]
                        })

        return flags
    except Exception as e:
        print(f"Validation error: {e}")
        return []
