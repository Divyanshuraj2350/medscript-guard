# MedScript Guard — Medical Rules Document

This document defines every medical rule currently implemented in the
validation engine, the clinical basis for each rule, and the roadmap
for rules to be added.

---

## Drug Interaction Rules

These are checked by comparing every pair of drugs in the prescription
against the interaction dictionary in `src/validation/validator.py`.

| Drug Pair | Severity | Clinical Reason |
|---|---|---|
| Warfarin + Aspirin | HIGH | Both are blood thinners. Combined use significantly increases bleeding risk, especially gastrointestinal and intracranial bleeding. |
| Metformin + Alcohol | HIGH | Alcohol inhibits lactate metabolism. Combined with metformin this increases risk of lactic acidosis, a rare but potentially fatal condition. |
| SSRI + Tramadol | CRITICAL | Both increase serotonin levels. Combined use can cause serotonin syndrome — symptoms include agitation, high fever, rapid heart rate, and in severe cases death. |
| Lisinopril + Potassium | MEDIUM | Lisinopril (ACE inhibitor) reduces potassium excretion. Adding potassium supplements can cause hyperkalemia (dangerously high potassium), leading to cardiac arrhythmia. |
| Ciprofloxacin + Antacids | MEDIUM | Antacids containing magnesium or aluminum bind to ciprofloxacin in the gut and reduce its absorption by up to 90%, making the antibiotic ineffective. |

---

## Dosage Range Rules

These are checked by extracting the numeric value from the dosage string
and comparing against known safe per-dose ranges.

| Drug | Min Safe Dose | Max Safe Dose | Notes |
|---|---|---|---|
| Aspirin | 50mg | 325mg | Above 325mg per dose increases bleeding risk with no added benefit for most uses |
| Warfarin | 1mg | 10mg | Highly individual — 10mg is an upper bound; most patients are on 2-7mg |
| Metformin | 500mg | 2000mg | Per dose limit; total daily dose can be up to 3000mg but divided |
| Acetaminophen | 325mg | 1000mg | Above 1000mg per dose increases hepatotoxicity risk |
| Ibuprofen | 200mg | 800mg | Above 800mg per dose increases GI and renal risk |

---

## Age-Based Contraindication Rules (Planned — Not Yet Implemented)

These rules need to be added to the validator. This is a known gap.

| Drug | Age Restriction | Reason |
|---|---|---|
| Nimesulide | Banned under age 12 | Hepatotoxicity risk in children. Banned by India's CDSCO for pediatric use. |
| Aspirin | Avoid under age 16 | Risk of Reye's syndrome — rare but fatal liver and brain condition |
| Tetracycline | Avoid under age 8 | Permanently stains developing teeth and inhibits bone growth |
| Codeine | Avoid under age 12 | Ultra-rapid metabolizers can convert to dangerous morphine levels |
| Fluoroquinolones | Avoid under age 18 | Causes cartilage damage in growing joints |
| Metoclopramide | Avoid under age 1 | High risk of extrapyramidal side effects in infants |

---

## How to Add a New Rule

### Adding a drug interaction:

In `src/validation/validator.py`, add to `INTERACTION_RULES`:

```python
frozenset({"drug_a", "drug_b"}): {
    "message": "Clinical description of the risk",
    "severity": "LOW" | "MEDIUM" | "HIGH" | "CRITICAL"
}
```

### Adding a dosage range:

In `src/validation/validator.py`, add to `DOSAGE_RANGES`:

```python
"drug_name": {"min": X, "max": Y}  # values in mg
```

### Adding an age contraindication (once implemented):

In `src/validation/validator.py`, add to `AGE_CONTRAINDICATIONS` (to be created):

```python
"drug_name": {
    "max_age": 12,        # None if no upper limit
    "min_age": None,      # None if no lower limit
    "message": "Banned for children under 12 — hepatotoxicity risk",
    "severity": "HIGH"
}
```

---

## Severity Level Definitions

| Level | Meaning | Action |
|---|---|---|
| LOW | Minor concern, monitor | Note for review |
| MEDIUM | Moderate risk | Pharmacist should verify |
| HIGH | Significant risk | Do not dispense without review |
| CRITICAL | Life-threatening potential | Do not dispense, contact prescriber immediately |

---

## Disclaimer

All rules in this system are for educational demonstration purposes only.
Clinical decisions must always be made by qualified healthcare professionals
using authoritative drug references such as BNF, DrugBank, or FDA labeling.