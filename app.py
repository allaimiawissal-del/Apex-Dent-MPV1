import streamlit as st
import pandas as pd
import time
import random
from datetime import datetime, timedelta

# ─────────────────────────────────────────────────────────────────────────────
#  PAGE CONFIG
# ─────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Apex-Dent | Dentist Dashboard",
    page_icon="🦷",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────────────────────────────────────
#  GLOBAL CSS
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
.stApp { background-color: #070F1C; color: #E8F4FF; }
[data-testid="stSidebar"] { background: #0D1B2E !important; border-right: 1px solid #1E3352; }
[data-testid="stSidebar"] * { color: #A0B8CC !important; }
[data-testid="stMetric"] { background: #112338; border: 1px solid #1E3352; border-radius: 10px; padding: 14px 18px; }
.stButton > button { background: linear-gradient(135deg, #00A8CC, #0080AA) !important; color: #fff !important; border: none !important; border-radius: 7px !important; }
.apex-card { background: #112338; border: 1px solid #1E3352; border-radius: 12px; padding: 20px 22px; margin-bottom: 16px; }
.apex-card-accent { border-left: 3px solid #00C8F0; }
.section-eye { font-family:monospace; font-size:11px; color:#00C8F0; letter-spacing:2px; font-weight:700; }
.tag-pending { background:#F0A50020; color:#F0A500; border:1px solid #F0A50040; padding:2px 9px; border-radius:4px; font-size:10px; }
.tag-confirm { background:#22D17A20; color:#22D17A; border:1px solid #22D17A40; padding:2px 9px; border-radius:4px; font-size:10px; }
.tag-cancel { background:#F0406020; color:#F04060; border:1px solid #F0406040; padding:2px 9px; border-radius:4px; font-size:10px; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
#  SIMULATED DATA
# ─────────────────────────────────────────────────────────────────────────────
def get_appointments():
    return [
        {"id": 1, "patient": "Youssef Belkacem",  "time": "09:00", "type": "Check-up",       "status": "Pending"},
        {"id": 2, "patient": "Fatima Khelifi",    "time": "10:30", "type": "X-Ray",          "status": "Confirmed"},
        {"id": 3, "patient": "Amir Meziane",      "time": "12:00", "type": "Extraction",       "status": "Pending"},
        {"id": 4, "patient": "Lina Bouhired",     "time": "14:00", "type": "Crown Fitting",    "status": "Confirmed"},
    ]

def get_lab_orders():
    return [
        {"case_id": "#C-1038", "patient": "Lina Bouhired",   "tooth": "Tooth #14", "type": "Zirconia Crown",  "lab": "Lab Alpha",  "status": "Milling",    "eta": "2 days"},
    ]

LAB_OPTIONS = {
    "Lab Alpha — Zirconia Specialist": {"score": 94, "eta": "3 days", "remake_rate": "2.1%"},
    "Lab Beta — Full-Arch Expert": {"score": 87, "eta": "4 days", "remake_rate": "3.4%"},
}

AI_CHECKS = [("Mesh Integrity", "Non-manifold edge detection"), ("Margin Clarity", "Edge sharpness analysis")]

# ─────────────────────────────────────────────────────────────────────────────
#  SESSION STATE
# ─────────────────────────────────────────────────────────────────────────────
if "appointments" not in st.session_state: st.session_state.appointments = get_appointments()
if "ai_result" not in st.session_state: st.session_state.ai_result = None
if "ai_check_results" not in st.session_state: st.session_state.ai_check_results = []
if "order_sent" not in st.session_state: st.session_state.order_sent = False

# ─────────────────────────────────────────────────────────────────────────────
#  SIDEBAR & NAVIGATION
# ─────────────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 🦷 Apex-Dent")
    page = st.radio("Navigation", options=["📅  Appointment Manager", "🔬  Lab Order Management"])

# ─────────────────────────────────────────────────────────────────────────────
#  MAIN LOGIC
# ─────────────────────────────────────────────────────────────────────────────
if "Appointment" in page:
    st.markdown("## Appointment Manager")
    filter_status = st.selectbox("Filter by status", options=["All", "Pending", "Confirmed", "Cancelled"])
    
    for appt in st.session_state.appointments:
        if filter_status == "All" or appt["status"] == filter_status:
            col1, col2, col3 = st.columns([2, 1, 1])
            col1.write(f"👤 {appt['patient']}")
            col2.write(appt["status"])
            if col3.button("Confirm", key=f"c_{appt['id']}") and appt["status"] == "Pending":
                appt["status"] = "Confirmed"
                st.rerun()
else:
    st.markdown("## Lab Order Management")
    uploaded_file = st.file_uploader("Upload STL", type=["stl", "ply"])
    if st.button("🤖 Run AI Quality Check"):
        st.session_state.ai_check_results = [("Mesh Integrity", "PASS", "Normal", "pass")]
        st.session_state.ai_result = "pass"
        st.rerun()
    
    if st.session_state.ai_result == "pass":
        st.success("Analysis complete! Ready to dispatch.")
        if st.button("🚀 Send Order to Lab"):
            st.session_state.order_sent = True
            st.rerun()
