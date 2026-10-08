import requests
import json

print("Fetching drug list from RxNorm API...")

# Get common drug names from RxNorm
url = "https://rxnav.nlm.nih.gov/REST/allconcepts.json?tty=IN"
response = requests.get(url, timeout=30)
data = response.json()

concepts = data.get("minConceptGroup", {}).get("minConcept", [])
drug_names = [c["name"].lower() for c in concepts if len(c["name"]) > 2]
drug_names = sorted(set(drug_names))

print(f"Found {len(drug_names)} drug names")

# Save to file
with open("data/rxnorm_drugs.json", "w") as f:
    json.dump(drug_names, f, indent=2)

print("Saved to data/rxnorm_drugs.json")
print("Sample:", drug_names[:20])
