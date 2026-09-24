import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import gradio as gr
import requests

API_URL = "http://localhost:8000"

SAMPLE_PRESCRIPTIONS = [
    "Patient age 68. Warfarin 5mg once daily with aspirin 100mg twice daily",
    "Patient age 11. Nimesulide 100mg once daily for fever",
    "Patient age 45. Metformin 500mg twice daily. Alcohol consumption reported",
    "Patient age 30. Amoxicillin 500mg three times daily for 7 days",
    "Patient age 72. Warfarin 10mg once daily with aspirin 200mg"
]

def analyze(prescription_text):
    if not prescription_text or len(prescription_text.strip()) < 10:
        return (
            "⚠️ Please enter a valid prescription (minimum 10 characters)",
            "",
            ""
        )
    try:
        response = requests.post(
            f"{API_URL}/analyze",
            json={"prescription_text": prescription_text},
            timeout=30
        )
        if response.status_code != 200:
            return "❌ API error. Make sure the server is running.", "", ""

        report = response.json()
        risk = report["overall_risk"]

        risk_icons = {
            "LOW": "🟢 LOW RISK",
            "MEDIUM": "🟡 MEDIUM RISK",
            "HIGH": "🔴 HIGH RISK",
            "CRITICAL": "🚨 CRITICAL RISK"
        }
        risk_display = risk_icons.get(risk, risk)

        summary_text = f"**{risk_display}**\n\n{report['summary']}"

        if not report["flags"]:
            flags_text = "✅ No issues detected."
        else:
            flags_text = ""
            for flag in report["flags"]:
                severity_icon = {
                    "LOW": "🔵",
                    "MEDIUM": "🟡",
                    "HIGH": "🔴",
                    "CRITICAL": "🚨"
                }.get(flag["severity"], "⚪")
                flags_text += (
                    f"{severity_icon} **{flag['type']}** "
                    f"| Severity: {flag['severity']}\n\n"
                    f"📋 {flag['message']}\n\n"
                    f"💊 Drugs involved: "
                    f"{', '.join(flag['drugs_involved'])}\n\n"
                    f"---\n\n"
                )

        details_text = ""
        try:
            from src.preprocessing.preprocessor import preprocess
            from src.ner.ner_model import extract_entities
            from src.relation_extraction.relation_extractor import extract_relations

            cleaned = preprocess(prescription_text)
            entities = extract_entities(cleaned)
            prescription = extract_relations(entities)

            details_text = "**Extracted Information:**\n\n"
            details_text += f"👤 Patient Age: {prescription.get('patient_age', 'Not detected')}\n\n"
            details_text += "**Drugs Found:**\n\n"
            for drug in prescription.get("drugs", []):
                details_text += (
                    f"- 💊 **{drug['name'].capitalize()}** "
                    f"| Dose: {drug['dosage'] or 'not specified'} "
                    f"| Frequency: {drug['frequency'] or 'not specified'}\n"
                )
        except Exception:
            details_text = "Could not extract details."

        return summary_text, flags_text, details_text

    except requests.ConnectionError:
        return (
            "❌ Cannot connect to API. Run: uvicorn api.main:app --port 8000",
            "",
            ""
        )
    except Exception as e:
        return f"❌ Unexpected error: {str(e)}", "", ""


def load_sample(sample):
    return sample


with gr.Blocks(title="MedScript Guard", theme=gr.themes.Soft()) as app:

    gr.Markdown("""
    # 🏥 MedScript Guard
    ### Prescription Error Detection System
    *Detects dangerous drug interactions, dosage errors, 
    and age-based contraindications*
    ---
    """)

    with gr.Row():
        with gr.Column(scale=2):
            prescription_input = gr.Textbox(
                label="Enter Prescription Text",
                placeholder="e.g. Patient age 68. Warfarin 5mg once daily "
                            "with aspirin 100mg twice daily",
                lines=6
            )
            analyze_btn = gr.Button(
                "🔍 Analyze Prescription",
                variant="primary",
                size="lg"
            )

            gr.Markdown("**📋 Sample Prescriptions — click to load:**")
            for sample in SAMPLE_PRESCRIPTIONS:
                sample_btn = gr.Button(
                    sample[:60] + "...",
                    size="sm",
                    variant="secondary"
                )
                sample_btn.click(
                    fn=lambda s=sample: s,
                    outputs=prescription_input
                )

        with gr.Column(scale=3):
            risk_output = gr.Markdown(label="Risk Assessment")
            flags_output = gr.Markdown(label="Detected Issues")
            details_output = gr.Markdown(label="Extracted Details")

    analyze_btn.click(
        fn=analyze,
        inputs=prescription_input,
        outputs=[risk_output, flags_output, details_output]
    )

    gr.Markdown("""
    ---
    ⚠️ *MedScript Guard v1.0 — For educational purposes only. 
    Not for clinical use. Always consult a qualified healthcare professional.*
    """)

if __name__ == "__main__":
    app.launch(server_port=7860, share=False)
