# =============================================================================
#  APEX-DENT — Dentist Dashboard MVP
#  Built with: Python + Streamlit
#  Run with:   streamlit run apex_dent_dashboard.py
#
#  Architecture note:
#  This is a single-file MVP prototype.  All "backend" logic is simulated
#  locally using Python dicts, random delays (time.sleep), and Streamlit
#  session_state.  In production these would be replaced by:
#    - REST/GraphQL calls to the NestJS backend
#    - PostgreSQL queries via an ORM (SQLAlchemy / Prisma)
#    - The FastAPI AI-service for real STL analysis
# =============================================================================

import streamlit as st
import pandas as pd
import time
import random
from datetime import datetime, timedelta

# ─────────────────────────────────────────────────────────────────────────────
#  PAGE CONFIG  (must be the very first Streamlit call)
# ─────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Apex-Dent | Dentist Dashboard",
    page_icon="🦷",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────────────────────────────────────
#  GLOBAL CSS — blue-themed, clean, professional
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
/* ── Root palette ─────────────────────────────────────── */
:root {
    --bg:        #070F1C;
    --surface:   #0D1B2E;
    --surfaceMd: #112338;
    --border:    #1E3352;
    --cyan:      #00C8F0;
    --teal:      #00B4A0;
    --violet:    #7C5CFC;
    --amber:     #F0A500;
    --rose:      #F04060;
    --green:     #22D17A;
    --white:     #E8F4FF;
    --grey:      #6A8099;
    --greyLt:    #A0B8CC;
}

/* ── Global background ────────────────────────────────── */
.stApp { background-color: var(--bg); color: var(--white); }

/* ── Sidebar ──────────────────────────────────────────── */
[data-testid="stSidebar"] {
    background: var(--surface) !important;
    border-right: 1px solid var(--border);
}
[data-testid="stSidebar"] * { color: var(--greyLt) !important; }

/* ── Sidebar radio labels ─────────────────────────────── */
[data-testid="stSidebar"] label { font-size: 14px !important; }

/* ── Metric cards ─────────────────────────────────────── */
[data-testid="stMetric"] {
    background: var(--surfaceMd);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 14px 18px;
}
[data-testid="stMetricLabel"]  { color: var(--grey)   !important; font-size: 11px !important; letter-spacing: 1px; text-transform: uppercase; }
[data-testid="stMetricValue"]  { color: var(--cyan)   !important; font-size: 26px !important; font-weight: 800; }
[data-testid="stMetricDelta"]  { color: var(--teal)   !important; }

/* ── Buttons ──────────────────────────────────────────── */
.stButton > button {
    background: linear-gradient(135deg, #00A8CC, #0080AA) !important;
    color: #fff !important;
    border: none !important;
    border-radius: 7px !important;
    font-weight: 600 !important;
    font-size: 13px !important;
    padding: 7px 18px !important;
    transition: opacity .2s !important;
}
.stButton > button:hover { opacity: 0.85 !important; }

/* ── Danger buttons (Cancel) ──────────────────────────── */
.btn-cancel > button {
    background: linear-gradient(135deg, #C03050, #A02040) !important;
}

/* ── Dataframe / tables ───────────────────────────────── */
[data-testid="stDataFrame"] { border-radius: 10px; overflow: hidden; }
thead tr th {
    background: var(--surfaceMd) !important;
    color: var(--cyan) !important;
    font-size: 12px !important;
    letter-spacing: 1px;
    text-transform: uppercase;
}
tbody tr td { color: var(--white) !important; font-size: 13px !important; }
tbody tr:nth-child(even) { background: var(--surfaceMd) !important; }

/* ── Select boxes & file uploader ────────────────────── */
[data-testid="stSelectbox"] > div > div,
[data-testid="stFileUploader"] {
    background: var(--surfaceMd) !important;border: 1px solid var(--border) !important;
    border-radius: 8px !important;
    color: var(--white) !important;
}

/* ── Progress bar ─────────────────────────────────────── */
[data-testid="stProgressBar"] > div { background: var(--surfaceMd); border-radius: 6px; }
[data-testid="stProgressBar"] > div > div { background: var(--cyan) !important; border-radius: 6px; }

/* ── Alert / info boxes ───────────────────────────────── */
[data-testid="stAlert"] { border-radius: 8px !important; }

/* ── Divider ──────────────────────────────────────────── */
hr { border-color: var(--border) !important; }

/* ── Custom card helper ───────────────────────────────── */
.apex-card {
    background: var(--surfaceMd);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 20px 22px;
    margin-bottom: 16px;
}
.apex-card-accent {
    border-left: 3px solid var(--cyan);
}
.apex-tag {
    display: inline-block;
    font-size: 10px; font-weight: 700; letter-spacing: 1.2px;
    text-transform: uppercase; padding: 2px 9px; border-radius: 4px;
}
.tag-pending  { background:#F0A50020; color:#F0A500; border:1px solid #F0A50040; }
.tag-confirm  { background:#22D17A20; color:#22D17A; border:1px solid #22D17A40; }
.tag-cancel   { background:#F0406020; color:#F04060; border:1px solid #F0406040; }
.tag-pass     { background:#22D17A20; color:#22D17A; border:1px solid #22D17A40; }
.tag-warn     { background:#F0A50020; color:#F0A500; border:1px solid #F0A50040; }
.tag-reject   { background:#F0406020; color:#F04060; border:1px solid #F0406040; }
.section-eye  { font-family:monospace; font-size:11px; color:#00C8F0;
                letter-spacing:2px; font-weight:700; }
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
#  SIMULATED DATA  (replaces database queries in production)
# ─────────────────────────────────────────────────────────────────────────────

# Simulate today's appointment list (would come from GET /appointments?date=today)
def get_appointments():
    today = datetime.now().date()
    return [
        {"id": 1, "patient": "Youssef Belkacem",  "time": "09:00", "type": "Check-up",        "status": "Pending"},
        {"id": 2, "patient": "Fatima Khelifi",    "time": "10:30", "type": "X-Ray",            "status": "Confirmed"},
        {"id": 3, "patient": "Amir Meziane",      "time": "12:00", "type": "Extraction",       "status": "Pending"},
        {"id": 4, "patient": "Lina Bouhired",     "time": "14:00", "type": "Crown Fitting",    "status": "Confirmed"},
        {"id": 5, "patient": "Karim Sahnoune",    "time": "15:30", "type": "Cleaning",         "status": "Pending"},
        {"id": 6, "patient": "Sara Tlemçani",     "time": "17:00", "type": "Veneer Consult",   "status": "Pending"},
    ]

# Simulate existing lab orders (would come from GET /cases?dentist_id=me)
def get_lab_orders():
    return [
        {"case_id": "#C-1038", "patient": "Lina Bouhired",   "tooth": "Tooth #14", "type": "Zirconia Crown",  "lab": "Lab Alpha",  "status": "Milling",    "eta": "2 days"},
        {"case_id": "#C-1035", "patient": "Omar Draa",       "tooth": "Tooth #21", "type": "PFM Bridge",      "lab": "Lab Beta",   "status": "QC Check",   "eta": "1 day"},
        {"case_id": "#C-1031", "patient": "Nadia Chabane",   "tooth": "Tooth #11", "type": "Ceramic Veneer",  "lab": "Lab Gamma",  "status": "Dispatched", "eta": "Today"},
        {"case_id": "#C-1028", "patient": "Youcef Hamadi",   "tooth": "Tooth #36", "type": "Implant Abutment","lab": "Lab Alpha",  "status": "Completed",  "eta": "—"},
    ]

# Available partner labs (would come from GET /labs?match=true)
LAB_OPTIONS = {
    "Lab Alpha — Zirconia Specialist  |  2.1 km  |  Queue: Low":   {"score": 94, "eta": "3 days", "remake_rate": "2.1%"},
    "Lab Beta  — Full-Arch Expert     |  5.8 km  |  Queue: Medium": {"score": 87, "eta": "4 days", "remake_rate": "3.4%"},
    "Lab Gamma — Aesthetics Specialist|  12 km   |  Queue: Low":    {"score": 79, "eta": "3 days", "remake_rate": "4.0%"},
}# Simulated AI Quality Gate checks (replaces FastAPI AI-service call)
AI_CHECKS = [
    ("Mesh Integrity",     "Non-manifold edge detection"),
    ("Margin Clarity",     "Edge sharpness gradient analysis"),
    ("Preparation Depth",  "Depth map vs. material spec"),
    ("Occlusal Clearance", "Opposing arch collision simulation"),
    ("Surface Noise",      "Gaussian deviation analysis"),
    ("File Resolution",    "Point cloud density check"),
    ("Undercut Detection", "Raycast undercut analysis"),
]


# ─────────────────────────────────────────────────────────────────────────────
#  SESSION STATE  — persists UI state between Streamlit reruns
# ─────────────────────────────────────────────────────────────────────────────
if "appointments"     not in st.session_state:
    st.session_state.appointments     = get_appointments()
if "ai_result"        not in st.session_state:
    st.session_state.ai_result        = None   # None | "pass" | "warn" | "reject"
if "ai_check_results" not in st.session_state:
    st.session_state.ai_check_results = []
if "order_sent"       not in st.session_state:
    st.session_state.order_sent       = False
if "selected_lab"     not in st.session_state:
    st.session_state.selected_lab     = None
if "uploaded_file"    not in st.session_state:
    st.session_state.uploaded_file    = None


# ─────────────────────────────────────────────────────────────────────────────
#  SIDEBAR
# ─────────────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 🦷 Apex-Dent")
    st.markdown(
        "<p style='color:#6A8099;font-size:12px;margin-top:-8px;'>Dentist Dashboard — MVP Demo</p>",
        unsafe_allow_html=True,
    )
    st.markdown("---")

    # Main navigation
    page = st.radio(
        "Navigation",
        options=["📅  Appointment Manager", "🔬  Lab Order Management"],
        label_visibility="collapsed",
    )
    st.markdown("---")

    # Quick stats (simulated KPIs)
    st.markdown("<p class='section-eye'>TODAY AT A GLANCE</p>", unsafe_allow_html=True)
    pending_count   = sum(1 for a in st.session_state.appointments if a["status"] == "Pending")
    confirmed_count = sum(1 for a in st.session_state.appointments if a["status"] == "Confirmed")
    st.metric("Appointments Today", len(st.session_state.appointments), f"+{confirmed_count} confirmed")
    st.metric("Pending Confirmation", pending_count)
    st.metric("Active Lab Cases", len([o for o in get_lab_orders() if o["status"] != "Completed"]))

    st.markdown("---")
    st.markdown(
        "<p style='color:#3A5570;font-size:11px;'>Logged in as <b style='color:#A0B8CC'>Dr. Amira Bensalem</b></p>",
        unsafe_allow_html=True,
    )


# ─────────────────────────────────────────────────────────────────────────────
#  HEADER (shared across pages)
# ─────────────────────────────────────────────────────────────────────────────
col_logo, col_title = st.columns([0.08, 0.92])
with col_logo:
    st.markdown("<div style='font-size:40px;line-height:1;padding-top:6px'>🦷</div>", unsafe_allow_html=True)
with col_title:
    if "Appointment" in page:
        st.markdown("## Appointment Manager")
        st.markdown("<p style='color:#6A8099;margin-top:-10px;font-size:14px'>View, confirm, and manage today's patient bookings</p>", unsafe_allow_html=True)
    else:
        st.markdown("## Lab Order Management")
        st.markdown("<p style='color:#6A8099;margin-top:-10px;font-size:14px'>Upload scans, run AI quality checks, and dispatch to partner labs</p>", unsafe_allow_html=True)

st.markdown("---")


# =============================================================================
#  PAGE 1 — APPOINTMENT MANAGER
# =============================================================================
if "Appointment" in page:

    st.markdown("<p class='section-eye'>TODAY'S APPOINTMENTS — " + datetime.now().strftime("%A %d %B %Y") + "</p>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    # ── Status filter ──────────────────────────────────────────────────────filter_status = st.selectbox(
        "Filter by status",
        options=["All", "Pending", "Confirmed", "Cancelled"],
        index=0,
    )

    # ── Appointment rows ───────────────────────────────────────────────────
    appointments = st.session_state.appointments

    # Filter
    if filter_status != "All":
        visible = [a for a in appointments if a["status"] == filter_status]
    else:
        visible = appointments

    if not visible:
        st.info("No appointments match this filter.")
    else:
        # Table header
        hcols = st.columns([0.5, 1.8, 1.4, 1.4, 1.2, 1.4, 1.4])
        for col, label in zip(hcols, ["#", "Patient", "Time", "Type", "Status", "", ""]):
            col.markdown(
                f"<p style='font-size:11px;color:#00C8F0;font-weight:700;letter-spacing:1px;text-transform:uppercase;margin-bottom:4px'>{label}</p>",
                unsafe_allow_html=True,
            )

        st.markdown("<hr style='margin:4px 0 10px;border-color:#1E3352'>", unsafe_allow_html=True)

        for appt in visible:
            idx = next(i for i, a in enumerate(appointments) if a["id"] == appt["id"])

            # Status badge colour
            status = appt["status"]
            tag_cls = {"Pending": "tag-pending", "Confirmed": "tag-confirm", "Cancelled": "tag-cancel"}.get(status, "tag-pending")

            row = st.columns([0.5, 1.8, 1.4, 1.4, 1.2, 1.4, 1.4])
            row[0].markdown(f"<p style='color:#3A5570;font-size:12px;padding-top:8px'>{appt['id']}</p>", unsafe_allow_html=True)
            row[1].markdown(f"<p style='color:#E8F4FF;font-weight:600;font-size:14px;padding-top:8px'>👤 {appt['patient']}</p>", unsafe_allow_html=True)
            row[2].markdown(f"<p style='color:#A0B8CC;font-size:13px;padding-top:8px'>🕐 {appt['time']}</p>", unsafe_allow_html=True)
            row[3].markdown(f"<p style='color:#A0B8CC;font-size:13px;padding-top:8px'>{appt['type']}</p>", unsafe_allow_html=True)
            row[4].markdown(f"<span class='apex-tag {tag_cls}'>{status}</span>", unsafe_allow_html=True)

            # ── CONFIRM button ─────────────────────────────────────────────
            # Simulates: POST /appointments/{id}/confirm → updates DB status
            if status == "Pending":
                if row[5].button("✓ Confirm", key=f"confirm_{appt['id']}"):
                    st.session_state.appointments[idx]["status"] = "Confirmed"
                    st.toast(f"✅ Appointment confirmed for {appt['patient']}", icon="✅")
                    st.rerun()
            else:
                row[5].markdown("<p style='color:#3A5570;font-size:12px;padding-top:8px'>—</p>", unsafe_allow_html=True)

            # ── CANCEL button ──────────────────────────────────────────────
            # Simulates: POST /appointments/{id}/cancel → updates DB + sends SMS
            if status != "Cancelled":
                if row[6].button("✗ Cancel", key=f"cancel_{appt['id']}"):
                    st.session_state.appointments[idx]["status"] = "Cancelled"
                    st.toast(f"❌ Appointment cancelled — patient will be notified by SMS", icon="📱")
                    st.rerun()
            else:
                row[6].markdown("<p style='color:#F04060;font-size:12px;padding-top:8px'>Cancelled</p>", unsafe_allow_html=True)

            st.markdown("<hr style='margin:4px 0;border-color:#1E3352'>", unsafe_allow_html=True)

    # ── Existing lab orders (read-only summary at bottom of page) ──────────
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("<p class='section-eye'>ACTIVE LAB CASES — RESTORATION PATIENTS</p>", unsafe_allow_html=True)
    st.markdown(
        "<p style='color:#6A8099;font-size:12px;margin-top:2px;margin-bottom:14px'>"
        "These patients are awaiting a restoration fitting. They will be notified automatically when their case is dispatched.</p>",
        unsafe_allow_html=True,
    )

    orders = get_lab_orders()
    active_orders = [o for o in orders if o["status"] != "Completed"]

    status_colors = {
        "Milling":    "#00C8F0","QC Check":   "#F0A500",
        "Dispatched": "#22D17A",
        "Completed":  "#6A8099",
    }
    for order in active_orders:
        color = status_colors.get(order["status"], "#A0B8CC")
        st.markdown(f"""
        <div class='apex-card apex-card-accent'>
            <div style='display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:8px'>
                <div>
                    <span style='color:#6A8099;font-size:11px'>{order['case_id']}</span>
                    <span style='color:#E8F4FF;font-weight:700;font-size:14px;margin-left:10px'>👤 {order['patient']}</span>
                    <span style='color:#6A8099;font-size:12px;margin-left:8px'>— {order['tooth']} · {order['type']}</span>
                </div>
                <div style='display:flex;gap:12px;align-items:center'>
                    <span style='font-size:11px;color:#6A8099'>Lab: <b style='color:#A0B8CC'>{order['lab']}</b></span>
                    <span style='font-size:11px;color:#6A8099'>ETA: <b style='color:#A0B8CC'>{order['eta']}</b></span>
                    <span style='background:{color}20;color:{color};border:1px solid {color}40;
                                 font-size:10px;font-weight:700;letter-spacing:1px;padding:2px 9px;border-radius:4px;
                                 text-transform:uppercase'>{order['status']}</span>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)


# =============================================================================
#  PAGE 2 — LAB ORDER MANAGEMENT
# =============================================================================
else:

    # ── STEP 1: Upload STL File ─────────────────────────────────────────────
    st.markdown("<p class='section-eye'>STEP 1 — UPLOAD INTRAORAL SCAN</p>", unsafe_allow_html=True)

    uploaded_file = st.file_uploader(
        "Drag and drop an STL or PLY file from your chairside scanner",
        type=["stl", "ply", "obj", "3mf"],
        help="Supported formats: STL, PLY, OBJ, 3MF — max 200 MB",
    )

    # Persist file info in session (simulates file being saved to S3)
    if uploaded_file is not None:
        st.session_state.uploaded_file = uploaded_file.name
        # Reset AI result if a new file is uploaded
        st.session_state.ai_result        = None
        st.session_state.ai_check_results = []
        st.session_state.order_sent       = False

        file_size_kb = round(uploaded_file.size / 1024, 1)
        st.markdown(f"""
        <div class='apex-card apex-card-accent'>
            <div style='display:flex;gap:16px;align-items:center'>
                <span style='font-size:28px'>📄</span>
                <div>
                    <p style='color:#E8F4FF;font-weight:700;font-size:14px;margin:0'>{uploaded_file.name}</p>
                    <p style='color:#6A8099;font-size:12px;margin:3px 0 0'>
                        Size: {file_size_kb} KB &nbsp;·&nbsp; Type: {uploaded_file.type or "STL"} &nbsp;·&nbsp;
                        <span style='color:#22D17A'>✓ Uploaded successfully</span>
                    </p>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    # ── STEP 2: AI Quality Gate ─────────────────────────────────────────────
    st.markdown("<p class='section-eye'>STEP 2 — AI QUALITY GATE</p>", unsafe_allow_html=True)
    st.markdown(
        "<p style='color:#6A8099;font-size:13px;margin-top:2px;margin-bottom:16px'>"
        "Simulates the FastAPI AI-service: 3D-CNN mesh analysis running 7 checks in under 90 seconds.</p>",
        unsafe_allow_html=True,
    )

    check_disabled = st.session_state.uploaded_file is None

    if check_disabled:
        st.warning("⚠ Please upload an STL file before running the quality check.")

    if st.button("🤖  Run AI Quality Check", disabled=check_disabled, key="ai_check_btn"):
        # ── Simulated AI inference pipeline ───────────────────────────────
        # Production: POST /ai/quality-gate  { stl_url: "s3://..." }# Returns:    { verdict, checks[], heatmap_url, report_text }

        st.session_state.ai_check_results = []
        st.session_state.ai_result        = None

        progress_bar  = st.progress(0, text="Initialising AI engine…")
        results_area  = st.empty()

        for i, (check_name, method) in enumerate(AI_CHECKS):
            # Simulate variable inference time per check
            sleep_time = random.uniform(0.25, 0.65)
            time.sleep(sleep_time)

            # Simulate check outcome — randomised to show WARN or REJECT occasionally
            rand = random.random()
            if rand > 0.92 and i == 1:          # ~8% chance: WARN on margin clarity
                outcome = "⚠ WARNING"
                detail  = "Margin clarity at 78% — below 85% threshold. Consider re-scanning."
                cls     = "warn"
            elif rand > 0.97 and i == 2:        # ~3% chance: REJECT on prep depth
                outcome = "✗ FAIL"
                detail  = "Preparation depth 0.6 mm — below minimum 0.8 mm for Zirconia."
                cls     = "reject"
            else:
                outcome = "✓ PASS"
                detail  = f"{method} — within specification."
                cls     = "pass"

            st.session_state.ai_check_results.append((check_name, outcome, detail, cls))

            # Update progress bar
            pct  = int(((i + 1) / len(AI_CHECKS)) * 100)
            text = f"Checking: {check_name} ({pct}%)"
            progress_bar.progress(pct, text=text)

        # Determine final verdict from results
        outcomes = [r[1] for r in st.session_state.ai_check_results]
        if any("FAIL" in o for o in outcomes):
            st.session_state.ai_result = "reject"
        elif any("WARNING" in o for o in outcomes):
            st.session_state.ai_result = "warn"
        else:
            st.session_state.ai_result = "pass"

        progress_bar.progress(100, text="Analysis complete ✓")
        time.sleep(0.4)
        progress_bar.empty()
        st.rerun()

    # ── Display AI results ─────────────────────────────────────────────────
    if st.session_state.ai_check_results:
        col_checks, col_verdict = st.columns([1.8, 1])

        with col_checks:
            st.markdown("**Check Details**")
            for check_name, outcome, detail, cls in st.session_state.ai_check_results:
                tag_style = {
                    "pass":   "background:#22D17A20;color:#22D17A;border:1px solid #22D17A40",
                    "warn":   "background:#F0A50020;color:#F0A500;border:1px solid #F0A50040",
                    "reject": "background:#F0406020;color:#F04060;border:1px solid #F0406040",
                }[cls]
                st.markdown(f"""
                <div style='display:flex;gap:10px;align-items:flex-start;padding:7px 0;border-bottom:1px solid #1E3352'>
                    <span style='{tag_style};font-size:10px;font-weight:700;letter-spacing:1px;
                                 padding:2px 8px;border-radius:4px;white-space:nowrap;flex-shrink:0'>{outcome}</span>
                    <div>
                        <span style='color:#E8F4FF;font-weight:600;font-size:13px'>{check_name}</span>
                        <p style='color:#6A8099;font-size:12px;margin:2px 0 0'>{detail}</p>
                    </div>
                </div>
                """, unsafe_allow_html=True)

        with col_verdict:
            result = st.session_state.ai_result
            if result == "pass":
                st.markdown("""
                <div style='background:#22D17A15;border:2px solid #22D17A55;border-radius:12px;
                            padding:24px;text-align:center;margin-top:30px'>
                    <div style='font-size:36px'>✅</div>
                    <div style='color:#22D17A;font-weight:800;font-size:20px;margin:8px 0 4px'>PASS</div>
                    <p style='color:#A0B8CC;font-size:12px'>All 7 checks passed. Ready to dispatch to lab.</p>
                </div>""", unsafe_allow_html=True)

            elif result == "warn":
                st.markdown("""
                <div style='background:#F0A50015;border:2px solid #F0A50055;border-radius:12px;
                            padding:24px;text-align:center;margin-top:30px'>
                    <div style='font-size:36px'>⚠️</div>
                    <div style='color:#F0A500;font-weight:800;font-size:20px;margin:8px 0 4px'>PASS WITH NOTES</div>
                    <p style='color:#A0B8CC;font-size:12px'>Minor issue detected. You can still dispatch — review the warning first.</p>
                </div>""", unsafe_allow_html=True)

            else:  # reject
                st.markdown("""
                <div style='background:#F0406015;border:2px solid #F0406055;border-radius:12px;
                            padding:24px;text-align:center;margin-top:30px'>
                    <div style='font-size:36px'>❌</div>
                    <div style='color:#F04060;font-weight:800;font-size:20px;margin:8px 0 4px'>REJECTED</div>
                    <p style='color:#A0B8CC;font-size:12px'>Critical error found. Please re-scan and re-upload before sending to lab.</p>
                </div>""", unsafe_allow_html=True)

    st.markdown("---")

    # ── STEP 3: Select Lab ─────────────────────────────────────────────────
    st.markdown("<p class='section-eye'>STEP 3 — SELECT PARTNER LAB</p>", unsafe_allow_html=True)
    st.markdown(
        "<p style='color:#6A8099;font-size:13px;margin-top:2px;margin-bottom:16px'>"
        "Simulates Smart Matchmaking output: labs are pre-ranked by specialty, queue depth, distance, and historical accuracy.</p>",
        unsafe_allow_html=True,
    )

    lab_choice = st.selectbox(
        "Choose a partner lab",
        options=list(LAB_OPTIONS.keys()),
        index=0,
        disabled=(st.session_state.ai_result is None),
        help="Lab ranking is generated by the AI Matchmaking engine after the Quality Gate passes.",
    )
    st.session_state.selected_lab = lab_choice

    # Show lab scorecard
    if st.session_state.ai_result is not None and lab_choice:
        lab_data = LAB_OPTIONS[lab_choice]
        sc = st.columns(3)
        sc[0].metric("Match Score",   f"{lab_data['score']}%")
        sc[1].metric("Est. Turnaround", lab_data["eta"])
        sc[2].metric("Remake Rate",   lab_data["remake_rate"])

    st.markdown("---")

    # ── STEP 4: Case details + Send Order ─────────────────────────────────
    st.markdown("<p class='section-eye'>STEP 4 — CASE DETAILS & SEND ORDER</p>", unsafe_allow_html=True)

    order_disabled = st.session_state.ai_result not in ("pass", "warn")

    if order_disabled and st.session_state.ai_result == "reject":
        st.error("🚫 Order cannot be sent — AI Quality Gate rejected this file. Please re-scan.")
    elif order_disabled and st.session_state.ai_result is None:
        st.info("ℹ Complete Steps 1 & 2 above before sending an order.")

    with st.form("case_details_form"):
        f1, f2 = st.columns(2)
        patient_name = f1.text_input("Patient Name",       value="Youssef Belkacem",    disabled=order_disabled)
        tooth_number = f2.text_input("Tooth Number",       value="Tooth #14",           disabled=order_disabled)
        f3, f4 = st.columns(2)
        material     = f3.selectbox("Restoration Material",
                                    ["Zirconia Crown", "PFM Crown", "Ceramic Veneer", "Implant Abutment", "Full-Arch Bridge"],
                                    disabled=order_disabled)
        shade        = f4.selectbox("Shade (VITA Scale)",
                                    ["A1", "A2", "A3", "A3.5", "B1", "B2", "C1", "C2", "D2"],
                                    disabled=order_disabled)
        notes = st.text_area("Clinical Notes (optional)",
                             placeholder="e.g. Patient has sensitivity — avoid temporary cement on adjacent teeth.",
                             disabled=order_disabled, height=80)

        send_btn = st.form_submit_button(
            "🚀  Send Order to Lab",
            disabled=order_disabled,
            use_container_width=True,
        )

        if send_btn:# ── Simulates: POST /cases  (creates case record in DB)
            # Body: { dentist_id, patient_name, tooth, material, shade,
            #         stl_url, lab_id, ai_verdict, notes }
            # Returns: { case_id, estimated_eta }
            with st.spinner("Sending order to lab…"):
                time.sleep(1.2)   # simulate network round-trip
            st.session_state.order_sent = True
            st.rerun()

    # ── Success banner ─────────────────────────────────────────────────────
    if st.session_state.order_sent:
        # Simulate case ID returned from backend
        simulated_case_id = f"#C-{random.randint(1050, 1099)}"
        lab_short = lab_choice.split("—")[0].strip() if lab_choice else "Lab Alpha"

        st.markdown(f"""
        <div style='background:linear-gradient(135deg,#22D17A15,#00C8F015);
                    border:2px solid #22D17A55;border-radius:14px;
                    padding:28px 30px;text-align:center;margin-top:10px'>
            <div style='font-size:40px'>🎉</div>
            <h3 style='color:#22D17A;margin:10px 0 6px'>Order Sent Successfully!</h3>
            <p style='color:#A0B8CC;font-size:14px;margin:0 0 16px'>
                Your case has been dispatched to <b style='color:#E8F4FF'>{lab_short}</b>
                and is now in their production queue.
            </p>
            <div style='display:flex;gap:16px;justify-content:center;flex-wrap:wrap'>
                <div style='background:#0D1B2E;border:1px solid #1E3352;border-radius:8px;padding:10px 20px'>
                    <div style='color:#6A8099;font-size:10px;letter-spacing:1px'>CASE ID</div>
                    <div style='color:#00C8F0;font-weight:800;font-size:18px'>{simulated_case_id}</div>
                </div>
                <div style='background:#0D1B2E;border:1px solid #1E3352;border-radius:8px;padding:10px 20px'>
                    <div style='color:#6A8099;font-size:10px;letter-spacing:1px'>AI VERDICT</div>
                    <div style='color:#22D17A;font-weight:800;font-size:18px'>
                        {"PASS ✓" if st.session_state.ai_result == "pass" else "PASS WITH NOTES ⚠"}
                    </div>
                </div>
                <div style='background:#0D1B2E;border:1px solid #1E3352;border-radius:8px;padding:10px 20px'>
                    <div style='color:#6A8099;font-size:10px;letter-spacing:1px'>EST. TURNAROUND</div>
                    <div style='color:#E8F4FF;font-weight:800;font-size:18px'>
                        {LAB_OPTIONS.get(lab_choice, {}).get("eta", "3–5 days")}
                    </div>
                </div>
            </div>
            <p style='color:#3A5570;font-size:12px;margin:16px 0 0'>
                📱 The patient will be notified automatically when the restoration is dispatched from the lab.
            </p>
        </div>
        """, unsafe_allow_html=True)

        # Reset button
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("➕  Start a New Case", key="reset_btn"):
            # Simulates clearing local form state (session) before next upload
            st.session_state.ai_result        = None
            st.session_state.ai_check_results = []
            st.session_state.order_sent       = False
            st.session_state.uploaded_file    = None
            st.rerun()
