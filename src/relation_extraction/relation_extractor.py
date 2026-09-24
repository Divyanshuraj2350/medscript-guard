import re


def extract_relations(entities: list[dict]) -> dict:
    try:
        if not entities or not isinstance(entities, list):
            return {"drugs": [], "patient_age": None}

        # 1. Separate entities into 4 lists by type:
        drugs = [e for e in entities if e.get("entity") == "DRUG"]
        dosages = [dict(e) for e in entities if e.get("entity") == "DOSAGE"]
        frequencies = [e for e in entities if e.get("entity") == "FREQUENCY"]
        ages = [e for e in entities if e.get("entity") == "PATIENT_AGE"]

        # 2. Clean every dosage value — extract only first occurrence of pattern
        for d in dosages:
            val = str(d.get("value", ""))
            match = re.search(r'\d+\.?\d*\s*(?:mg|ml|mcg|g)', val, re.IGNORECASE)
            d["value"] = match.group(0) if match else None

        # 3. Build drug objects by index
        drug_list = []
        for i, drug in enumerate(drugs):
            dosage_val = dosages[i]["value"] if i < len(dosages) else None
            freq_val = frequencies[i]["value"] if i < len(frequencies) else None
            drug_list.append({
                "name": drug.get("value"),
                "dosage": dosage_val,
                "frequency": freq_val
            })

        # 4. patient_age: extract digits from first ages entry
        patient_age = None
        if ages and "value" in ages[0]:
            match = re.search(r'\d+', str(ages[0]["value"]))
            if match:
                patient_age = int(match.group(0))

        # 5. Return prescription object
        return {
            "drugs": drug_list,
            "patient_age": patient_age
        }
    except Exception:
        return {"drugs": [], "patient_age": None}
