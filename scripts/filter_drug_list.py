import json
import re

with open("data/rxnorm_drugs.json") as f:
    all_drugs = json.load(f)

def is_clean_drug_name(name):
    # Skip chemical formulas and IUPAC names
    if name.startswith("("):
        return False
    # Skip names with brackets, numbers at start, or special chars
    if re.search(r'^\d', name):
        return False
    if re.search(r'[(){}\[\]]', name):
        return False
    # Skip very long chemical names
    if len(name) > 40:
        return False
    # Skip names with too many hyphens (chemical notation)
    if name.count("-") > 3:
        return False
    # Skip single characters
    if len(name) < 4:
        return False
    # Must contain only letters, hyphens, spaces
    if not re.match(r'^[a-z\-\s]+$', name):
        return False
    return True

clean_drugs = [d for d in all_drugs if is_clean_drug_name(d)]
clean_drugs = sorted(set(clean_drugs))

print(f"Total raw: {len(all_drugs)}")
print(f"After filtering: {len(clean_drugs)}")
print(f"Sample: {clean_drugs[:30]}")

with open("data/clean_drug_list.json", "w") as f:
    json.dump(clean_drugs, f, indent=2)

print("Saved to data/clean_drug_list.json")
