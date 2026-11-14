import os
import sqlite3
import time
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
import streamlit as st

APP_DIR = Path(__file__).parent
DB_PATH = Path(os.getenv("MEDINOVA_DB_PATH", str(APP_DIR / "medinova.db")))
DB_PATH.parent.mkdir(parents=True, exist_ok=True)

st.set_page_config(page_title="MediNova AI 3.0", page_icon="🧬", layout="wide", initial_sidebar_state="expanded")

DISCLAIMER = (
    "Educational prototype only — not a medical device. It does not diagnose, triage, "
    "interpret personal results, prescribe, or recommend medicine doses. Do not enter "
    "patient-identifying information or private medical records."
)
AI_INSTRUCTIONS = """You are MediNova AI, an educational health-science assistant.
Explain general health science, biology, biotechnology, and pharmacy concepts clearly.
Never diagnose, triage, prescribe, recommend doses, or advise starting/stopping treatment.
Do not interpret an individual's symptoms, reports, or lab values. Do not request personal
identifiers or private health information. For personal medical decisions, direct users to a
qualified healthcare professional. For urgent or severe symptoms, advise contacting local
emergency services or a clinician. Distinguish established facts from uncertainty and never
invent references."""

@st.cache_resource
def initialize_database(db_path: str):
    con = sqlite3.connect(db_path, check_same_thread=False)
    con.execute("""CREATE TABLE IF NOT EXISTS study_notes(
        id INTEGER PRIMARY KEY AUTOINCREMENT, topic TEXT NOT NULL,
        note TEXT NOT NULL, created_at TEXT NOT NULL)""")
    con.execute("""CREATE TABLE IF NOT EXISTS demo_events(
        id INTEGER PRIMARY KEY AUTOINCREMENT, event_type TEXT NOT NULL,
        value REAL NOT NULL, unit TEXT NOT NULL, created_at TEXT NOT NULL,
        source TEXT NOT NULL)""")
    con.commit()
    return True

def connect():
    return sqlite3.connect(DB_PATH, timeout=10)

def save_note(topic, note):
    with connect() as con:
        con.execute("INSERT INTO study_notes(topic,note,created_at) VALUES(?,?,?)",
                    (topic, note, datetime.now(timezone.utc).isoformat()))

def get_notes(limit=30):
    with connect() as con:
        return pd.read_sql_query(
            "SELECT topic,note,created_at FROM study_notes ORDER BY id DESC LIMIT ?",
            con, params=(limit,))

def get_events(limit=100):
    with connect() as con:
        return pd.read_sql_query(
            "SELECT event_type,value,unit,created_at,source FROM demo_events ORDER BY id DESC LIMIT ?",
            con, params=(limit,))

def add_demo_event(kind, value, unit):
    with connect() as con:
        con.execute("INSERT INTO demo_events(event_type,value,unit,created_at,source) VALUES(?,?,?,?,?)",
                    (kind, float(value), unit, datetime.now(timezone.utc).isoformat(), "SIMULATED DEMO DATA"))

@st.cache_resource
def get_ai_client(api_key):
    from openai import OpenAI
    return OpenAI(api_key=api_key)

def ask_ai(question):
    key = st.secrets.get("OPENAI_API_KEY", os.getenv("OPENAI_API_KEY", "")).strip()
    if not key:
        raise RuntimeError("AI is not configured. Add OPENAI_API_KEY as a Streamlit secret.")
    from openai import OpenAI
    client = get_ai_client(key)
    model = os.getenv("OPENAI_MODEL", "gpt-5.5")
    response = client.responses.create(
        model=model, instructions=AI_INSTRUCTIONS, input=question, store=False
    )
    return response.output_text

initialize_database(str(DB_PATH))

st.markdown("""
<style>
.stApp {background:linear-gradient(180deg,#071426 0%,#0b1c31 100%); color:#edf6ff;}
[data-testid="stSidebar"] {background:#0b2038;}
.hero {padding:1.4rem 1.6rem;border:1px solid #1c5575;border-radius:18px;
background:linear-gradient(115deg,#0b3554,#075985 55%,#123b68);margin-bottom:1rem;}
.hero h1 {color:#fff;margin:0;font-size:2.3rem;}
.hero p {color:#c9e9ff;margin:.35rem 0 0;}
div[data-testid="stMetric"] {background:#102b46;border:1px solid #1e5270;padding:14px;border-radius:14px;}
div[data-testid="stMetricLabel"],div[data-testid="stMetricValue"] {color:#eaf7ff;}
.stButton>button {border-radius:10px;border:1px solid #20b8d4;}
.small-muted {color:#a9c5dc;font-size:.85rem;}
</style>
""", unsafe_allow_html=True)

with st.sidebar:
    st.title("🧬 MediNova AI")
    st.caption("Version 3.0 • Real-time learning platform")
    page = st.radio("Platform modules", [
        "Overview", "Live Demo Dashboard", "AI Science Assistant",
        "Medicine Intelligence", "Diagnostics Learning", "Biotechnology Hub",
        "Lab Learning", "Study Notebook", "About & Safety"
    ])
    st.divider()
    ai_configured = bool(st.secrets.get("OPENAI_API_KEY", os.getenv("OPENAI_API_KEY", "")))
    st.caption("AI connection: " + ("Configured" if ai_configured else "Not configured"))
    st.caption("Platform: Android-friendly web app")

st.markdown('<div class="hero"><h1>🧬 MediNova AI 3.0</h1><p>Smarter healthcare knowledge. Connected science. Real-time learning.</p></div>', unsafe_allow_html=True)
st.warning(DISCLAIMER)

if page == "Overview":
    st.subheader("Platform command centre")
    c1,c2,c3 = st.columns(3)
    c1.metric("Learning modules", "8")
    c2.metric("AI assistant", "Ready" if ai_configured else "Setup required")
    c3.metric("Data mode", "Demo / local")
    st.markdown("### What is included")
    cols = st.columns(2)
    features = [
        ("📡 Live demo dashboard","Timestamped simulated sensor events and refreshable metrics."),
        ("🤖 AI science assistant","Optional AI explanations for general educational questions."),
        ("💊 Medicine intelligence","Safe medicine-information framework; no dosing or prescribing."),
        ("🧪 Diagnostics learning","Plain-language explanations of common test concepts."),
        ("🧬 Biotechnology hub","PCR, genomics, bioinformatics and drug discovery topics."),
        ("📚 Study notebook","Save non-sensitive study notes locally.")
    ]
    for i,(title,desc) in enumerate(features):
        with cols[i%2]:
            st.markdown(f"**{title}**")
            st.write(desc)
    st.info("This release is a development prototype. Live demo values are simulated, not measured from a person or medical device.")

elif page == "Live Demo Dashboard":
    st.subheader("📡 Real-time demo data dashboard")
    st.caption("DEMO MODE: all readings generated here are synthetic. They are not health measurements and must never be used for clinical decisions.")
    if "demo_tick" not in st.session_state:
        st.session_state.demo_tick = 0
    a,b = st.columns([1,2])
    with a:
        if st.button("Generate demo event", use_container_width=True):
            import random
            add_demo_event("Demo signal", round(random.uniform(10,99),1), "arbitrary units")
            st.session_state.demo_tick += 1
    with b:
        st.caption("Each event is saved with a UTC timestamp. Refresh the page to see the latest events.")
    data = get_events()
    if not data.empty:
        st.metric("Latest demo signal", f"{data.iloc[0]['value']} {data.iloc[0]['unit']}")
        st.caption("Last event: " + data.iloc[0]["created_at"])
        st.line_chart(data.iloc[::-1].set_index("created_at")["value"])
        st.dataframe(data, use_container_width=True, hide_index=True)
    else:
        st.info("No demo events yet. Select “Generate demo event” to create synthetic data.")
    st.caption("For actual device integration, a separately validated device/API connector and secure consent-based data pipeline are required.")

elif page == "AI Science Assistant":
    st.subheader("🤖 AI Health-Science Education")
    st.write("Ask about general biology, pharmacy, biotechnology, or health-science concepts.")
    st.caption("Do not submit symptoms, personal lab reports, medication decisions, or identifying details.")
    with st.form("science_question"):
        question = st.text_area("Your educational question", placeholder="Example: Explain the principle of PCR.", max_chars=1500)
        submitted = st.form_submit_button("Ask MediNova AI")
    if submitted:
        if len(question.strip()) < 4:
            st.error("Please enter a longer educational question.")
        else:
            with st.spinner("Preparing an educational explanation…"):
                try:
                    st.markdown(ask_ai(question.strip()))
                except Exception as exc:
                    st.error(f"AI is unavailable: {exc}")

elif page == "Medicine Intelligence":
    st.subheader("💊 Medicine information framework")
    st.info("This is a reference-design module, not a prescribing tool. No dose, treatment selection, or self-medication instructions are provided.")
    st.markdown("**Planned verified record fields**")
    st.dataframe(pd.DataFrame([
        {"Field":"Generic name","Purpose":"Identify the medicine"},
        {"Field":"Dosage form","Purpose":"Tablet, capsule, solution, etc."},
        {"Field":"General category","Purpose":"Educational classification"},
        {"Field":"Official source","Purpose":"Traceability to approved information"},
        {"Field":"Reviewed by / date","Purpose":"Qualified professional review"},
        {"Field":"Review status","Purpose":"Draft / reviewed / expired"}
    ]), use_container_width=True, hide_index=True)
    st.warning("Do not add medicine records as verified until reviewed against current official product information by a registered pharmacist or qualified clinician.")

elif page == "Diagnostics Learning":
    st.subheader("🩺 Diagnostics learning")
    concepts = {
        "Complete blood count (CBC)":"A group of tests measuring components of blood, including red cells, white cells and platelets.",
        "Blood glucose":"A measurement of glucose in blood. Interpretation depends on test conditions and clinical context.",
        "Lipid profile":"A group of measurements related to blood lipids, commonly including cholesterol and triglycerides.",
        "Creatinine":"A waste product measured in blood; it can contribute to assessment of kidney function alongside other information.",
        "Thyroid-stimulating hormone (TSH)":"A hormone involved in regulating thyroid activity."
    }
    chosen = st.selectbox("Choose a diagnostic concept", list(concepts))
    st.info(concepts[chosen])
    st.caption("This module teaches test concepts only. It does not interpret personal results or identify disease.")

elif page == "Biotechnology Hub":
    st.subheader("🧬 Biotechnology knowledge hub")
    topics = {
        "PCR":"Polymerase chain reaction is a laboratory technique used to amplify selected DNA segments.",
        "Genomics":"Genomics studies an organism's complete DNA and how genetic information relates to biological function.",
        "Bioinformatics":"Bioinformatics combines biology, computing and statistics to analyze biological data.",
        "Pharmacogenomics":"Pharmacogenomics studies how genetic variation can influence responses to medicines. Clinical use requires validated tests and professional interpretation.",
        "Biomarkers":"A biomarker is a measurable biological characteristic that can indicate a biological process or response.",
        "Drug discovery":"Drug discovery includes target research, screening, development and carefully controlled preclinical and clinical studies."
    }
    topic = st.selectbox("Select a topic", list(topics))
    st.info(topics[topic])

elif page == "Lab Learning":
    st.subheader("🧪 Laboratory science learning")
    labs = {
        "Haemoglobin":"Haemoglobin is the oxygen-carrying protein in red blood cells.",
        "Fasting blood glucose":"This test measures blood glucose after a specified fasting period.",
        "Creatinine":"Creatinine is a waste product used with other clinical information to assess kidney function.",
        "TSH":"Thyroid-stimulating hormone helps regulate thyroid activity.",
        "Lipid profile":"A lipid profile measures selected fats in blood, including cholesterol and triglycerides."
    }
    lab = st.selectbox("Select a lab test", list(labs))
    st.info(labs[lab])
    st.caption("Reference intervals vary by laboratory and method. Personal results should be discussed with a healthcare professional.")

elif page == "Study Notebook":
    st.subheader("📚 Personal study notebook")
    with st.form("note_form"):
        topic = st.text_input("Topic", max_chars=100)
        note = st.text_area("Study note", max_chars=3000)
        saved = st.form_submit_button("Save note")
    if saved:
        if topic.strip() and note.strip():
            save_note(topic.strip(), note.strip())
            st.success("Study note saved.")
        else:
            st.error("Enter both a topic and a note.")
    notes = get_notes()
    if not notes.empty:
        st.dataframe(notes, use_container_width=True, hide_index=True)
    st.caption("Do not store patient information or private medical records here.")

else:
    st.subheader("About MediNova AI 3.0")
    st.markdown("""
**Developer:** Mokshith Reddy  
**Platform:** Python + Streamlit  
**Target:** Android browsers and desktop web  
**Release:** Development prototype

**Safety and privacy**
- No diagnosis, triage, treatment recommendation, or medicine dosing.
- No user accounts or secure patient-record service in this version.
- Local SQLite storage may be ephemeral on cloud hosting and is not encrypted.
- AI questions are sent to the configured AI provider; only submit general educational questions.
- Do not use real patient data for testing.

**Before real-world deployment**
- Obtain clinical and pharmacy professional review.
- Complete privacy, security, and threat-model assessments.
- Use a managed database with encryption, access controls, backups and audit logging.
- Validate any device/API integration and obtain applicable Indian regulatory advice.
- Conduct accessibility, load and security testing.
""")

st.divider()
st.caption("MediNova AI 3.0 • Developed by Mokshith Reddy • Educational prototype")
