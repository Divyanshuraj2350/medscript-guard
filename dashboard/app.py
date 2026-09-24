import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
import requests

API_URL = "http://localhost:8000"

st.title("MedScript Guard")
st.caption("Prescription Error Detection System")

prescription_text = st.text_area(
    label="Enter Prescription Text",
    height=150,
    placeholder="e.g. Patient age 68. Warfarin 5mg once daily with aspirin 100mg",
)

if st.button("Analyze Prescription"):
    if not prescription_text or len(prescription_text.strip()) < 10:
        st.warning("Please enter a valid prescription (minimum 10 characters)")
    else:
        try:
            with st.spinner("Analyzing..."):
                response = requests.post(
                    f"{API_URL}/analyze",
                    json={"prescription_text": prescription_text},
                    timeout=30,
                )

            if response.status_code == 200:
                report = response.json()

                st.metric(label="Overall Risk Level", value=report["overall_risk"])

                color = {
                    "LOW": "green",
                    "MEDIUM": "orange",
                    "HIGH": "red",
                    "CRITICAL": "#8B0000",
                }
                st.markdown(
                    f"### Risk: :{color}[{report['overall_risk']}]"
                    if report["overall_risk"] in ["LOW", "MEDIUM"]
                    else f"<h3 style='color:{color[report['overall_risk']]}'>"
                    f"Risk: {report['overall_risk']}</h3>",
                    unsafe_allow_html=True,
                )

                st.info(report["summary"])

                if report["flags"]:
                    st.subheader("Detected Issues")
                    for flag in report["flags"]:
                        content = (
                            f"**{flag['type']}** | Severity: {flag['severity']}\n\n"
                            f"{flag['message']}\n\n"
                            f"Drugs involved: {', '.join(flag['drugs_involved'])}"
                        )
                        if flag["severity"] in ["HIGH", "CRITICAL"]:
                            st.error(content)
                        elif flag["severity"] == "MEDIUM":
                            st.warning(content)
                        else:
                            st.info(content)
                else:
                    st.success("No issues detected. Safe to dispense.")

        except requests.ConnectionError:
            st.error(
                "Cannot connect to API. Make sure the server is running on port 8000."
            )
        except Exception as e:
            st.error(f"Unexpected error: {str(e)}")

st.divider()
st.caption(
    "MedScript Guard v1.0 — For educational purposes only. Not for clinical use."
)
