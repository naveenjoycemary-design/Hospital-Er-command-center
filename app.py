"""
╔══════════════════════════════════════════════════════════════╗
║           ER COMMAND CENTER PRO — v2.1                       ║
║     Real-Time Hospital Emergency Operations Dashboard        ║
╚══════════════════════════════════════════════════════════════╝
"""

# ─────────────────────────────────────────────
# IMPORTS
# ─────────────────────────────────────────────
import time
import random
import math
import pandas as pd
import numpy as np
import streamlit as st
import mysql.connector
import requests
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from faker import Faker
from streamlit_autorefresh import st_autorefresh
import pytz
from datetime import datetime, timedelta

# ─────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="ER Command Center ",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─────────────────────────────────────────────
# AUTO-REFRESH (every 60 seconds)
# ─────────────────────────────────────────────
st_autorefresh(interval=120 * 1000, key="er_pro_refresh")

# ─────────────────────────────────────────────
# GLOBAL CSS — War Room / Glassmorphism Theme
# ─────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Rajdhani:wght@400;500;600;700&family=Share+Tech+Mono&family=Exo+2:wght@300;400;600;800&display=swap');

/* ── Root Variables ── */
:root {
    --bg-deep:        #020b14;
    --bg-panel:       rgba(5, 20, 38, 0.85);
    --bg-card:        rgba(8, 28, 52, 0.9);
    --border-glow:    rgba(0, 180, 255, 0.25);
    --accent-blue:    #00b4ff;
    --accent-teal:    #00ffd5;
    --accent-red:     #ff3355;
    --accent-amber:   #ffbb00;
    --accent-green:   #00ff88;
    --text-primary:   #e8f4fd;
    --text-secondary: #7aa5c4;
    --text-dim:       #3d6080;
    --font-hud:       'Rajdhani', sans-serif;
    --font-mono:      'Share Tech Mono', monospace;
    --font-body:      'Exo 2', sans-serif;
}

/* ── Global ── */
html, body, [class*="css"] {
    background-color: var(--bg-deep) !important;
    color: var(--text-primary) !important;
    font-family: var(--font-body) !important;
}

.stApp {
    background:
        radial-gradient(ellipse at 20% 0%, rgba(0,60,120,0.35) 0%, transparent 55%),
        radial-gradient(ellipse at 80% 100%, rgba(0,30,80,0.3) 0%, transparent 55%),
        linear-gradient(180deg, #020b14 0%, #030d1a 100%) !important;
    background-attachment: fixed !important;
}

/* Grid scanline overlay */
.stApp::before {
    content: "";
    position: fixed;
    inset: 0;
    background-image:
        repeating-linear-gradient(0deg, transparent, transparent 39px, rgba(0,180,255,0.03) 40px),
        repeating-linear-gradient(90deg, transparent, transparent 39px, rgba(0,180,255,0.03) 40px);
    pointer-events: none;
    z-index: 0;
}

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, rgba(2,15,28,0.97) 0%, rgba(3,12,24,0.97) 100%) !important;
    border-right: 1px solid var(--border-glow) !important;
}
[data-testid="stSidebar"] * { font-family: var(--font-body) !important; }

/* ── Hide default sidebar collapse button arrow and replace with clean icon ── */
[data-testid="stSidebarCollapseButton"] {
    background: rgba(0,30,60,0.8) !important;
    border: 1px solid rgba(0,180,255,0.3) !important;
    border-radius: 6px !important;
    width: 28px !important;
    height: 28px !important;
    padding: 0 !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    overflow: hidden !important;
}
[data-testid="stSidebarCollapseButton"] svg {
    display: none !important;
}
[data-testid="stSidebarCollapseButton"]::after {
    content: "◀" !important;
    font-size: 12px !important;
    color: #00b4ff !important;
    font-family: sans-serif !important;
}
[data-testid="stSidebarCollapseButton"]:hover {
    background: rgba(0,100,180,0.4) !important;
    box-shadow: 0 0 10px rgba(0,180,255,0.3) !important;
}

/* ── Block Container ── */
.block-container {
    padding: 1.2rem 2rem 2rem !important;
    max-width: 100% !important;
}

/* ── Metric Cards ── */
[data-testid="stMetric"] {
    background: var(--bg-card) !important;
    border: 1px solid var(--border-glow) !important;
    border-radius: 12px !important;
    padding: 1rem 1.2rem !important;
    box-shadow: 0 0 20px rgba(0,180,255,0.07), inset 0 1px 0 rgba(255,255,255,0.05) !important;
    backdrop-filter: blur(12px) !important;
}
[data-testid="stMetricLabel"] {
    font-family: var(--font-hud) !important;
    font-size: 0.75rem !important;
    letter-spacing: 0.12em !important;
    text-transform: uppercase !important;
    color: var(--text-secondary) !important;
}
[data-testid="stMetricValue"] {
    font-family: var(--font-mono) !important;
    font-size: 1.9rem !important;
    color: var(--accent-blue) !important;
    line-height: 1.1 !important;
}
[data-testid="stMetricDelta"] {
    font-family: var(--font-hud) !important;
    font-size: 0.78rem !important;
}

/* ── DataFrames ── */
[data-testid="stDataFrame"], .stDataFrame {
    border: 1px solid var(--border-glow) !important;
    border-radius: 10px !important;
    overflow: hidden !important;
}
[data-testid="stDataFrame"] thead tr th {
    background: rgba(0, 60, 120, 0.6) !important;
    color: var(--accent-teal) !important;
    font-family: var(--font-hud) !important;
    font-size: 0.73rem !important;
    letter-spacing: 0.1em !important;
    text-transform: uppercase !important;
    border-bottom: 1px solid var(--border-glow) !important;
}

/* ── Section Headers ── */
h1, h2, h3 {
    font-family: var(--font-hud) !important;
    letter-spacing: 0.05em !important;
    color: var(--text-primary) !important;
}

/* ── Plotly Charts ── */
.js-plotly-plot { border-radius: 12px !important; }

/* ── Selectbox / Multiselect ── */
[data-testid="stSelectbox"] > div,
[data-testid="stMultiSelect"] > div {
    background: var(--bg-card) !important;
    border-color: var(--border-glow) !important;
    border-radius: 8px !important;
}

/* ── Buttons ── */
.stButton > button {
    background: linear-gradient(135deg, rgba(0,100,180,0.4), rgba(0,60,120,0.6)) !important;
    border: 1px solid var(--accent-blue) !important;
    color: var(--accent-blue) !important;
    font-family: var(--font-hud) !important;
    letter-spacing: 0.08em !important;
    border-radius: 8px !important;
    font-size: 0.8rem !important;
    text-transform: uppercase !important;
    transition: all 0.2s !important;
}
.stButton > button:hover {
    background: rgba(0, 180, 255, 0.2) !important;
    box-shadow: 0 0 15px rgba(0,180,255,0.3) !important;
}

/* ── Divider ── */
hr { border-color: var(--border-glow) !important; opacity: 0.5 !important; }

/* ── Expander ── */
[data-testid="stExpander"] {
    border: 1px solid var(--border-glow) !important;
    border-radius: 10px !important;
    background: var(--bg-card) !important;
}

/* ── Tabs ── */
[data-testid="stTabs"] [data-baseweb="tab-list"] {
    background: rgba(5,20,38,0.8) !important;
    border-radius: 10px !important;
    border: 1px solid var(--border-glow) !important;
    gap: 4px !important;
    padding: 4px !important;
}
[data-testid="stTabs"] [data-baseweb="tab"] {
    font-family: var(--font-hud) !important;
    font-size: 0.85rem !important;
    letter-spacing: 0.08em !important;
    color: var(--text-secondary) !important;
    border-radius: 7px !important;
    padding: 6px 18px !important;
}
[data-testid="stTabs"] [aria-selected="true"] {
    background: rgba(0,100,180,0.5) !important;
    color: var(--accent-blue) !important;
}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# SECRETS & CONFIG
# ─────────────────────────────────────────────
DB_CONFIG = {
    "host": "mainline.proxy.rlwy.net",
    "user": "root",
    "password": "jwZjmQxvpUWSfMBBTsHIprLVjXNgybAD",
    "database": "railway",
    "port": 24726,
}

WEATHER_API_KEY = "efd6b4dcc0f1b762d34a167b399098a5"
fake = Faker()
IST  = pytz.timezone("Asia/Kolkata")

# ─────────────────────────────────────────────
# CONSTANTS
# ─────────────────────────────────────────────
DEPARTMENTS = ["General Medicine", "Orthopedics", "Cardiology",
               "Neurology", "Pediatrics", "Trauma", "Burns", "Psychiatry"]
TOTAL_BEDS = 80   # ✅ MUST COME FIRST
GENERAL_BEDS  = int(TOTAL_BEDS * 0.8)   # 64
EMERGENCY_BEDS = TOTAL_BEDS - GENERAL_BEDS  # 16

DOCTORS = [
    "Dr. Ananya Iyer",   "Dr. Rajan Mehta",   "Dr. Priya Nair",
    "Dr. Suresh Kumar",  "Dr. Kavitha Rao",   "Dr. Arjun Patel",
    "Dr. Deepa Menon",   "Dr. Vikram Singh",  "Dr. Leela Krishnan",
    "Dr. Anil Sharma",
]

SYMPTOMS_MAP = {
    1: ["Cardiac arrest", "Severe trauma", "Respiratory failure", "Stroke"],
    2: ["Chest pain", "Severe bleeding", "High fever (>104°F)", "Seizures"],
    3: ["Moderate pain", "Fracture suspected", "Vomiting & dehydration", "Infections"],
    4: ["Minor injury", "Mild fever", "Headache", "Abdominal pain"],
    5: ["Prescription refill", "Minor rash", "Cold symptoms", "Routine check"],
}

TOTAL_BEDS    = 80
MAX_ER_HOURS  = 6
AUTO_INTERVAL = 60    # seconds
OVERLOAD_PCT  = 0.85


PLOTLY_DARK_LAYOUT = dict(
    template="plotly_dark",
    paper_bgcolor="rgba(5,20,38,0.0)",
    plot_bgcolor="rgba(5,20,38,0.0)",
    font=dict(family="Exo 2, sans-serif", color="#7aa5c4", size=11),
    margin=dict(l=10, r=10, t=36, b=10),
)

# ─────────────────────────────────────────────
# DB HELPERS
# ─────────────────────────────────────────────
def run_query(sql: str, params=None) -> pd.DataFrame:
    conn = mysql.connector.connect(**DB_CONFIG)
    df   = pd.read_sql(sql, conn, params=params)
    conn.close()
    return df

def run_write(sql: str, params=None):
    conn   = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor()
    cursor.execute(sql, params or ())
    conn.commit()
    cursor.close()
    conn.close()

# ─────────────────────────────────────────────
# SCHEMA BOOTSTRAP
# ─────────────────────────────────────────────
def ensure_table():
    run_write("""
    CREATE TABLE IF NOT EXISTS er_patients_pro (
        id                     INT AUTO_INCREMENT PRIMARY KEY,
        patient_code           VARCHAR(20)  NOT NULL,
        patient_name           VARCHAR(80)  NOT NULL,
        age                    INT          NOT NULL,
        gender                 VARCHAR(10)  NOT NULL,
        triage_level           INT          NOT NULL,
        wait_time              INT          NOT NULL,
        department             VARCHAR(60)  NOT NULL,
        arrival_time           DATETIME     DEFAULT CURRENT_TIMESTAMP,
        temperature_at_arrival FLOAT,
        symptoms               VARCHAR(120),
        arrival_mode           VARCHAR(20),
        bed_assigned           TINYINT(1)   DEFAULT 0,
        doctor_assigned        VARCHAR(80),
        branch                 VARCHAR(60),
        discharged             TINYINT(1)   DEFAULT 0
    )
    """)

ensure_table()

# ─────────────────────────────────────────────
# WEATHER
# ─────────────────────────────────────────────
@st.cache_data(ttl=300)
def get_weather(city: str):
    try:
        url = (f"https://api.openweathermap.org/data/2.5/weather"
               f"?q={city}&appid={WEATHER_API_KEY}&units=metric")
        d   = requests.get(url, timeout=5).json()
        return {
            "condition":   d["weather"][0]["main"],
            "description": d["weather"][0]["description"].title(),
            "temp":        d["main"]["temp"],
            "humidity":    d["main"]["humidity"],
            "icon":        d["weather"][0]["icon"],
        }
    except Exception:
        return {"condition": "Unknown", "description": "N/A", "temp": 30.0,
                "humidity": 60, "icon": "01d"}

def weather_severity(w: dict) -> tuple:
    c, t = w["condition"], w["temp"]
    if c in ("Thunderstorm",):             return 3, "⚡ THUNDERSTORM"
    if c in ("Rain", "Drizzle", "Snow"):   return 2, "🌧 RAIN EVENT"
    if t >= 38:                             return 2, "🔥 EXTREME HEAT"
    if t >= 33:                             return 1, "☀️ HIGH HEAT"
    return 0, "✅ NORMAL"

def weather_admission_multiplier(sev: int) -> float:
    return {0: 1.0, 1: 1.4, 2: 1.9, 3: 2.5}.get(sev, 1.0)

# ─────────────────────────────────────────────
# SIMULATE & INSERT PATIENTS
# ─────────────────────────────────────────────
HOSPITAL_BRANCH = "City General Hospital"

def insert_patient(weather: dict):
    sev   = weather_severity(weather)[0]

    multi = weather_admission_multiplier(sev)
    w_crit = [int(5 * multi), int(10 * multi), 35, 30, 20]
    triage = random.choices([1, 2, 3, 4, 5], weights=w_crit)[0]
    # ── CURRENT BED USAGE ──
    bed_df = run_query("""
    SELECT 
        SUM(CASE WHEN triage_level IN (1,2) THEN 1 ELSE 0 END) AS emergency_used,
        SUM(CASE WHEN triage_level IN (3,4,5) THEN 1 ELSE 0 END) AS general_used
    FROM er_patients_pro
    WHERE bed_assigned = 1 AND discharged = 0
    """)

    emergency_used = int(bed_df["emergency_used"].iloc[0] or 0)
    general_used   = int(bed_df["general_used"].iloc[0] or 0)


    # ── BED ALLOCATION LOGIC ──
    if triage in [1, 2]:
        # Emergency patients
        bed_ok = emergency_used < EMERGENCY_BEDS

    else:
        # General patients
        bed_ok = general_used < GENERAL_BEDS
    
    if (emergency_used + general_used) >= TOTAL_BEDS:
        bed_ok = False
    # ── WAIT TIME BASED ON TRIAGE ──
    if triage == 1:
        wait_time = random.randint(0, 5)

    elif triage == 2:
        wait_time = random.randint(6, 15)

    elif triage == 3:
        wait_time = random.randint(16, 25)

    elif triage == 4:
        wait_time = random.randint(26, 35)

    else:  # triage 5
        wait_time = random.randint(60, 75)
    
    
    
    run_write("""
        INSERT INTO er_patients_pro
        (patient_code, patient_name, age, gender, triage_level, wait_time,
         department, temperature_at_arrival, symptoms, arrival_mode,
         bed_assigned, doctor_assigned, branch)
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
    """, (
        f"ER-{random.randint(100000, 999999)}",
        fake.name(),
        random.randint(1, 95),
        random.choice(["Male", "Female", "Other"]),
        triage,
        wait_time,
        random.choice(DEPARTMENTS),
        round(weather["temp"] + random.uniform(-2, 2), 1),
        random.choice(SYMPTOMS_MAP[triage]),
        random.choice(["Ambulance", "Walk-in", "Walk-in", "Walk-in"]),
        int(bed_ok),
        random.choice(DOCTORS),
        HOSPITAL_BRANCH,
    ))

def insert_batch(weather: dict, count: int):
    for _ in range(count):
        insert_patient(weather)

# ─────────────────────────────────────────────
# AUTO DISCHARGE
# ─────────────────────────────────────────────
def auto_discharge():
    run_write("""
        UPDATE er_patients_pro
        SET discharged = 1
        WHERE discharged = 0
        AND (
            (triage_level = 5 AND arrival_time < NOW() - INTERVAL 2 HOUR) OR
            (triage_level = 4 AND arrival_time < NOW() - INTERVAL 3 HOUR) OR
            (triage_level = 3 AND arrival_time < NOW() - INTERVAL 4 HOUR) OR
            (triage_level = 2 AND arrival_time < NOW() - INTERVAL 5 HOUR) OR
            (triage_level = 1 AND arrival_time < NOW() - INTERVAL 6 HOUR)
        )
    """)

# ─────────────────────────────────────────────
# LOAD DATA
# ─────────────────────────────────────────────
def load_active() -> pd.DataFrame:
    return run_query("""
        SELECT id, patient_code, patient_name, age, gender,
               triage_level, wait_time, department, arrival_time,
               temperature_at_arrival, symptoms, arrival_mode,
               bed_assigned, doctor_assigned, branch
        FROM   er_patients_pro
        WHERE  discharged = 0
          AND  branch = %s
        ORDER  BY arrival_time DESC
        LIMIT  600
    """, (HOSPITAL_BRANCH,))

def load_history(hours: int = 6) -> pd.DataFrame:
    """Load history with explicit UTC handling."""
    return run_query("""
        SELECT arrival_time, triage_level, department, wait_time,
               temperature_at_arrival, bed_assigned
        FROM   er_patients_pro
        WHERE  branch = %s
          AND  arrival_time >= NOW() - INTERVAL %s HOUR
        ORDER  BY arrival_time ASC
    """, (HOSPITAL_BRANCH, hours))

# ─────────────────────────────────────────────
# UTILS
# ─────────────────────────────────────────────
def fmt_wait(m):
    m = int(m)
    return f"{m} min" if m < 60 else f"{m//60}h {m%60}m"

def temp_band(t):
    if pd.isna(t): return "Unknown"
    if t >= 38:    return "Extreme Heat"
    if t >= 32:    return "Hot"
    if t >= 25:    return "Normal"
    return "Cool"

def performance_score(occ_pct, avg_wait, critical_count) -> int:
    score = 100
    score -= min(30, int(occ_pct * 30))
    score -= min(30, int((avg_wait / 120) * 30))
    score -= min(20, critical_count * 2)
    return max(0, score)

def forecast_admissions(hist_df: pd.DataFrame) -> int:
    if hist_df.empty:
        return 0
    hdf = hist_df.copy()
    hdf["arrival_time"] = pd.to_datetime(hdf["arrival_time"])
    hdf["hour"] = hdf["arrival_time"].dt.floor("h")
    per_hour = hdf.groupby("hour").size()
    if len(per_hour) < 2:
        return int(per_hour.mean()) if len(per_hour) else 0
    last_two = per_hour.iloc[-2:]
    trend    = last_two.iloc[-1] - last_two.iloc[-2]
    return max(0, int(last_two.iloc[-1] + trend))

# ─────────────────────────────────────────────
# ════════════════  SIDEBAR  ═════════════════
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="text-align:center;padding:8px 0 20px;">
        <div style="font-family:'Rajdhani',sans-serif;font-size:1.6rem;
                    font-weight:700;color:#00b4ff;letter-spacing:0.12em;">
            🏥 ER-CMD CENTER
        </div>
        <div style="font-size:0.68rem;color:#3d6080;letter-spacing:0.2em;
                    text-transform:uppercase;margin-top:2px;">
            Command Center 
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("**⚙️ Filters**")

    sel_dept = st.multiselect(
        "Department",
        options=DEPARTMENTS,
        default=DEPARTMENTS,
    )
    sel_triage = st.multiselect(
        "Triage Level",
        options=[1, 2, 3, 4, 5],
        default=[1, 2, 3, 4, 5],
        format_func=lambda x: f"Level {x}",
    )
    time_window = st.selectbox("Time Window", ["Last 1 Hour", "Last 3 Hours", "Last 6 Hours", "All Active"])

    st.markdown("---")
    weather_city = st.text_input("🌍 Weather City", value="Chennai")

    st.markdown("---")
    st.markdown("**🛠 Config**")
    max_er_h  = st.slider("Auto Discharge After (hrs)", 2, 12, MAX_ER_HOURS)
    overload  = st.slider("Overload Threshold %", 50, 100, int(OVERLOAD_PCT * 100))
    overload_pct = overload / 100

    st.markdown("---")
    export_btn = st.button("⬇ Export Patient CSV")

# ─────────────────────────────────────────────
# ══════════════  BOOTSTRAP  ══════════════════
# ─────────────────────────────────────────────
auto_discharge()

weather         = get_weather(weather_city)
w_sev, w_label  = weather_severity(weather)
w_multi         = weather_admission_multiplier(w_sev)

full_df = load_active()

beds_assigned = int(full_df["bed_assigned"].sum()) if not full_df.empty else 0
beds_available = TOTAL_BEDS - beds_assigned


# ── Smart auto-insert: 1–6 patients per cycle based on load & weather ──
if "last_insert_ts" not in st.session_state:
    st.session_state["last_insert_ts"] = 0

now_ts = time.time()

if now_ts - st.session_state["last_insert_ts"] >= AUTO_INTERVAL:

    # ── SMART INSERT CONTROL ──
    if beds_assigned < TOTAL_BEDS * 0.6:
        base = 3
    elif beds_assigned < TOTAL_BEDS * 0.85:
        base = 2
    else:
        base = 1  # slow down when near full

    # apply weather effect
    insert_count = int(base * w_multi)

    # clamp limits
    insert_count = max(1, min(insert_count, 6))

    # optional randomness (recommended)
    insert_count = random.randint(max(1, insert_count - 1), insert_count + 1)

    insert_batch(weather, insert_count)

    st.session_state["last_insert_ts"] = now_ts

# ─────────────────────────────────────────────
# LOAD & FILTER DATA
# ─────────────────────────────────────────────
df_raw = load_active()

if df_raw.empty:
    st.warning("⚠️ No active patient data. Seeding initial batch…")
    insert_batch(weather, 20)
    st.rerun()

df_raw["arrival_time"] = pd.to_datetime(df_raw["arrival_time"])

tw_map = {
    "Last 1 Hour": 1, "Last 3 Hours": 3, "Last 6 Hours": 6, "All Active": 999
}
cutoff = datetime.utcnow() - timedelta(hours=tw_map[time_window])
df = df_raw[df_raw["arrival_time"] >= cutoff].copy()
df = df[df["department"].isin(sel_dept) & df["triage_level"].isin(sel_triage)]

if df.empty:
    st.warning("No data matches the current filters.")
    st.stop()

# Derived columns
df["Wait Display"]  = df["wait_time"].apply(fmt_wait)
df["Temp Band"]     = df["temperature_at_arrival"].apply(temp_band)
df["Arrival (IST)"] = (
    df["arrival_time"]
    .dt.tz_localize("UTC", ambiguous="NaT", nonexistent="shift_forward")
    .dt.tz_convert(IST)
    .dt.strftime("%H:%M")
)
df["Bed Status"]    = df["bed_assigned"].map({1: "✅ Assigned", 0: "❌ Waiting"})

# KPIs
total_pts = len(full_df)
avg_wait      = round(df["wait_time"].mean(), 1)
critical_df   = df[df["triage_level"].isin([1, 2])]
critical_cnt  = len(critical_df)
beds_assigned = int(full_df["bed_assigned"].sum())
bed_occ_pct   = min(100, round(beds_assigned / TOTAL_BEDS * 100, 1))
beds_avail    = TOTAL_BEDS - beds_assigned
beds_avail    = TOTAL_BEDS - beds_assigned
long_wait_df  = df[df["wait_time"] > 60]

hist_df       = load_history(6)
last_hr_df    = hist_df[
    pd.to_datetime(hist_df["arrival_time"]) >= datetime.utcnow() - timedelta(hours=1)
] if not hist_df.empty else pd.DataFrame()
admissions_hr = len(last_hr_df)
forecast_next = forecast_admissions(hist_df)
perf_score = performance_score(
    beds_assigned / TOTAL_BEDS,
    avg_wait,
    critical_cnt
)
overloaded = (beds_assigned / TOTAL_BEDS) >= overload_pct

dept_counts         = df.groupby("department").size().reset_index(name="count")
bottleneck_depts    = dept_counts[dept_counts["count"] >= dept_counts["count"].quantile(0.75)]
doc_counts          = df.groupby("doctor_assigned").size().reset_index(name="patients")

# ─────────────────────────────────────────────
# ══════════════  TABS  ════════════════════════
# ─────────────────────────────────────────────
now_ist  = datetime.now(IST).strftime("%a, %d %b %Y  %H:%M:%S IST")

tab_dash, tab_walk = st.tabs(["📊 Live Dashboard", "📖 Walkthrough & Guide"])

# ╔══════════════════════════════════════════╗
# ║           WALKTHROUGH TAB                ║
# ╚══════════════════════════════════════════╝
with tab_walk:
    st.markdown("""
    <div style="background:linear-gradient(135deg,rgba(0,40,80,0.9),rgba(0,20,50,0.95));
                border:1px solid rgba(0,180,255,0.3);border-radius:16px;
                padding:28px 36px;margin-bottom:24px;">
        <div style="font-family:'Rajdhani',sans-serif;font-size:2.2rem;font-weight:700;
                    color:#fff;letter-spacing:0.08em;">
            🏥 ER Command Center 
        </div>
        <div style="font-size:0.9rem;color:#7aa5c4;margin-top:8px;line-height:1.7;">
            A real-time emergency department operations dashboard designed for
            clinical administrators, charge nurses, and hospital leadership.
            This guide explains every section so you can use the dashboard confidently.
        </div>
    </div>
    """, unsafe_allow_html=True)

    sections = [
        ("🔄 Auto-Refresh & Live Data",
         "The dashboard automatically refreshes every <b>60 seconds</b> — no manual reload needed. "
         "Every refresh pulls live patient data from the hospital database and inserts a minimum of "
         "<b>10 new simulated patient arrivals</b> to keep the feed active. "
         "The timestamp at top-right always shows the last sync time in IST.",
         "#00b4ff"),

        ("📊 KPI Row (Top Metrics)",
         "<b>Active Census</b> — current undischarged patients vs total beds.<br>"
         "<b>Avg Wait</b> — mean wait time across filtered patients; forecast shows next-hour estimate.<br>"
         "<b>Critical</b> — count of Triage Level 1 & 2 patients needing immediate attention.<br>"
         "<b>Bed Occupancy %</b> — beds assigned as a share of total capacity (80 beds).<br>"
         "<b>Admissions/hr</b> — patients who arrived in the last 60 minutes.<br>"
         "<b>Weather Severity</b> — live weather condition that affects admission multiplier.<br>"
         "<b>Long Waits</b> — patients waiting more than 60 minutes (flag for escalation).<br>"
         "<b>Perf Score</b> — composite 0–100 score based on occupancy, wait times, and critical count.",
         "#00ffd5"),

        ("🌡 Weather Impact Banner",
         "Live weather data from OpenWeatherMap for the configured city. "
         "Weather directly affects patient admission rates via a <b>multiplier</b>:<br>"
         "• Normal → ×1.0 &nbsp;|&nbsp; High Heat → ×1.4 &nbsp;|&nbsp; Rain/Extreme Heat → ×1.9 &nbsp;|&nbsp; Thunderstorm → ×2.5<br>"
         "During surge conditions, the banner turns amber/red and a surge recommendation appears.",
         "#ffbb00"),

        ("🚨 Overload Alert",
         "When active patient count exceeds the configured overload threshold (default 85% of 80 beds), "
         "a red alert banner fires recommending <b>divert protocol</b>. "
         "You can adjust the threshold using the sidebar slider.",
         "#ff3355"),

        ("📈 Triage Distribution (Donut Chart)",
         "Shows the breakdown of all active patients by triage level (L1–L5). "
         "L1 = immediate life threat (red), L5 = non-urgent (green). "
         "A healthy ER should show mostly L3–L5; a high L1/L2 share signals critical load.",
         "#ff6600"),

        ("🏢 Department Workload (Bar Chart)",
         "Horizontal bar chart showing how many active patients are in each department. "
         "Longer bars indicate departments under pressure. "
         "Cross-reference with the <b>Bottleneck Alerts</b> section below.",
         "#00b4ff"),

        ("📉 Patient Arrival Trend (Line Chart with Trendline)",
         "Line chart bucketed into 30-minute intervals over the last 6 hours. "
         "The <b>trendline</b> shows whether admissions are rising or falling. "
         "An upward-sloping trend combined with a weather surge is an early warning to staff up.",
         "#00ff88"),

        ("🗓 Arrival Heatmap",
         "Density heatmap showing patient volume by <b>day of week × hour of day</b>. "
         "Identifies recurring peak periods (e.g., Monday mornings, Friday evenings). "
         "Use this for predictive staffing and shift planning.",
         "#00ffd5"),

        ("🌡 Temp vs Admissions Correlation",
         "Scatter plot with a linear trendline correlating ambient temperature with hourly admission volume. "
         "A positive slope confirms heat-driven surges. "
         "Each point represents one hour; color intensity reflects admission count.",
         "#ffbb00"),

        ("🔵 Bed Occupancy Gauge",
         "Radial gauge showing live bed occupancy %. "
         "Green zone 0–60%, amber 60–85%, red 85–100%. "
         "The red threshold line matches your sidebar overload setting. "
         "Delta compares to a 70% baseline.",
         "#00b4ff"),

        ("👨‍⚕️ Doctor Workload Distribution",
         "Bar chart showing patient count per doctor across the top 10. "
         "Identifies over-assigned physicians for load balancing. "
         "Color shifts from blue → orange as load increases.",
         "#ff6600"),

        ("🚑 Arrival Mode Split (Donut)",
         "Breakdown of how patients arrive: Ambulance vs Walk-in. "
         "A high ambulance ratio indicates more severe incoming cases.",
         "#ff3355"),

        ("🚨 Critical Triage Alerts Table",
         "Real-time table of all Triage 1 & 2 patients. "
         "Columns show patient code, name, age, department, wait time, symptoms, bed status, and assigned doctor. "
         "Refresh every 60s ensures this is always current.",
         "#ff3355"),

        ("⏳ Long Wait Alerts Table",
         "Patients waiting more than 60 minutes. "
         "Prioritize these for bed assignment or doctor re-routing. "
         "An empty table is the goal.",
         "#ffbb00"),

        ("🏢 Bottleneck Alerts",
         "Auto-detects departments in the top 25th percentile of patient load. "
         "Color-coded cards (red > 30%, amber > 15%, blue otherwise) give instant visual triage of department pressure.",
         "#ff6600"),

        ("⚙️ Sidebar Filters",
         "<b>Department</b> — filter the entire dashboard to specific departments.<br>"
         "<b>Triage Level</b> — focus on specific severity bands.<br>"
         "<b>Time Window</b> — Last 1/3/6 hours or All Active.<br>"
         "<b>Weather City</b> — change the city for weather data.<br>"
         "<b>Auto Discharge After</b> — how many hours before a patient is auto-discharged.<br>"
         "<b>Overload Threshold %</b> — set the alert trigger point.<br>"
         "<b>Export CSV</b> — download the current filtered patient list.",
         "#7aa5c4"),

        ("🏆 Performance Scorecard",
         "Bottom-of-page composite scoring panel. "
         "Score = 100 minus penalties for high occupancy, long waits, and critical case count. "
         "<b>70+</b> = Optimal (green) &nbsp;|&nbsp; <b>40–69</b> = Moderate (amber) &nbsp;|&nbsp; <b>< 40</b> = Critical (red).",
         "#00ff88"),
    ]

    for title, body, color in sections:
        st.markdown(f"""
        <div style="background:rgba(8,28,52,0.85);border-left:3px solid {color};
                    border-radius:0 10px 10px 0;padding:16px 20px;margin-bottom:12px;
                    border-top:1px solid rgba(0,180,255,0.1);
                    border-right:1px solid rgba(0,180,255,0.1);
                    border-bottom:1px solid rgba(0,180,255,0.1);">
            <div style="font-family:'Rajdhani',sans-serif;font-size:1.05rem;
                        font-weight:600;color:{color};letter-spacing:0.07em;margin-bottom:6px;">
                {title}
            </div>
            <div style="font-size:0.85rem;color:#b0cce0;line-height:1.75;">
                {body}
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("""
    <div style="text-align:center;margin-top:24px;font-family:'Share Tech Mono',monospace;
                font-size:0.72rem;color:#1a3a5c;letter-spacing:0.12em;">
        ER COMMAND CENTER   ·  BUILT BY Naveen Raja
    </div>
    """, unsafe_allow_html=True)


# ╔══════════════════════════════════════════╗
# ║           MAIN DASHBOARD TAB             ║
# ╚══════════════════════════════════════════╝
with tab_dash:

    # ── Header Banner ──
    st.markdown(f"""
    <div style="
        background: linear-gradient(135deg, rgba(0,40,80,0.9) 0%, rgba(0,20,50,0.95) 100%);
        border: 1px solid rgba(0,180,255,0.3);
        border-radius: 16px;
        padding: 20px 28px;
        margin-bottom: 18px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        box-shadow: 0 0 40px rgba(0,100,200,0.15), inset 0 1px 0 rgba(255,255,255,0.05);
    ">
        <div>
            <div style="font-family:'Rajdhani',sans-serif;font-size:2rem;
                        font-weight:700;color:#fff;letter-spacing:0.08em;line-height:1;">
                🏥 ER  <span style="color:#00b4ff;">COMMAND CENTER </span>
            </div>
            <div style="font-size:0.82rem;color:#7aa5c4;margin-top:4px;
                        font-family:'Share Tech Mono',monospace;letter-spacing:0.05em;">
                {HOSPITAL_BRANCH.upper()}  ·  LIVE EMERGENCY OPERATIONS
            </div>
        </div>
        <div style="text-align:right;">
            <div style="font-family:'Share Tech Mono',monospace;
                        font-size:0.78rem;color:#00b4ff;">{now_ist}</div>
            <div style="font-size:0.72rem;color:#3d6080;margin-top:4px;
                        font-family:'Rajdhani',sans-serif;letter-spacing:0.1em;">
                AUTO-REFRESH: 60s &nbsp;|&nbsp; FILTERS: {time_window.upper()}
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Weather Banner ──
    BANNER_COLORS = {
        0: ("rgba(0,80,40,0.8)", "#00ff88", "rgba(0,255,136,0.3)"),
        1: ("rgba(80,50,0,0.8)", "#ffbb00", "rgba(255,187,0,0.3)"),
        2: ("rgba(80,30,0,0.8)", "#ff6600", "rgba(255,102,0,0.4)"),
        3: ("rgba(80,0,20,0.8)", "#ff3355", "rgba(255,51,85,0.4)"),
    }
    bg, fg, shadow = BANNER_COLORS[w_sev]

    st.markdown(f"""
    <div style="background:{bg};border:1px solid {fg};border-radius:10px;
                padding:10px 20px;margin-bottom:16px;
                display:flex;justify-content:space-between;align-items:center;
                box-shadow:0 0 20px {shadow};font-family:'Rajdhani',sans-serif;">
        <div style="font-size:1rem;font-weight:600;color:{fg};letter-spacing:0.08em;">
            {w_label} &nbsp;·&nbsp; {weather_city}: {weather['temp']}°C &nbsp;
            <span style="color:#aaa;font-weight:400;font-size:0.85rem;">
            {weather['description']}  ·  Humidity {weather['humidity']}%
            </span>
        </div>
        <div style="font-size:0.82rem;color:{fg};letter-spacing:0.05em;">
            Admission Multiplier: <strong>×{w_multi:.1f}</strong> &nbsp;|&nbsp;
            {'⚠️ WEATHER SURGE ACTIVE — admissions elevated' if w_sev >= 2
             else ('⚡ Mild surge expected' if w_sev == 1 else '✅ Normal admission rates')}
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Overload Alert ──
    if overloaded:
        st.markdown(f"""
        <div style="background:rgba(180,0,30,0.25);border:1.5px solid #ff3355;
                    border-radius:10px;padding:10px 20px;margin-bottom:16px;
                    font-family:'Rajdhani',sans-serif;font-size:1rem;
                    color:#ff3355;letter-spacing:0.07em;
                    box-shadow:0 0 25px rgba(255,51,85,0.3);">
            🚨 &nbsp;OVERLOAD ALERT — ER occupancy at
            <strong>{round(total_pts/TOTAL_BEDS*100,1)}%</strong>
            exceeds threshold ({overload}%). Divert protocol recommended.
        </div>
        """, unsafe_allow_html=True)

    # ── KPI Row ──
    k = st.columns(8)
    k[0].metric("🛏 Active Census",    total_pts,        f"of {TOTAL_BEDS} beds")
    k[1].metric("⏱ Avg Wait",          f"{avg_wait}m",   f"Forecast: {forecast_next}/hr")
    k[2].metric("🚨 Critical",          critical_cnt,     "Triage 1–2")
    k[3].metric("🛏 Bed Occupancy",     f"{bed_occ_pct}%",f"{beds_avail} free")
    k[4].metric("🏥 Admissions/hr",     admissions_hr,    f"↑ next hr ~{forecast_next}")
    k[5].metric("🌡 Weather Severity",  w_label.split()[0], w_label.split()[-1] if len(w_label.split()) > 1 else "")
    k[6].metric("⚠️ Long Waits",        len(long_wait_df), ">60 min")
    k[7].metric("🏆 Perf Score",        f"{perf_score}/100",
                "🟢 Good" if perf_score >= 70 else ("🟡 Fair" if perf_score >= 40 else "🔴 Poor"))

    st.markdown("<br>", unsafe_allow_html=True)

    # ─────────────────────────────────────────────
    # ROW 1: Triage | Dept | Arrival Trend (Line)
    # ─────────────────────────────────────────────
    c1, c2, c3 = st.columns([1.1, 1.1, 1.4])

    # ── Triage Donut ──
    with c1:
        tc = df["triage_level"].value_counts().sort_index().reset_index()
        tc.columns = ["Triage", "Patients"]
        tc["Label"] = tc["Triage"].map(lambda x: f"L{x}")
        fig_t = px.pie(
            tc, names="Label", values="Patients",
            hole=0.6, title="Triage Distribution",
            color="Label",
            color_discrete_map={
                "L1": "#ff2244", "L2": "#ff6600",
                "L3": "#ffbb00", "L4": "#00d4ff", "L5": "#00ff88"},
        )
        fig_t.update_traces(textposition="outside", textinfo="label+percent",
                            marker=dict(line=dict(color="#020b14", width=2)))
        fig_t.update_layout(**PLOTLY_DARK_LAYOUT,
                            legend=dict(orientation="h", y=-0.1))
        st.plotly_chart(fig_t, use_container_width=True)

    # ── Dept Workload ──
    with c2:
        dc = df.groupby("department").size().reset_index(name="Patients")
        dc = dc.sort_values("Patients", ascending=True)
        fig_d = px.bar(
            dc, x="Patients", y="department", orientation="h",
            title="Department Workload",
            color="Patients",
            color_continuous_scale=[[0, "#00305a"], [0.5, "#0077b6"], [1, "#00b4ff"]],
        )
        fig_d.update_layout(**PLOTLY_DARK_LAYOUT, coloraxis_showscale=False,
                            yaxis_title="", xaxis_title="Patients")
        st.plotly_chart(fig_d, use_container_width=True)

    # ── Patient Arrival Trend — Line chart with trendline ──
    with c3:
        if not hist_df.empty:
            h = hist_df.copy()
            h["arrival_time"] = pd.to_datetime(h["arrival_time"])
            h["slot"] = h["arrival_time"].dt.floor("30min")
            trend_data = h.groupby("slot").size().reset_index(name="Admissions")
            trend_data = trend_data.sort_values("slot")

            # Build numeric x for trendline calculation
            if len(trend_data) >= 2:
                x_num = np.arange(len(trend_data))
                y_vals = trend_data["Admissions"].values
                coeffs = np.polyfit(x_num, y_vals, 1)
                poly   = np.poly1d(coeffs)
                trend_data["Trendline"] = poly(x_num)

            fig_tr = go.Figure()
            # Actual line
            fig_tr.add_trace(go.Scatter(
                x=trend_data["slot"],
                y=trend_data["Admissions"],
                mode="lines+markers",
                name="Admissions",
                line=dict(color="#00b4ff", width=2.5),
                marker=dict(size=5, color="#00b4ff"),
                fill="tozeroy",
                fillcolor="rgba(0,180,255,0.08)",
            ))
            # Trendline
            if "Trendline" in trend_data.columns:
                fig_tr.add_trace(go.Scatter(
                    x=trend_data["slot"],
                    y=trend_data["Trendline"],
                    mode="lines",
                    name="Trend",
                    line=dict(color="#ff6600", width=2, dash="dash"),
                ))
            fig_tr.update_layout(
                **PLOTLY_DARK_LAYOUT,
                title="Patient Arrivals (30-min intervals)",
                xaxis_title="",
                yaxis_title="Admissions",
                legend=dict(orientation="h", y=-0.15, x=0),
            )
            st.plotly_chart(fig_tr, use_container_width=True)
        else:
            st.info("Trend data loading…")

    # ─────────────────────────────────────────────
    # ROW 2: Heatmap | Temp vs Admissions | Gauge
    # ─────────────────────────────────────────────
    c4, c5, c6 = st.columns([1.2, 1, 1])

    # ── Arrival Heatmap ──
    with c4:
        if not hist_df.empty:
            h2 = hist_df.copy()
            h2["dt"]   = pd.to_datetime(h2["arrival_time"])
            h2["Hour"] = h2["dt"].dt.hour
            h2["Day"]  = h2["dt"].dt.strftime("%a")
            hmap = h2.groupby(["Day", "Hour"]).size().reset_index(name="Count")
            day_order = ["Mon","Tue","Wed","Thu","Fri","Sat","Sun"]
            hmap["Day"] = pd.Categorical(hmap["Day"], categories=day_order, ordered=True)
            hmap = hmap.sort_values("Day")
            fig_h = px.density_heatmap(
                hmap, x="Hour", y="Day", z="Count",
                title="Patient Arrivals Heatmap",
                color_continuous_scale="Blues",
            )
            fig_h.update_layout(**PLOTLY_DARK_LAYOUT)
            st.plotly_chart(fig_h, use_container_width=True)
        else:
            st.info("Heatmap loading…")

    # ── Temp vs Admissions Correlation (FIXED) ──
    with c5:
        if not hist_df.empty:
            sc_df = hist_df.dropna(subset=["temperature_at_arrival"]).copy()
            sc_df["arrival_time"] = pd.to_datetime(sc_df["arrival_time"])
            sc_df["hour_slot"] = sc_df["arrival_time"].dt.floor("h")

            agg = sc_df.groupby("hour_slot").agg(
                Admissions=("temperature_at_arrival", "count"),
                Avg_Temp=("temperature_at_arrival", "mean")
            ).reset_index()

            if len(agg) >= 2:
                # Manual OLS trendline (avoids statsmodels dependency)
                x_vals = agg["Avg_Temp"].values
                y_vals = agg["Admissions"].values
                coeffs = np.polyfit(x_vals, y_vals, 1)
                x_line = np.linspace(x_vals.min(), x_vals.max(), 100)
                y_line = np.poly1d(coeffs)(x_line)

                fig_sc = go.Figure()
                fig_sc.add_trace(go.Scatter(
                    x=agg["Avg_Temp"],
                    y=agg["Admissions"],
                    mode="markers",
                    name="Hourly Data",
                    marker=dict(
                        size=9,
                        color=agg["Admissions"],
                        colorscale="RdBu_r",
                        showscale=False,
                        line=dict(color="#020b14", width=1),
                    ),
                ))
                fig_sc.add_trace(go.Scatter(
                    x=x_line,
                    y=y_line,
                    mode="lines",
                    name="Trendline",
                    line=dict(color="#ff6600", width=2, dash="dot"),
                ))
                fig_sc.update_layout(
                    **PLOTLY_DARK_LAYOUT,
                    title="Temp vs Admissions",
                    xaxis_title="Avg Temp (°C)",
                    yaxis_title="Admissions",
                    legend=dict(orientation="h", y=-0.2),
                )
                st.plotly_chart(fig_sc, use_container_width=True)
            else:
                st.info("Collecting data for correlation… (need ≥2 hours of history)")
        else:
            st.info("Correlation data loading…")

    # ── Bed Occupancy Gauge ──
    with c6:
        fig_g = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=bed_occ_pct,
            number={"suffix": "%", "font": {"family": "Share Tech Mono", "color": "#00b4ff", "size": 36}},
            delta={"reference": 70, "increasing": {"color": "#ff3355"}, "decreasing": {"color": "#00ff88"}},
            title={"text": "Bed Occupancy", "font": {"family": "Rajdhani", "color": "#7aa5c4", "size": 14}},
            gauge={
                "axis": {"range": [0, 100], "tickcolor": "#3d6080"},
                "bar":  {"color": "#00b4ff", "thickness": 0.25},
                "bgcolor": "rgba(0,0,0,0)",
                "borderwidth": 1,
                "bordercolor": "#1a3a5c",
                "steps": [
                    {"range": [0, 60],  "color": "rgba(0,255,136,0.1)"},
                    {"range": [60, 85], "color": "rgba(255,187,0,0.1)"},
                    {"range": [85, 100],"color": "rgba(255,51,85,0.15)"},
                ],
                "threshold": {
                    "line": {"color": "#ff3355", "width": 3},
                    "thickness": 0.8,
                    "value": overload,
                },
            },
        ))
        fig_g.update_layout(**PLOTLY_DARK_LAYOUT, height=260)
        st.plotly_chart(fig_g, use_container_width=True)

    # ─────────────────────────────────────────────
    # ROW 3: Doctor Workload | Arrival Mode
    # ─────────────────────────────────────────────
    c7, c8 = st.columns([1.5, 1])

    with c7:
        fig_doc = px.bar(
            doc_counts.sort_values("patients", ascending=False).head(10),
            x="doctor_assigned", y="patients",
            title="Doctor Workload Distribution",
            color="patients",
            color_continuous_scale=[[0, "#003060"], [0.6, "#0077b6"], [1, "#ff6600"]],
        )
        fig_doc.update_layout(**PLOTLY_DARK_LAYOUT, xaxis_title="",
                              coloraxis_showscale=False, xaxis_tickangle=-30)
        st.plotly_chart(fig_doc, use_container_width=True)

    with c8:
        mode_cnt = df["arrival_mode"].value_counts().reset_index()
        mode_cnt.columns = ["Mode", "Count"]
        fig_mode = px.pie(
            mode_cnt, names="Mode", values="Count",
            hole=0.55, title="Arrival Mode Split",
            color_discrete_sequence=["#ff3355", "#00b4ff"],
        )
        fig_mode.update_layout(**PLOTLY_DARK_LAYOUT)
        st.plotly_chart(fig_mode, use_container_width=True)

    # ─────────────────────────────────────────────
    # ALERT TABLES
    # ─────────────────────────────────────────────
    st.markdown("---")
    a1, a2 = st.columns(2)

    TABLE_COLS = [
        "patient_code", "patient_name", "age", "gender",
        "triage_level", "Wait Display", "department",
        "Arrival (IST)", "symptoms", "arrival_mode", "Bed Status", "doctor_assigned"
    ]
    RENAME = {
        "patient_code": "ID", "patient_name": "Patient", "age": "Age",
        "gender": "Sex", "triage_level": "Triage", "department": "Dept",
        "symptoms": "Symptoms", "arrival_mode": "Mode",
        "doctor_assigned": "Doctor", "Wait Display": "Wait",
        "Arrival (IST)": "Time",
    }

    with a1:
        st.markdown("### 🚨 Critical Triage Alerts")
        if not critical_df.empty:
            st.dataframe(
                critical_df[TABLE_COLS].rename(columns=RENAME).head(12),
                use_container_width=True, height=300,
            )
        else:
            st.success("✅ No critical patients at this time.")

    with a2:
        st.markdown("### ⏳ Long Wait Alerts  *(> 60 min)*")
        if not long_wait_df.empty:
            st.dataframe(
                long_wait_df[TABLE_COLS].rename(columns=RENAME).head(12),
                use_container_width=True, height=300,
            )
        else:
            st.success("✅ All patients within acceptable wait times.")

    # ── Department Bottleneck ──
    st.markdown("### 🏢 Department Bottleneck Alerts")
    if not bottleneck_depts.empty:
        bott_cols = st.columns(len(bottleneck_depts))
        for i, (_, row) in enumerate(bottleneck_depts.iterrows()):
            dept_pct  = round(row["count"] / total_pts * 100, 1) if total_pts else 0
            col_hex   = "#ff3355" if dept_pct > 30 else ("#ffbb00" if dept_pct > 15 else "#00b4ff")
            bott_cols[i].markdown(f"""
            <div style="background:rgba(8,28,52,0.9);border:1px solid {col_hex};
                        border-radius:10px;padding:14px;text-align:center;
                        box-shadow:0 0 15px {col_hex}33;">
                <div style="font-family:'Rajdhani',sans-serif;font-size:0.7rem;
                            color:{col_hex};letter-spacing:0.15em;text-transform:uppercase;">
                    {row['department']}
                </div>
                <div style="font-family:'Share Tech Mono',monospace;font-size:2rem;
                            color:{col_hex};margin:4px 0;">{row['count']}</div>
                <div style="font-size:0.72rem;color:#3d6080;">
                    {dept_pct}% of active patients
                </div>
            </div>
            """, unsafe_allow_html=True)

    # ── Weather Spike Summary ──
    if w_sev >= 1:
        st.markdown("### 🌦 Weather Surge Impact Summary")
        st.markdown(f"""
        <div style="background:rgba(50,30,0,0.8);border:1px solid #ffbb00;
                    border-radius:10px;padding:16px 24px;
                    font-family:'Exo 2',sans-serif;font-size:0.9rem;line-height:1.8;
                    color:#e8c87a;">
            <b>Event:</b> {w_label} &nbsp;·&nbsp;
            <b>Temp:</b> {weather['temp']}°C &nbsp;·&nbsp;
            <b>Condition:</b> {weather['description']}<br>
            <b>Admission Rate Multiplier:</b> ×{w_multi:.1f} &nbsp;·&nbsp;
            <b>Admissions This Hour:</b> {admissions_hr} &nbsp;·&nbsp;
            <b>Forecast Next Hour:</b> ~{forecast_next}<br>
            <b>Recommendation:</b>
            {'Activate surge protocol – additional staff and beds required.' if w_sev >= 2
             else 'Monitor closely – mild increase in critical cases expected.'}
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Live Patient Feed ──
    st.markdown("### 📋 Live Patient Feed")
    with st.expander("Show full live feed", expanded=True):
        feed_df = df[TABLE_COLS].rename(columns=RENAME).head(30)
        st.dataframe(feed_df, use_container_width=True, height=420)

    # ── Export ──
    if export_btn:
        csv = df.drop(columns=["arrival_time"], errors="ignore").to_csv(index=False)
        st.download_button(
            label="📥 Download CSV",
            data=csv,
            file_name=f"er_patients_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
            mime="text/csv",
        )
        st.success("✅ Export ready!")

    # ─────────────────────────────────────────────
    # HOSPITAL PERFORMANCE SCORECARD
    # ─────────────────────────────────────────────
    st.markdown("---")
    st.markdown("### 🏆 Hospital Performance Scorecard")

    score_color = "#00ff88" if perf_score >= 70 else ("#ffbb00" if perf_score >= 40 else "#ff3355")
    score_label = "OPTIMAL" if perf_score >= 70 else ("MODERATE" if perf_score >= 40 else "CRITICAL")

    s1, s2, s3, s4, s5 = st.columns(5)
    for col, label, val, suffix in [
        (s1, "Occupancy Rate",  round(total_pts/TOTAL_BEDS*100, 1), "%"),
        (s2, "Avg Wait Time",   avg_wait,   " min"),
        (s3, "Critical Cases",  critical_cnt, ""),
        (s4, "Bed Utilization", f"{bed_occ_pct}", "%"),
        (s5, "Performance",     perf_score,  "/100"),
    ]:
        col.markdown(f"""
        <div style="background:rgba(8,28,52,0.9);border:1px solid rgba(0,180,255,0.2);
                    border-radius:10px;padding:16px;text-align:center;">
            <div style="font-family:'Rajdhani',sans-serif;font-size:0.68rem;
                        color:#3d6080;letter-spacing:0.15em;text-transform:uppercase;">
                {label}
            </div>
            <div style="font-family:'Share Tech Mono',monospace;font-size:1.9rem;
                        color:{score_color if label=='Performance' else '#00b4ff'};
                        margin:6px 0;">
                {val}{suffix}
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown(f"""
    <div style="text-align:center;margin-top:12px;
                font-family:'Rajdhani',sans-serif;font-size:1.05rem;
                color:{score_color};letter-spacing:0.15em;">
        HOSPITAL STATUS: <strong>{score_label}</strong>
    </div>
    """, unsafe_allow_html=True)

    # ── Footer ──
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(f"""
    <div style="text-align:center;font-family:'Share Tech Mono',monospace;
                font-size:0.65rem;color:#1a3a5c;letter-spacing:0.15em;padding:12px 0;">
        ER COMMAND CENTER   ·  AUTO-REFRESH 60s  ·  {now_ist}  ·  {HOSPITAL_BRANCH.upper()}
    </div>
    """, unsafe_allow_html=True)