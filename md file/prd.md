# MedScript Guard — Product Requirements Document (PRD)

## Problem Statement

Prescription errors are one of the most preventable causes of patient harm in healthcare.
According to WHO, medication errors cause at least 1 death every day and injure approximately
1.3 million people annually in the United States alone.

The three most common error types are:

1. **Wrong dosage** — a drug prescribed at a quantity outside the safe therapeutic range
2. **Dangerous drug interactions** — two or more drugs prescribed together that cause harmful reactions
3. **Age-based contraindications** — drugs prescribed to patients (especially children) for whom the drug is banned or unsafe

Pharmacists catch some of these. Doctors occasionally miss them under time pressure.
Junior medical staff and rural health workers often lack the reference knowledge entirely.

There is no lightweight, real-time tool that a pharmacist or health worker can use to
quickly validate a prescription before dispensing.

---

## What MedScript Guard Does

MedScript Guard is a prescription error detection system that takes raw prescription text
as input and returns a structured risk report flagging:

- Dangerous drug-drug interactions
- Dosage values outside the known safe range for a drug
- Age-based contraindications (drugs banned for specific age groups)

It does this through a multi-stage NLP pipeline that extracts drug names, dosages,
frequencies, and patient age from unstructured text, then validates against a
medical rule engine.

---

## Target Users

| User | How They Use It |
|---|---|
| Pharmacist | Paste prescription text before dispensing |
| Junior doctor | Cross-check before signing a prescription |
| Rural health worker | Validate prescriptions without specialist access |
| Medical student | Learn drug interaction rules interactively |

---

## Core Requirements

### Functional Requirements

- Accept free-text prescription input
- Extract drug names, dosages, frequencies, and patient age
- Detect known dangerous drug-drug interaction pairs
- Detect dosages outside safe therapeutic ranges
- Detect age-based contraindications
- Return a structured risk report with severity levels
- Expose results via a REST API
- Display results on a web dashboard

### Non-Functional Requirements

- API response under 3 seconds for standard prescriptions
- System must not crash on malformed or empty input
- All errors must be caught and returned as structured responses
- Pipeline stages must be independently testable
- Experiment tracking must log every analysis run

---

## Out of Scope (Current Version)

- OCR for handwritten prescriptions
- Authentication or user accounts
- EHR (Electronic Health Record) integration
- Real-time drug database sync
- Multi-language support
- Mobile app

---

## Success Criteria

- 20/20 unit tests passing across all pipeline stages
- Correctly flags warfarin + aspirin interaction as HIGH risk
- Correctly flags dosage outside safe range
- Dashboard renders risk level with correct color coding
- API returns structured JSON for all valid inputs