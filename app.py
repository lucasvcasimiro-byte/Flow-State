import streamlit as st
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
from icalendar import Calendar
from datetime import datetime, time, timedelta
import pickle
import warnings
import json
import os
import hashlib
import math

warnings.filterwarnings('ignore')
st.set_page_config(page_title="FlowState Productivity", layout="wide", page_icon="⚡")
st.markdown('''
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
    html, body, [class*="css"]  { font-family: 'Inter', sans-serif; }
    .block-container { padding-top: 2rem; padding-bottom: 2rem; max-width: 1200px; }
    .stButton>button {
        background-color: #2563eb; color: white; border-radius: 6px;
        font-weight: 500; border: none; transition: all 0.2s;
    }
    .stButton>button:hover { background-color: #1d4ed8; color: white; }
    div[data-testid="stMetric"] {
        background-color: #ffffff; border-radius: 12px; padding: 1.25rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.06); border: 1px solid #e5e7eb;
    }
    .card-container {
        background: #ffffff; border-radius: 12px; padding: 1.5rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.06); border: 1px solid #e5e7eb; margin-bottom: 1.5rem;
    }
    .stAlert { border-radius: 8px !important; border: none !important; }
    .header-style { font-size: 2rem; font-weight: 700; color: #111827; margin-bottom: 0.25rem; }
    .subheader-style { font-size: 1rem; color: #6b7280; margin-bottom: 2rem; }
    /* Agenda */
    .agenda-card {
        border-left: 4px solid #3b82f6; background: #ffffff; border-radius: 8px;
        padding: 14px 16px; margin-bottom: 10px; box-shadow: 0 1px 3px rgba(0,0,0,0.08);
        border: 1px solid #e5e7eb;
    }
    .agenda-card.short { border-left-color: #10b981; }
    .agenda-card.long  { border-left-color: #ef4444; }
    .agenda-time  { font-weight: 600; color: #4b5563; font-size: 0.8rem; text-transform: uppercase; letter-spacing: 0.05em; }
    .agenda-title { font-weight: 600; color: #111827; font-size: 1rem; margin: 3px 0; }
    .agenda-duration { font-size: 0.82rem; color: #9ca3af; }
    .agenda-free {
        text-align: center; color: #9ca3af; padding: 10px 0; font-size: 0.88rem;
        border: 1px dashed #d1d5db; border-radius: 8px; margin: 10px 0; background: #f9fafb;
    }
    .agenda-focus-block {
        text-align: center; padding: 12px 16px; font-size: 0.92rem; font-weight: 700;
        border: 2px solid #10b981; border-radius: 10px; margin: 10px 0;
        background: linear-gradient(135deg, #f0fdf4, #dcfce7); color: #065f46;
        box-shadow: 0 2px 8px rgba(16,185,129,0.15);
    }
    /* Login */
    .login-card {
        background: #ffffff; border-radius: 16px; padding: 2.5rem 2rem;
        box-shadow: 0 20px 60px rgba(0,0,0,0.12); border: 1px solid #e5e7eb;
        max-width: 440px; margin: 0 auto;
    }
    .login-logo { font-size: 1.6rem; font-weight: 700; color: #111827; letter-spacing: -0.5px; margin-bottom: 0.25rem; }
    .login-tagline { font-size: 0.9rem; color: #6b7280; margin-bottom: 1.5rem; }
    /* Sidebar */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0f172a 0%, #1e293b 100%) !important;
    }
    section[data-testid="stSidebar"] * { color: #cbd5e1 !important; }
    section[data-testid="stSidebar"] .stRadio label { font-size: 0.9rem !important; font-weight: 500 !important; }
    section[data-testid="stSidebar"] hr { border-color: #334155 !important; }
    /* Badges */
    .badge-high   { background:#fee2e2; color:#b91c1c; padding:2px 10px; border-radius:20px; font-size:0.75rem; font-weight:600; }
    .badge-medium { background:#fef3c7; color:#92400e; padding:2px 10px; border-radius:20px; font-size:0.75rem; font-weight:600; }
    .badge-low    { background:#d1fae5; color:#065f46; padding:2px 10px; border-radius:20px; font-size:0.75rem; font-weight:600; }
    .badge-pending{ background:#eff6ff; color:#1d4ed8; padding:2px 10px; border-radius:20px; font-size:0.75rem; font-weight:600; }
    .badge-done   { background:#f0fdf4; color:#15803d; padding:2px 10px; border-radius:20px; font-size:0.75rem; font-weight:600; }
    /* Section header */
    .section-header {
        font-size: 1.4rem; font-weight: 700; color: #111827;
        border-bottom: 2px solid #e5e7eb; padding-bottom: 0.4rem; margin-bottom: 1.5rem;
    }
    /* KPI card */
    .kpi-card {
        background:#ffffff; border-radius:12px; padding:1.25rem 1.5rem;
        border:1px solid #e5e7eb; box-shadow:0 2px 8px rgba(0,0,0,0.05); transition: box-shadow 0.2s;
    }
    .kpi-card:hover { box-shadow:0 4px 16px rgba(0,0,0,0.1); }
    .kpi-label { font-size:0.75rem; font-weight:600; color:#6b7280; text-transform:uppercase; letter-spacing:0.05em; margin-bottom:0.35rem; }
    .kpi-value { font-size:1.75rem; font-weight:700; color:#111827; line-height:1; }
    .kpi-sub   { font-size:0.78rem; color:#9ca3af; margin-top:0.25rem; }
    /* Timer panel */
    .timer-panel {
        background: linear-gradient(135deg, #1e1b4b, #312e81);
        border-radius: 16px; padding: 1.5rem 2rem; margin-bottom: 1rem;
        box-shadow: 0 6px 24px rgba(99,102,241,0.3);
    }
    .timer-display {
        font-size: 3.2rem; font-weight: 800; color: #c7d2fe;
        font-family: 'Courier New', monospace; letter-spacing: 0.05em;
        text-align: center; margin: 0.4rem 0;
    }
    .timer-task-name { font-size: 1rem; font-weight: 600; color: #e0e7ff; text-align: center; margin-bottom: 0.3rem; }
    .timer-total     { font-size: 0.8rem; color: #a5b4fc; text-align: center; margin-top: 0.2rem; }
    /* Priority banner */
    .priority-banner {
        background: linear-gradient(135deg, #1e40af, #3b82f6);
        border-radius: 12px; padding: 1rem 1.5rem; margin-bottom: 1.25rem;
        box-shadow: 0 4px 15px rgba(59,130,246,0.3);
    }
    /* Task name */
    .task-name { font-size: 0.9rem; color: #374151; font-weight: 500; }
    .task-name.done { text-decoration: line-through; color: #9ca3af; }
</style>
''', unsafe_allow_html=True)

# ──────────────────────────────────────────────────────────────────────────────
# AUTH UTILITIES
# ──────────────────────────────────────────────────────────────────────────────
USER_FILE = 'user_data/users.json'

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def load_users():
    if not os.path.exists('user_data'):
        os.makedirs('user_data')
    if not os.path.exists(USER_FILE):
        return {}
    try:
        with open(USER_FILE, 'r') as f:
            content = f.read().strip()
            if not content:
                return {}
            return json.loads(content)
    except Exception:
        return {}

def save_users(users):
    with open(USER_FILE, 'w') as f:
        json.dump(users, f)

# ──────────────────────────────────────────────────────────────────────────────
# HELPER UTILITIES
# ──────────────────────────────────────────────────────────────────────────────
def fmt_seconds(s):
    """Format seconds into HH:MM:SS or MM:SS."""
    s = int(max(0, s))
    h = s // 3600
    m = (s % 3600) // 60
    sec = s % 60
    if h > 0:
        return f"{h:02d}:{m:02d}:{sec:02d}"
    return f"{m:02d}:{sec:02d}"

def generate_trend_data(base_val, days=7, noise=0.8, seed=42):
    """Generate a plausible simulated 7-day trend anchored to base_val on day 7."""
    rng = np.random.default_rng(seed)
    deltas = rng.normal(0, noise, days)
    cumulative = np.cumsum(deltas)
    trend = base_val + cumulative - cumulative[-1]
    return np.clip(trend, max(0.0, base_val - noise * 4), base_val + noise * 4)

# ──────────────────────────────────────────────────────────────────────────────
# LOGIN / SIGNUP
# ──────────────────────────────────────────────────────────────────────────────
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
if 'user_email' not in st.session_state:
    st.session_state['user_email'] = ""

if not st.session_state['logged_in']:
    st.markdown('<br><br>', unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 1.4, 1])
    with col2:
        st.markdown('''
        <div class="login-card">
            <div class="login-logo">⚡ FlowState</div>
            <div class="login-tagline">Your professional productivity workspace</div>
        </div>
        ''', unsafe_allow_html=True)
        st.markdown('<br>', unsafe_allow_html=True)
        tab1, tab2 = st.tabs(["Sign In", "Create Account"])
        with tab1:
            email    = st.text_input("Email address", key="login_email", placeholder="you@example.com")
            password = st.text_input("Password", type="password", key="login_pass", placeholder="••••••••")
            if st.button("Sign In", use_container_width=True, key="btn_login"):
                users = load_users()
                if email in users and users[email]['password'] == hash_password(password):
                    st.session_state['logged_in']  = True
                    st.session_state['user_email'] = email
                    st.rerun()
                else:
                    st.error("Incorrect email or password.")
        with tab2:
            new_email    = st.text_input("Email address", key="signup_email", placeholder="you@example.com")
            new_username = st.text_input("Username / Display Name", key="signup_username", placeholder="e.g. John Doe (optional)")
            new_password = st.text_input("Password", type="password", key="signup_pass", placeholder="Min. 6 characters")
            if st.button("Create Account", use_container_width=True, key="btn_signup"):
                users = load_users()
                if new_email in users:
                    st.error("An account with this email already exists.")
                elif not new_email or not new_password:
                    st.warning("Please fill in all fields.")
                elif len(new_password) < 6:
                    st.warning("Password must be at least 6 characters.")
                else:
                    users[new_email] = {
                        'password': hash_password(new_password),
                        'username': new_username.strip() if new_username.strip() else new_email.split('@')[0].split('.')[0].capitalize(),
                        'tasks': [],
                        'profile': {}
                    }
                    save_users(users)
                    st.success("Account created! Sign in to continue.")
    st.stop()

if not st.session_state['logged_in'] or not st.session_state['user_email']:
    st.warning("Please log in to continue.")
    st.stop()

users = load_users()
if st.session_state['user_email'] not in users:
    users[st.session_state['user_email']] = {
        'tasks': [], 'profile_name': None,
        'profile_result': {}, 'profile_inputs': {},
        'username': st.session_state['user_email'].split('@')[0].split('.')[0].capitalize()
    }
    save_users(users)

user_data = users[st.session_state['user_email']]

if 'username' not in user_data:
    user_data['username'] = st.session_state['user_email'].split('@')[0].split('.')[0].capitalize()
    users[st.session_state['user_email']] = user_data
    save_users(users)

display_username = user_data.get('username')
user_initials = (display_username[:2] if display_username else st.session_state['user_email'][:2]).upper()

# ──────────────────────────────────────────────────────────────────────────────
# SIDEBAR
# ──────────────────────────────────────────────────────────────────────────────
st.sidebar.markdown(f'''
    <div style="padding:1.2rem 0 0.5rem;">
        <div style="font-size:1.3rem;font-weight:700;color:#f1f5f9;letter-spacing:-0.5px;">⚡ FlowState</div>
        <div style="font-size:0.75rem;color:#64748b;margin-top:0.15rem;">Productivity Platform</div>
    </div>
    <hr style="border-color:#334155;margin:0.5rem 0 1rem;">
    <div style="display:flex;align-items:center;gap:10px;margin-bottom:1rem;">
        <div style="background:linear-gradient(135deg,#6366f1,#8b5cf6);border-radius:50%;width:32px;height:32px;
                    display:flex;align-items:center;justify-content:center;color:#fff;font-weight:700;font-size:0.8rem;flex-shrink:0;">{user_initials}</div>
        <div>
            <div style="font-size:0.82rem;color:#e2e8f0;font-weight:600;word-break:break-all;">{display_username}</div>
            <div style="font-size:0.72rem;color:#94a3b8;">{st.session_state['user_email']}</div>
        </div>
    </div>
''', unsafe_allow_html=True)

menu = st.sidebar.radio(
    "Navigation",
    ["Dashboard", "Task Prioritization", "Calendar Analyzer", "Wearable & Recovery", "Profile Insights"],
    label_visibility="collapsed"
)

if menu == "Profile Insights":
    st.sidebar.markdown("---")
    st.sidebar.markdown("**Model Settings**")
    n_clusters_choice = st.sidebar.radio("Clusters:", options=[3, 4], index=0,
                                          help="Choose between 3 or 4 clusters")

st.sidebar.markdown("---")
with st.sidebar.expander("⚙️ Account Settings"):
    new_name = st.text_input("Change Display Name", value=display_username, key="change_display_name_input")
    if st.button("Save Name", key="save_display_name_btn", use_container_width=True):
        if new_name.strip():
            users = load_users()
            users[st.session_state['user_email']]['username'] = new_name.strip()
            save_users(users)
            st.success("Name updated!")
            st.rerun()

if st.sidebar.button("Sign Out", use_container_width=True):
    st.session_state['logged_in']  = False
    st.session_state['user_email'] = ""
    st.rerun()

# ──────────────────────────────────────────────────────────────────────────────
# MODEL & DATA LOADING
# ──────────────────────────────────────────────────────────────────────────────
@st.cache_resource
def load_model_data():
    with open('final_app_model.pkl', 'rb') as f:
        return pickle.load(f)

model_data = load_model_data()

cluster_features = model_data.get('features', [
    'work_hours', 'meetings_count', 'breaks_taken',
    'after_hours_work', 'app_switches', 'sleep_hours', 'task_completion',
    'isolation_index', 'fatigue_score', 'burnout_score'
])

df = model_data.get('data')
if df is None:
    df = pd.read_csv('wfh_burnout_dataset.csv')

scaler = model_data['scaler']
kmeans = model_data['kmeans']

# ──────────────────────────────────────────────────────────────────────────────
# CLUSTERING UTILITIES
# ──────────────────────────────────────────────────────────────────────────────
@st.cache_data
def get_cluster_info(_scaler, _kmeans, data, features, n_clusters=3):
    scaled_data = _scaler.transform(data[features])
    if _kmeans.n_clusters != n_clusters:
        dynamic_kmeans = KMeans(n_clusters=n_clusters, random_state=42)
        dynamic_kmeans.fit(scaled_data)
        labels    = dynamic_kmeans.predict(scaled_data)
        centroids = _scaler.inverse_transform(dynamic_kmeans.cluster_centers_)
        used_kmeans = dynamic_kmeans
    else:
        labels    = _kmeans.predict(scaled_data)
        centroids = _scaler.inverse_transform(_kmeans.cluster_centers_)
        used_kmeans = _kmeans

    centroid_df = pd.DataFrame(centroids, columns=features)

    cluster_scores = []
    for i in range(n_clusters):
        work    = centroid_df.loc[i, 'work_hours']
        sleep   = centroid_df.loc[i, 'sleep_hours']
        fatigue = centroid_df.loc[i, 'fatigue_score']
        score   = (fatigue * 2) + (work * 1.5) - (sleep * 1)
        cluster_scores.append((i, work, sleep, fatigue, score))

    cluster_scores.sort(key=lambda x: x[4], reverse=True)
    cluster_profiles  = {}
    assigned_profiles = set()

    for rank, (idx, work, sleep, fatigue, score) in enumerate(cluster_scores):
        if fatigue > 6.5 and work > 9 and "Overworked" not in assigned_profiles:
            name = "The Overworked & Exhausted"
            assigned_profiles.add("Overworked")
            sugg = """🚨 **Status Review:** You are pushing dangerous hours and experiencing high fatigue. Immediate action is needed.

📅 **6-Month Improvement Plan:**
* **Months 1-2:** **Establish Boundaries.** Set a hard stop at 8 working hours. No after-hours emails. Start practicing a 30-minute wind-down routine before sleep without screens.
* **Months 3-4:** **Rebalance & Delegate.** Target consistent 7.5+ hour sleep schedules. Begin taking 10-minute micro-breaks every 90 minutes of work.
* **Months 5-6:** **Sustainable Rhythm.** Your fatigue should be dropping. Reintroduce a hobby or daily exercise. Maintain strict barriers between 'home' space and 'work' space to permanently lower burnout risk."""

        elif work > 9 and fatigue <= 6.5 and "HighAchiever" not in assigned_profiles:
            name = "The High-Achiever"
            assigned_profiles.add("HighAchiever")
            sugg = """🔥 **Status Review:** You are working long hours but somehow managing the fatigue—for now. This phase is often the precursor to sudden burnout.

📅 **6-Month Improvement Plan:**
* **Months 1-2:** **Strategic Pullback.** Reduce meetings by 20%. Aim to shave 1 hour off your workday by prioritizing high-impact tasks.
* **Months 3-4:** **Active Recovery.** Schedule a mandatory 45-minute lunch away from the desk.
* **Months 5-6:** **Efficiency over Volume.** Reduce work hours to 8.5/day. Focus on task completion rates rather than time spent."""

        elif fatigue < 5 and sleep > 7 and "Balanced" not in assigned_profiles:
            name = "The Balanced Worker"
            assigned_profiles.add("Balanced")
            sugg = """✅ **Status Review:** Excellent! You maintain a strong functional balance between rest and work without sacrificing health.

📅 **6-Month Improvement Plan:**
* **Months 1-2:** **Solidify Routine.** Ensure your current sleep/work schedule is protected from creeping meeting hours.
* **Months 3-4:** **Optimize Focus.** Try batching your tasks to avoid app-switching fatigue, aiming for "deep work" blocks of 2 hours.
* **Months 5-6:** **Prevent Stagnation.** Pick up a low-stress learning opportunity or mentor someone else on how to achieve this balance!"""

        elif sleep < 6.5 and work <= 9 and "SleepDeprived" not in assigned_profiles:
            name = "The Sleep-Deprived"
            assigned_profiles.add("SleepDeprived")
            sugg = """🛌 **Status Review:** While your work hours are manageable, your sleep duration is unhealthy. This limits your recovery and fuels background fatigue.

📅 **6-Month Improvement Plan:**
* **Months 1-2:** **Sleep Hygiene.** Move all screens out of the bedroom. Go to bed 15 minutes earlier every week until you hit a 7-8 hour window.
* **Months 3-4:** **Morning Optimization.** Use mornings for 20 minutes of natural sunlight to reset your circadian rhythm.
* **Months 5-6:** **Performance Review.** As sleep stabilizes, you should notice sharper focus and faster task completion."""

        else:
            if work > 8 and sleep < 7:
                name = "The Stretched Performer"
                sugg = """⚙️ **Status Review:** You are managing reasonable work hours but with insufficient rest. Long-term sustainability is at risk.

📅 **6-Month Improvement Plan:**
* **Months 1-2:** **Recovery Priority.** Aim to add 30-45 minutes of sleep per night by creating a strict bedtime.
* **Months 3-4:** **Workload Audit.** Reduce your work time by 30 minutes/day by eliminating low-impact activities.
* **Months 5-6:** **New Baseline.** With better sleep and refined work focus, you should feel substantially more energized."""
            elif sleep >= 7 and work > 8:
                name = "The Driven & Rested"
                sugg = """⭐ **Status Review:** You have solid sleep habits while maintaining a robust work schedule—a rare and healthy combination.

📅 **6-Month Improvement Plan:**
* **Months 1-2:** **Protect Your Sleep.** No work past 7 PM on weekdays.
* **Months 3-4:** **Work Quality Focus.** Aim for 5-6 high-impact tasks daily instead of dozens of small ones.
* **Months 5-6:** **Mentor Others.** Help colleagues achieve this balance by sharing your strategies."""
            elif fatigue > 5 and work <= 8:
                name = "The Slow Burn"
                sugg = """🔥 **Status Review:** Even with moderate hours, you're experiencing creeping fatigue. This often signals inefficiency or stress accumulation.

📅 **6-Month Improvement Plan:**
* **Months 1-2:** **Energy Audit.** Track which meetings, people, or tasks drain you most.
* **Months 3-4:** **Boundary Setting.** Eliminate after-hours email checks. Start a 15-minute daily walk.
* **Months 5-6:** **Efficiency Boost.** With triggers identified and boundaries set, your fatigue should subside."""
            else:
                name = "The Moderate / Undefined"
                sugg = """☕ **Status Review:** You fall into a middle-ground pattern. There is room to optimize your daily energy.

📅 **6-Month Improvement Plan:**
* **Months 1-2:** **Audit Your Days.** Spend 2 weeks tracking what exactly makes you tired.
* **Months 3-4:** **Introduce Rhythm.** Adopt the Pomodoro technique (25 mins work, 5 mins rest).
* **Months 5-6:** **Targeted Adjustment.** Focus either on raising your sleep by 30 minutes or dropping daily working hours by 45 minutes."""

        cluster_profiles[idx] = {"name": f"Type {idx}: {name}", "suggestion": sugg}

    return labels, centroid_df, cluster_profiles, used_kmeans


def perform_clustering(data, features, n_clusters):
    labels, centroid_df, profiles, used_kmeans = get_cluster_info(scaler, kmeans, data, features, n_clusters)
    return scaler, used_kmeans, labels, centroid_df, profiles


# ══════════════════════════════════════════════════════════════════════════════
# DASHBOARD
# ══════════════════════════════════════════════════════════════════════════════
if menu == "Dashboard":
    all_tasks     = user_data.get('tasks', [])
    pending_tasks = [t for t in all_tasks if t['status'] == 'Pending']
    done_tasks    = [t for t in all_tasks if t['status'] == 'Completed']
    high_tasks    = [t for t in pending_tasks if t['priority'] == 'High']
    profile_result = user_data.get('profile_result', {})
    profile_inputs = user_data.get('profile_inputs', {})
    profile_name   = user_data.get('profile_name', None)

    greeting_hour = datetime.now().hour
    greeting = "Good morning" if greeting_hour < 12 else ("Good afternoon" if greeting_hour < 18 else "Good evening")
    user_first = user_data.get('username', st.session_state['user_email'].split('@')[0].split('.')[0].capitalize())

    st.markdown(f'<div class="header-style">{greeting}, {user_first}</div>', unsafe_allow_html=True)
    st.markdown('<div class="subheader-style">Here is your productivity snapshot for today.</div>', unsafe_allow_html=True)

    # ── Today's Top Priority Banner ──────────────────────────────────────────
    if high_tasks:
        top_task = high_tasks[0]
        st.markdown(f'''
        <div class="priority-banner" style="display:flex;align-items:center;gap:1rem;">
            <div style="font-size:1.8rem;">🎯</div>
            <div>
                <div style="font-size:0.7rem;font-weight:700;color:#bfdbfe;text-transform:uppercase;letter-spacing:0.1em;">Today\'s Top Priority</div>
                <div style="font-size:1.05rem;font-weight:700;color:#ffffff;margin-top:2px;">{top_task['name']}</div>
                <div style="font-size:0.75rem;color:#93c5fd;margin-top:2px;">High priority · {len(high_tasks)} high-priority task{'s' if len(high_tasks) > 1 else ''} remaining</div>
            </div>
        </div>''', unsafe_allow_html=True)

    # ── Day / Week Toggle ────────────────────────────────────────────────────
    if 'dash_view' not in st.session_state:
        st.session_state['dash_view'] = 'Today'
    tog1, tog2, _ = st.columns([1, 1, 6])
    with tog1:
        if st.button("📅 Today", use_container_width=True, key="dash_today_btn"):
            st.session_state['dash_view'] = 'Today'
    with tog2:
        if st.button("📊 This Week", use_container_width=True, key="dash_week_btn"):
            st.session_state['dash_view'] = 'This Week'
    st.markdown("<br>", unsafe_allow_html=True)

    # ── KPI strip ────────────────────────────────────────────────────────────
    pct = round(len(done_tasks) / max(1, len(all_tasks)) * 100)
    total_focused = sum(t.get('focused_seconds', 0) for t in all_tasks)
    focused_label = fmt_seconds(total_focused) if total_focused > 0 else "—"

    def mini_kpi(label, value, sub, accent="#2563eb"):
        return f'''<div style="background:#fff;border-radius:12px;padding:1.1rem 1.25rem;
                   border:1px solid #e5e7eb;box-shadow:0 2px 6px rgba(0,0,0,0.04);">
            <div style="font-size:0.7rem;font-weight:700;color:#6b7280;text-transform:uppercase;
                        letter-spacing:0.06em;margin-bottom:0.35rem;">{label}</div>
            <div style="font-size:1.7rem;font-weight:800;color:{accent};line-height:1;">{value}</div>
            <div style="font-size:0.75rem;color:#9ca3af;margin-top:0.2rem;">{sub}</div>
        </div>'''

    if st.session_state['dash_view'] == 'Today':
        k1, k2, k3, k4 = st.columns(4)
        with k1: st.markdown(mini_kpi("Pending Tasks",   len(pending_tasks), f"{len(high_tasks)} high priority", "#2563eb"), unsafe_allow_html=True)
        with k2: st.markdown(mini_kpi("Completed",       len(done_tasks),    f"of {len(all_tasks)} total",       "#10b981"), unsafe_allow_html=True)
        with k3: st.markdown(mini_kpi("Completion Rate", f"{pct}%",          "tasks resolved",                   "#6366f1"), unsafe_allow_html=True)
        with k4: st.markdown(mini_kpi("Focus Time",      focused_label,      "total tracked time",               "#f59e0b"), unsafe_allow_html=True)
    else:
        focus_sessions = sum(1 for t in all_tasks if t.get('focused_seconds', 0) > 0)
        k1, k2, k3, k4 = st.columns(4)
        with k1: st.markdown(mini_kpi("Total Tasks",    len(all_tasks),  "all time",               "#2563eb"), unsafe_allow_html=True)
        with k2: st.markdown(mini_kpi("Completed",      len(done_tasks), f"{pct}% completion rate","#10b981"), unsafe_allow_html=True)
        with k3: st.markdown(mini_kpi("Focus Sessions", focus_sessions,  "tasks with tracked time","#6366f1"), unsafe_allow_html=True)
        with k4:
            conf = profile_result.get('confidence', None)
            conf_str = f"{conf:.0f}% match" if conf else "Not analysed"
            st.markdown(mini_kpi("Profile Confidence", conf_str, profile_name or "Run Profile Insights", "#f59e0b"), unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Load calendar events ─────────────────────────────────────────────────
    active_events = []
    if 'calendar_events' in st.session_state and st.session_state['calendar_events']:
        active_events = st.session_state['calendar_events']
    else:
        saved_events = user_data.get('calendar_events', [])
        if saved_events:
            loaded_events = []
            for ev in saved_events:
                loaded_events.append({
                    'Event': ev['Event'],
                    'Start': datetime.fromisoformat(ev['Start']),
                    'End':   datetime.fromisoformat(ev['End']),
                    'Duration (mins)': ev['Duration (mins)'],
                    'Date':  datetime.fromisoformat(ev['Date']).date()
                })
            st.session_state['calendar_events']  = loaded_events
            st.session_state['calendar_filename'] = user_data.get('calendar_filename', "Saved Calendar.ics")
            active_events = loaded_events

    has_calendar = len(active_events) > 0
    if has_calendar:
        event_df = pd.DataFrame(active_events).sort_values('Start').reset_index(drop=True)
        dates    = event_df['Date'].unique()
        num_days = len(dates)
        _pst = time(9, 0); _elt = time(17, 0)
        large_blocks_count = 0; total_free_mins = 0
        for d in dates:
            day_evs = event_df[event_df['Date'] == d].sort_values('Start')
            d_start = datetime.combine(d, _pst); d_end = datetime.combine(d, _elt)
            last_e  = d_start
            for _, row in day_evs.iterrows():
                ev_s = max(d_start, row['Start']); ev_e = min(d_end, row['End'])
                if ev_s > ev_e: ev_s, ev_e = ev_e, ev_s
                if ev_s > last_e:
                    gap = (ev_s - last_e).total_seconds() / 60.0
                    total_free_mins += gap
                    if gap >= 60: large_blocks_count += 1
                last_e = max(last_e, ev_e)
            if last_e < d_end:
                gap = (d_end - last_e).total_seconds() / 60.0
                total_free_mins += gap
                if gap >= 60: large_blocks_count += 1
        focus_score      = round(min(10.0, (large_blocks_count / max(1, num_days)) * 3), 1)
        meetings_per_day = event_df.groupby('Date').size()
        busiest_day_str  = meetings_per_day.idxmax().strftime('%a')
        free_blocks_str  = f"{large_blocks_count} blocks"
        late_cnt         = len(event_df[event_df['End'].dt.time > _elt])
        late_meetings_str= f"{late_cnt} meetings"
        cal_status_txt   = "Active"; cal_status_bg = "#dcfce7"; cal_status_color = "#15803d"
        cal_desc = f"Analyzing <b>{st.session_state.get('calendar_filename','Saved Calendar')}</b> with {len(event_df)} events this week."
    else:
        focus_score = "—"; busiest_day_str = "—"; free_blocks_str = "—"; late_meetings_str = "—"
        cal_status_txt = "Upload to activate"; cal_status_bg = "#eff6ff"; cal_status_color = "#2563eb"
        cal_desc = "Upload your <strong>.ics calendar file</strong> to unlock your weekly schedule analysis, focus block scoring, meeting load, and daily recommendations."

    # ── Three panels ─────────────────────────────────────────────────────────
    p1, p2, p3 = st.columns(3)

    with p1:
        has_profile = bool(profile_result)
        accent = "#6366f1"
        if has_profile:
            pname  = profile_result.get('profile_name', 'Unknown')
            pconf  = profile_result.get('confidence', 0)
            p_work = profile_inputs.get('work_hours', '—')
            p_slp  = profile_inputs.get('sleep_hours', '—')
            p_fat  = profile_inputs.get('fatigue_score', '—')
            if "Overworked" in pname:      desc, status_col, status_txt = "High workload + fatigue pattern detected.", "#ef4444", "At Risk"
            elif "Balanced" in pname:      desc, status_col, status_txt = "Healthy work-life equilibrium maintained.", "#10b981", "Optimal"
            elif "Sleep" in pname:         desc, status_col, status_txt = "Sleep deprivation affecting recovery.",      "#f59e0b", "Watch"
            elif "High-Achiever" in pname: desc, status_col, status_txt = "High output — monitor burnout risk.",        "#f59e0b", "Caution"
            else:                          desc, status_col, status_txt = "Mixed patterns — room to optimise.",         "#9ca3af", "Moderate"
            st.markdown(f'''
            <div style="background:#fff;border-radius:14px;padding:1.5rem;border:1px solid #e5e7eb;
                        box-shadow:0 2px 8px rgba(0,0,0,0.05);height:100%;">
                <div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:1rem;">
                    <div style="font-size:0.72rem;font-weight:700;color:#6b7280;text-transform:uppercase;letter-spacing:0.07em;">Work Profile</div>
                    <span style="background:{status_col}20;color:{status_col};font-size:0.7rem;font-weight:700;padding:2px 10px;border-radius:20px;">{status_txt}</span>
                </div>
                <div style="font-size:1.05rem;font-weight:700;color:#111827;margin-bottom:0.4rem;border-left:3px solid {accent};padding-left:0.6rem;">{pname}</div>
                <div style="font-size:0.82rem;color:#6b7280;margin-bottom:1.1rem;">{desc}</div>
                <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:8px;margin-bottom:1rem;">
                    <div style="background:#f8fafc;border-radius:8px;padding:0.5rem;text-align:center;">
                        <div style="font-size:1rem;font-weight:700;color:#111827;">{p_work}h</div>
                        <div style="font-size:0.65rem;color:#9ca3af;">Work</div>
                    </div>
                    <div style="background:#f8fafc;border-radius:8px;padding:0.5rem;text-align:center;">
                        <div style="font-size:1rem;font-weight:700;color:#111827;">{p_slp}h</div>
                        <div style="font-size:0.65rem;color:#9ca3af;">Sleep</div>
                    </div>
                    <div style="background:#f8fafc;border-radius:8px;padding:0.5rem;text-align:center;">
                        <div style="font-size:1rem;font-weight:700;color:#111827;">{p_fat}/10</div>
                        <div style="font-size:0.65rem;color:#9ca3af;">Fatigue</div>
                    </div>
                </div>
                <div style="font-size:0.75rem;color:#9ca3af;">Match confidence: <strong style="color:{accent};">{pconf:.0f}%</strong> &nbsp;·&nbsp; ML clustering model (K=3)</div>
            </div>''', unsafe_allow_html=True)
        else:
            st.markdown(f'''
            <div style="background:#fff;border-radius:14px;padding:1.5rem;border:1px solid #e5e7eb;
                        box-shadow:0 2px 8px rgba(0,0,0,0.05);height:100%;">
                <div style="font-size:0.72rem;font-weight:700;color:#6b7280;text-transform:uppercase;letter-spacing:0.07em;margin-bottom:1rem;">Work Profile</div>
                <div style="color:#9ca3af;font-size:0.9rem;margin-bottom:0.75rem;">No profile analysed yet.</div>
                <div style="font-size:0.82rem;color:#6b7280;">Go to <strong>Profile Insights → Discover Your Person Type</strong> and click Analyze My Habits to get your ML-matched work profile.</div>
            </div>''', unsafe_allow_html=True)

    with p2:
        st.markdown(f'''
        <div style="background:#fff;border-radius:14px;padding:1.5rem;border:1px solid #e5e7eb;
                    box-shadow:0 2px 8px rgba(0,0,0,0.05);height:100%;">
            <div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:1rem;">
                <div style="font-size:0.72rem;font-weight:700;color:#6b7280;text-transform:uppercase;letter-spacing:0.07em;">Calendar Analyzer</div>
                <span style="background:{cal_status_bg};color:{cal_status_color};font-size:0.7rem;font-weight:700;padding:2px 10px;border-radius:20px;">{cal_status_txt}</span>
            </div>
            <div style="font-size:1rem;font-weight:600;color:#111827;margin-bottom:0.5rem;">Schedule Health Overview</div>
            <div style="font-size:0.82rem;color:#6b7280;margin-bottom:1.1rem;min-height:3.6rem;line-height:1.4;">{cal_desc}</div>
            <div style="display:grid;grid-template-columns:1fr 1fr;gap:8px;margin-bottom:1rem;">
                <div style="background:#eff6ff;border-radius:8px;padding:0.6rem;text-align:center;">
                    <div style="font-size:0.8rem;font-weight:700;color:#1d4ed8;">Focus Score</div>
                    <div style="font-size:0.9rem;font-weight:800;color:#1e3a8a;margin-top:0.25rem;">{focus_score}{' / 10' if has_calendar else ''}</div>
                </div>
                <div style="background:#eff6ff;border-radius:8px;padding:0.6rem;text-align:center;">
                    <div style="font-size:0.8rem;font-weight:700;color:#1d4ed8;">Busiest Day</div>
                    <div style="font-size:0.9rem;font-weight:800;color:#1e3a8a;margin-top:0.25rem;">{busiest_day_str}</div>
                </div>
                <div style="background:#eff6ff;border-radius:8px;padding:0.6rem;text-align:center;">
                    <div style="font-size:0.8rem;font-weight:700;color:#1d4ed8;">Free Blocks</div>
                    <div style="font-size:0.9rem;font-weight:800;color:#1e3a8a;margin-top:0.25rem;">{free_blocks_str}</div>
                </div>
                <div style="background:#eff6ff;border-radius:8px;padding:0.6rem;text-align:center;">
                    <div style="font-size:0.8rem;font-weight:700;color:#1d4ed8;">Late Meetings</div>
                    <div style="font-size:0.9rem;font-weight:800;color:#1e3a8a;margin-top:0.25rem;">{late_meetings_str}</div>
                </div>
            </div>
            <div style="font-size:0.75rem;color:#9ca3af;">Navigate to <strong>Calendar Analyzer</strong> to upload and analyse your schedule.</div>
        </div>''', unsafe_allow_html=True)

    with p3:
        snap = user_data.get('wearable_snapshot', {})
        w_prev_sleep   = snap.get('sleep',   6.5)
        w_prev_fatigue = snap.get('fatigue', 7)
        w_prev_stress  = snap.get('stress',  6.2)
        w_prev_steps   = snap.get('steps',   4200)
        snap_date      = snap.get('date', None)
        _sl = max(0, min(100, (w_prev_sleep  - 4) * 25))
        _st = max(0, min(100, (10 - w_prev_stress) * 10))
        _ft = max(0, min(100, (10 - w_prev_fatigue) * 11.1))
        _ac = max(0, min(100, w_prev_steps / 100))
        _rs = round(_sl * 0.40 + _st * 0.25 + _ft * 0.25 + _ac * 0.10)
        if   _rs >= 67: _rl, _rc = "Optimal",  "#10b981"
        elif _rs >= 34: _rl, _rc = "Moderate", "#f59e0b"
        else:           _rl, _rc = "Low",       "#ef4444"

        def small_metric(icon, label, val, col="#374151"):
            return f'''<div style="display:flex;align-items:center;gap:8px;padding:0.5rem 0;border-bottom:1px solid #f3f4f6;">
                <span style="font-size:1rem;">{icon}</span>
                <span style="font-size:0.82rem;color:#6b7280;flex:1;">{label}</span>
                <span style="font-size:0.88rem;font-weight:700;color:{col};">{val}</span>
            </div>'''

        s_label = "Low" if w_prev_stress < 3.4 else ("Medium" if w_prev_stress < 6.7 else "High")
        s_col   = "#10b981" if w_prev_stress < 3.4 else ("#f59e0b" if w_prev_stress < 6.7 else "#ef4444")
        rows = (
            small_metric("🌙", "Sleep",          f"{w_prev_sleep}h",     "#6366f1" if w_prev_sleep >= 7 else "#ef4444") +
            small_metric("🔋", "Morning Fatigue", f"{w_prev_fatigue}/10", "#ef4444" if w_prev_fatigue >= 7 else "#10b981") +
            small_metric("🧘", "Stress",          s_label,                s_col) +
            small_metric("👟", "Steps",           f"{w_prev_steps:,}",    "#10b981" if w_prev_steps >= 5000 else "#f59e0b")
        )
        snap_note = f"Last updated: {snap_date}" if snap_date else "Based on default values — update in Wearable & Recovery."
        st.markdown(f'''
        <div style="background:#fff;border-radius:14px;padding:1.5rem;border:1px solid #e5e7eb;
                    box-shadow:0 2px 8px rgba(0,0,0,0.05);height:100%;">
            <div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:1rem;">
                <div style="font-size:0.72rem;font-weight:700;color:#6b7280;text-transform:uppercase;letter-spacing:0.07em;">Wearable & Recovery</div>
                <span style="background:{_rc}20;color:{_rc};font-size:0.7rem;font-weight:700;padding:2px 10px;border-radius:20px;">{_rl}</span>
            </div>
            <div style="display:flex;align-items:baseline;gap:10px;margin-bottom:0.25rem;">
                <div style="font-size:2.5rem;font-weight:800;color:{_rc};line-height:1;">{_rs}</div>
                <div style="font-size:0.82rem;color:#9ca3af;">/ 100 recovery score</div>
            </div>
            <div style="font-size:0.78rem;color:#9ca3af;margin-bottom:1rem;">{snap_note}</div>
            {rows}
            <div style="font-size:0.75rem;color:#9ca3af;margin-top:0.75rem;">Navigate to <strong>Wearable & Recovery</strong> to adjust your inputs.</div>
        </div>''', unsafe_allow_html=True)

    # ── 7-Day Trend Sparklines ────────────────────────────────────────────────
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div class="section-header">📈 7-Day Performance Trends</div>', unsafe_allow_html=True)

    cur_fatigue    = snap.get('fatigue', 7)
    cur_sleep      = snap.get('sleep',   6.5)
    cur_focus      = float(focus_score) if has_calendar and isinstance(focus_score, (int, float)) else 5.0
    cur_completion = pct
    days_labels    = [(datetime.now() - timedelta(days=6 - i)).strftime('%a') for i in range(7)]

    trend_focus      = generate_trend_data(cur_focus,      7, 0.8, seed=1)
    trend_completion = generate_trend_data(cur_completion, 7, 5.0, seed=2)
    trend_fatigue    = generate_trend_data(cur_fatigue,    7, 0.7, seed=3)
    trend_sleep      = generate_trend_data(cur_sleep,      7, 0.4, seed=4)

    fig_t, axes_t = plt.subplots(1, 4, figsize=(14, 2.8))
    fig_t.patch.set_facecolor('#f8fafc')
    trend_configs = [
        (trend_focus,      "Focus Score",       "#3b82f6", (0,  10)),
        (trend_completion, "Completion Rate %", "#10b981", (0, 100)),
        (trend_fatigue,    "Fatigue (1–10)",    "#ef4444", (1,  10)),
        (trend_sleep,      "Sleep (hrs)",       "#6366f1", (4,  10)),
    ]
    for ax, (data, title, color, ylim) in zip(axes_t, trend_configs):
        ax.set_facecolor('#ffffff')
        ax.fill_between(range(7), data, alpha=0.15, color=color)
        ax.plot(range(7), data, color=color, linewidth=2.5, marker='o', markersize=4)
        ax.plot(6, data[-1], 'o', color=color, markersize=8, zorder=5)
        ax.set_xticks(range(7)); ax.set_xticklabels(days_labels, fontsize=7.5, color='#6b7280')
        ax.set_ylim(ylim)
        ax.set_title(title, fontsize=9, fontweight='600', color='#374151', pad=6)
        ax.tick_params(axis='y', labelsize=7.5, colors='#9ca3af')
        ax.spines[['top', 'right', 'left']].set_visible(False)
        ax.spines['bottom'].set_color('#e5e7eb')
        ax.grid(axis='y', color='#f3f4f6', linewidth=0.8)
        ax.annotate(f"{data[-1]:.1f}", xy=(6, data[-1]), xytext=(4, 6),
                    textcoords='offset points', fontsize=8, fontweight='700', color=color)
    plt.tight_layout(pad=1.5)
    st.pyplot(fig_t)
    st.caption("📊 Trend data is simulated around your current metrics to illustrate how daily tracking would look in a production deployment.")

    # ── Pending Tasks strip ───────────────────────────────────────────────────
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div class="section-header">Pending Tasks</div>', unsafe_allow_html=True)
    if pending_tasks:
        t_cols = st.columns(2)
        half = (len(pending_tasks[:6]) + 1) // 2
        for idx, t in enumerate(pending_tasks[:6]):
            badge_cls   = f"badge-{t['priority'].lower()}"
            focused_sec = t.get('focused_seconds', 0)
            focused_str = f" · ⏱ {fmt_seconds(focused_sec)}" if focused_sec > 0 else ""
            with t_cols[0 if idx < half else 1]:
                st.markdown(f'''
                <div style="display:flex;align-items:center;gap:8px;padding:0.5rem 0;border-bottom:1px solid #f3f4f6;">
                    <span class="task-name" style="flex:1;">{t['name']}</span>
                    <span class="{badge_cls}">{t['priority']}</span>
                    <span style="font-size:0.75rem;color:#9ca3af;">{focused_str}</span>
                </div>''', unsafe_allow_html=True)
        if len(pending_tasks) > 6:
            st.caption(f"+{len(pending_tasks)-6} more — open Task Prioritization to view all.")
    else:
        st.success("All tasks are complete.")


# ══════════════════════════════════════════════════════════════════════════════
# TASK PRIORITIZATION + FOCUSED TASK TIMER
# ══════════════════════════════════════════════════════════════════════════════
elif menu == "Task Prioritization":
    st.markdown('<div class="header-style">Task Prioritization</div>', unsafe_allow_html=True)
    st.markdown('<div class="subheader-style">Manage your priorities, track focused work time, and eliminate the noise.</div>', unsafe_allow_html=True)

    # ── Timer session state ──────────────────────────────────────────────────
    for key, default in [('timer_running', False), ('timer_task_idx', None), ('timer_session_start', None)]:
        if key not in st.session_state:
            st.session_state[key] = default

    # ── Migrate old tasks to support new fields ──────────────────────────────
    users     = load_users()
    user_data = users[st.session_state['user_email']]
    changed   = False
    for t in user_data.get('tasks', []):
        if 'focused_seconds' not in t:  t['focused_seconds']  = 0;    changed = True
        if 'timer_started_at' not in t: t['timer_started_at'] = None; changed = True
    if changed:
        save_users(users)

    # ── Add Task ─────────────────────────────────────────────────────────────
    st.markdown('<div class="card-container">', unsafe_allow_html=True)
    with st.form("add_task_form"):
        col1, col2, col3 = st.columns([3, 1, 1])
        with col1:
            task_name = st.text_input("Task description", placeholder="e.g. Finish ML report...")
        with col2:
            priority = st.selectbox("Priority", ["High", "Medium", "Low"])
        with col3:
            st.markdown("<br>", unsafe_allow_html=True)
            add_task = st.form_submit_button("Add Task", use_container_width=True)
        if add_task and task_name:
            users     = load_users()
            user_data = users[st.session_state['user_email']]
            user_data.setdefault('tasks', []).append({
                "name": task_name, "priority": priority,
                "status": "Pending", "focused_seconds": 0, "timer_started_at": None
            })
            save_users(users)
            st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

    # ── Reload fresh state ───────────────────────────────────────────────────
    users     = load_users()
    user_data = users[st.session_state['user_email']]
    all_tasks = user_data.get('tasks', [])
    pending   = [t for t in all_tasks if t['status'] == 'Pending']

    # ══ FOCUSED TASK TIMER ═══════════════════════════════════════════════════
    st.markdown('<div class="section-header">⏱ Focused Task Timer</div>', unsafe_allow_html=True)

    if not pending:
        st.info("Add pending tasks above to start tracking your focused work time.")
    else:
        # Calendar best focus block suggestion
        cal_evs_now = st.session_state.get('calendar_events', [])
        if cal_evs_now:
            today = datetime.now().date()
            today_evs = sorted([e for e in cal_evs_now if e['Date'] == today], key=lambda x: x['Start'])
            pref_s = datetime.combine(today, time(9, 0))
            pref_e = datetime.combine(today, time(17, 0))
            best_gap = 0; best_s = None; best_e = None
            last_e_cal = pref_s
            for ev in today_evs:
                ev_s = max(pref_s, ev['Start']); ev_e = min(pref_e, ev['End'])
                if ev_s > last_e_cal:
                    gap = (ev_s - last_e_cal).total_seconds() / 60
                    if gap > best_gap:
                        best_gap = gap; best_s = last_e_cal; best_e = ev_s
                last_e_cal = max(last_e_cal, ev_e)
            if last_e_cal < pref_e:
                gap = (pref_e - last_e_cal).total_seconds() / 60
                if gap > best_gap:
                    best_gap = gap; best_s = last_e_cal; best_e = pref_e
            if best_gap >= 60 and best_s and best_e:
                st.markdown(f'''
                <div style="background:linear-gradient(135deg,#f0fdf4,#dcfce7);border:1px solid #86efac;
                            border-radius:10px;padding:0.75rem 1rem;margin-bottom:1rem;display:flex;align-items:center;gap:10px;">
                    <span style="font-size:1.3rem;">🚀</span>
                    <div>
                        <div style="font-size:0.7rem;font-weight:700;color:#15803d;text-transform:uppercase;letter-spacing:0.06em;">Best Focus Window Today</div>
                        <div style="font-size:0.9rem;font-weight:600;color:#166534;">{best_s.strftime("%H:%M")} – {best_e.strftime("%H:%M")} · {int(best_gap)} min free block</div>
                    </div>
                </div>''', unsafe_allow_html=True)

        # Task selector
        tc1, tc2 = st.columns([3, 1])
        with tc1:
            pending_labels = [f"{'🔴' if t['priority']=='High' else '🟡' if t['priority']=='Medium' else '🟢'} {t['name']}" for t in pending]
            sel_label = st.selectbox("Select task to focus on", pending_labels, key="timer_task_select")
        sel_idx_pending    = pending_labels.index(sel_label)
        sel_task_name      = pending[sel_idx_pending]['name']
        global_task_idx    = next((i for i, t in enumerate(all_tasks) if t['name'] == sel_task_name and t['status'] == 'Pending'), None)

        timer_running = st.session_state['timer_running']
        timer_idx     = st.session_state['timer_task_idx']
        timer_start   = st.session_state['timer_session_start']

        session_elapsed = 0
        if timer_running and timer_start is not None:
            session_elapsed = int((datetime.now() - timer_start).total_seconds())

        accumulated = all_tasks[global_task_idx].get('focused_seconds', 0) if global_task_idx is not None else 0

        is_timing_this = timer_running and timer_idx == global_task_idx
        display_elapsed = session_elapsed if is_timing_this else 0
        display_total   = (accumulated + session_elapsed) if is_timing_this else accumulated

        active_other_name = None
        if timer_running and timer_idx is not None and not is_timing_this and timer_idx < len(all_tasks):
            active_other_name = all_tasks[timer_idx]['name']

        status_txt = "⏱ RUNNING" if is_timing_this else ("⏸ PAUSED — other task active" if timer_running else "READY")

        st.markdown(f'''
        <div class="timer-panel">
            <div style="font-size:0.68rem;font-weight:700;color:#a5b4fc;text-transform:uppercase;letter-spacing:0.12em;text-align:center;margin-bottom:0.2rem;">{status_txt}</div>
            <div class="timer-task-name">{sel_label}</div>
            <div class="timer-display">{fmt_seconds(display_elapsed)}</div>
            <div class="timer-total">Total accumulated: {fmt_seconds(display_total)}</div>
        </div>''', unsafe_allow_html=True)

        b1, b2, b3, b4, _ = st.columns([1, 1, 1, 1, 2])
        with b1:
            lbl = "⏸ Pause" if is_timing_this else "▶ Start"
            if st.button(lbl, use_container_width=True, key="timer_startstop_btn"):
                if is_timing_this:
                    elapsed = int((datetime.now() - timer_start).total_seconds())
                    users = load_users()
                    users[st.session_state['user_email']]['tasks'][global_task_idx]['focused_seconds'] = accumulated + elapsed
                    save_users(users)
                    st.session_state['timer_running']       = False
                    st.session_state['timer_session_start'] = None
                else:
                    if timer_running and timer_idx is not None and timer_start is not None:
                        elapsed = int((datetime.now() - timer_start).total_seconds())
                        users = load_users()
                        users[st.session_state['user_email']]['tasks'][timer_idx]['focused_seconds'] = \
                            users[st.session_state['user_email']]['tasks'][timer_idx].get('focused_seconds', 0) + elapsed
                        save_users(users)
                    st.session_state['timer_running']       = True
                    st.session_state['timer_task_idx']      = global_task_idx
                    st.session_state['timer_session_start'] = datetime.now()
                st.rerun()

        with b2:
            if st.button("🔄 Refresh", use_container_width=True, key="timer_refresh_btn"):
                st.rerun()

        with b3:
            if st.button("✅ Mark Done", use_container_width=True, key="timer_done_btn"):
                users = load_users()
                if is_timing_this:
                    elapsed = int((datetime.now() - timer_start).total_seconds())
                    users[st.session_state['user_email']]['tasks'][global_task_idx]['focused_seconds'] = accumulated + elapsed
                    st.session_state['timer_running']       = False
                    st.session_state['timer_session_start'] = None
                users[st.session_state['user_email']]['tasks'][global_task_idx]['status'] = 'Completed'
                save_users(users)
                st.rerun()

        with b4:
            if st.button("🗑 Reset Time", use_container_width=True, key="timer_reset_btn"):
                if is_timing_this:
                    st.session_state['timer_running']       = False
                    st.session_state['timer_session_start'] = None
                users = load_users()
                users[st.session_state['user_email']]['tasks'][global_task_idx]['focused_seconds'] = 0
                save_users(users)
                st.rerun()

        if active_other_name:
            st.info(f"⚠️ Timer is running for **\"{active_other_name}\"**. Starting here will pause and save that session.")

    # ── Task List ─────────────────────────────────────────────────────────────
    st.markdown('<div class="section-header">Your Tasks</div>', unsafe_allow_html=True)
    users     = load_users()
    user_data = users[st.session_state['user_email']]
    if user_data.get('tasks'):
        for i, task in enumerate(user_data['tasks']):
            with st.container():
                col1, col2, col3, col4 = st.columns([5, 1.5, 1.5, 1])
                with col1:
                    done_style  = "task-name done" if task['status'] == 'Completed' else "task-name"
                    fsec        = task.get('focused_seconds', 0)
                    fnote       = f" <span style='color:#9ca3af;font-size:0.75rem;'>· ⏱ {fmt_seconds(fsec)}</span>" if fsec > 0 else ""
                    st.markdown(f"<span class='{done_style}'>{task['name']}</span>{fnote}", unsafe_allow_html=True)
                with col2:
                    st.markdown(f"<span class='badge-{task['priority'].lower()}'>{task['priority']}</span>", unsafe_allow_html=True)
                with col3:
                    sb = "badge-done" if task['status'] == 'Completed' else "badge-pending"
                    st.markdown(f"<span class='{sb}'>{task['status']}</span>", unsafe_allow_html=True)
                with col4:
                    if task['status'] == "Pending":
                        if st.button("Done", key=f"done_{i}"):
                            users = load_users()
                            users[st.session_state['user_email']]['tasks'][i]['status'] = "Completed"
                            save_users(users); st.rerun()
                    else:
                        if st.button("Delete", key=f"del_{i}"):
                            users = load_users()
                            users[st.session_state['user_email']]['tasks'].pop(i)
                            save_users(users); st.rerun()
                st.markdown("<hr style='margin:0.4rem 0;border-color:#f3f4f6;'>", unsafe_allow_html=True)
    else:
        st.info("No tasks yet. Add your first task above.")

    # ── Focus History ─────────────────────────────────────────────────────────
    users      = load_users()
    user_data  = users[st.session_state['user_email']]
    timed_tasks = [t for t in user_data.get('tasks', []) if t.get('focused_seconds', 0) > 0]
    if timed_tasks:
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown('<div class="section-header">📊 Focus Time History</div>', unsafe_allow_html=True)
        total_all = sum(t.get('focused_seconds', 0) for t in timed_tasks)
        st.markdown(f'''
        <div style="background:linear-gradient(135deg,#1e1b4b,#312e81);border-radius:12px;
                    padding:1rem 1.5rem;margin-bottom:1rem;display:flex;align-items:center;gap:2rem;">
            <div style="text-align:center;">
                <div style="font-size:2rem;font-weight:800;color:#c7d2fe;">{fmt_seconds(total_all)}</div>
                <div style="font-size:0.7rem;color:#a5b4fc;text-transform:uppercase;letter-spacing:0.05em;">Total Focus Time</div>
            </div>
            <div style="height:40px;width:1px;background:#4338ca;"></div>
            <div style="text-align:center;">
                <div style="font-size:2rem;font-weight:800;color:#c7d2fe;">{len(timed_tasks)}</div>
                <div style="font-size:0.7rem;color:#a5b4fc;text-transform:uppercase;letter-spacing:0.05em;">Tasks Tracked</div>
            </div>
            <div style="height:40px;width:1px;background:#4338ca;"></div>
            <div style="text-align:center;">
                <div style="font-size:2rem;font-weight:800;color:#c7d2fe;">{sum(1 for t in timed_tasks if t['status']=='Completed')}</div>
                <div style="font-size:0.7rem;color:#a5b4fc;text-transform:uppercase;letter-spacing:0.05em;">Completed</div>
            </div>
        </div>''', unsafe_allow_html=True)

        for t in sorted(timed_tasks, key=lambda x: x.get('focused_seconds', 0), reverse=True):
            secs      = t.get('focused_seconds', 0)
            pct_bar   = min(100, int(secs / max(1, total_all) * 100))
            bar_color = "#10b981" if t['status'] == 'Completed' else "#6366f1"
            sb        = "badge-done" if t['status'] == 'Completed' else "badge-pending"
            st.markdown(f'''
            <div style="background:#fff;border-radius:10px;padding:0.85rem 1rem;margin-bottom:8px;
                        border:1px solid #e5e7eb;box-shadow:0 1px 3px rgba(0,0,0,0.04);">
                <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:6px;">
                    <div style="font-size:0.9rem;font-weight:600;color:#111827;flex:1;">{t['name']}</div>
                    <div style="display:flex;gap:6px;align-items:center;">
                        <span class="badge-{t['priority'].lower()}">{t['priority']}</span>
                        <span class="{sb}">{t['status']}</span>
                        <span style="font-size:0.88rem;font-weight:700;color:{bar_color};margin-left:8px;">⏱ {fmt_seconds(secs)}</span>
                    </div>
                </div>
                <div style="background:#f3f4f6;border-radius:4px;height:5px;">
                    <div style="background:{bar_color};width:{pct_bar}%;height:5px;border-radius:4px;"></div>
                </div>
            </div>''', unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# CALENDAR ANALYZER
# ══════════════════════════════════════════════════════════════════════════════
elif menu == "Calendar Analyzer":
    st.markdown('<div class="header-style">Calendar Analyzer</div>', unsafe_allow_html=True)
    st.markdown('<div class="subheader-style">Upload your .ics file for a structured, professional view of your week.</div>', unsafe_allow_html=True)

    col_a, col_b, col_c = st.columns([1, 1, 1])
    with col_a: preferred_start_time = st.time_input("Preferred Start Time", value=time(9, 0))
    with col_b: earliest_leave_time  = st.time_input("Earliest realistic time you can leave work", value=time(17, 0))
    with col_c: commute_time         = st.slider("How long does it take you to get home? (minutes)", 0, 120, 10)

    if 'calendar_events' not in st.session_state:
        users     = load_users()
        user_data = users[st.session_state['user_email']]
        saved_events = user_data.get('calendar_events', [])
        if saved_events:
            loaded_events = []
            for ev in saved_events:
                loaded_events.append({
                    'Event': ev['Event'],
                    'Start': datetime.fromisoformat(ev['Start']),
                    'End':   datetime.fromisoformat(ev['End']),
                    'Duration (mins)': ev['Duration (mins)'],
                    'Date':  datetime.fromisoformat(ev['Date']).date()
                })
            st.session_state['calendar_events']  = loaded_events
            st.session_state['calendar_filename'] = user_data.get('calendar_filename', "Saved Calendar.ics")
        else:
            st.session_state['calendar_events']  = []
            st.session_state['calendar_filename'] = ""

    uploaded_file = st.file_uploader("Upload a Calendar File (.ics)", type=["ics"])
    if uploaded_file is not None:
        try:
            cal = Calendar.from_ical(uploaded_file.read())
            events = []; saved_to_json = []
            for component in cal.walk():
                if component.name == "VEVENT":
                    summary    = component.get('summary')
                    dtstart_val= component.get('dtstart')
                    dtend_val  = component.get('dtend')
                    if dtstart_val and dtend_val:
                        dtstart = dtstart_val.dt; dtend = dtend_val.dt
                        if isinstance(dtstart, datetime) and isinstance(dtend, datetime):
                            dtstart = dtstart.replace(tzinfo=None); dtend = dtend.replace(tzinfo=None)
                            duration = (dtend - dtstart).total_seconds() / 60.0
                            events.append({'Event': str(summary), 'Start': dtstart, 'End': dtend,
                                           'Duration (mins)': duration, 'Date': dtstart.date()})
                            saved_to_json.append({'Event': str(summary), 'Start': dtstart.isoformat(),
                                                  'End': dtend.isoformat(), 'Duration (mins)': duration,
                                                  'Date': dtstart.date().isoformat()})
            if len(events) == 0:
                st.warning("No timed events found in the calendar.")
            else:
                st.session_state['calendar_events']  = events
                st.session_state['calendar_filename'] = uploaded_file.name
                users = load_users()
                users[st.session_state['user_email']]['calendar_events']  = saved_to_json
                users[st.session_state['user_email']]['calendar_filename'] = uploaded_file.name
                save_users(users)
                st.success(f"Successfully loaded and persisted: {uploaded_file.name}")
                st.rerun()
        except Exception as e:
            st.error(f"Error parsing the calendar file: {e}")

    active_events = st.session_state.get('calendar_events', [])
    if active_events:
        st.markdown('<div class="card-container" style="border-left:4px solid #10b981; margin-bottom:1.5rem;">', unsafe_allow_html=True)
        col_info, col_clear = st.columns([4, 1])
        with col_info:
            st.markdown(f"📅 **Active Calendar:** `{st.session_state.get('calendar_filename', 'Loaded Calendar')}`")
        with col_clear:
            if st.button("🗑️ Clear Calendar", use_container_width=True):
                st.session_state['calendar_events'] = []; st.session_state['calendar_filename'] = ""
                users = load_users()
                users[st.session_state['user_email']]['calendar_events']  = []
                users[st.session_state['user_email']]['calendar_filename'] = ""
                save_users(users); st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

        event_df = pd.DataFrame(active_events).sort_values('Start').reset_index(drop=True)
        dates    = event_df['Date'].unique()
        num_days = len(dates)

        total_meetings_week = len(event_df)
        total_hours_week    = event_df['Duration (mins)'].sum() / 60.0
        late_meetings_count = len(event_df[event_df['End'].dt.time > earliest_leave_time])
        meetings_per_day    = event_df.groupby('Date').size()
        busiest_day_date    = meetings_per_day.idxmax()
        best_day_date       = meetings_per_day.idxmin()

        total_free_mins = 0; large_blocks_count = 0; short_gaps_count = 0
        for d in dates:
            day_evs = event_df[event_df['Date'] == d].sort_values('Start')
            d_start = datetime.combine(d, preferred_start_time)
            d_end   = datetime.combine(d, earliest_leave_time)
            last_e  = d_start
            for _, row in day_evs.iterrows():
                ev_s = max(d_start, row['Start']); ev_e = min(d_end, row['End'])
                if ev_s > ev_e: ev_s, ev_e = ev_e, ev_s
                if ev_s > last_e:
                    gap = (ev_s - last_e).total_seconds() / 60.0
                    total_free_mins += gap
                    if gap >= 60: large_blocks_count += 1
                    if 0 < gap < 30: short_gaps_count += 1
                last_e = max(last_e, ev_e)
            if last_e < d_end:
                gap = (d_end - last_e).total_seconds() / 60.0
                total_free_mins += gap
                if gap >= 60: large_blocks_count += 1
                if 0 < gap < 30: short_gaps_count += 1

        focus_score         = round(min(10.0, (large_blocks_count / max(1, num_days)) * 3), 1)
        fragmentation_score = round(min(10.0, (short_gaps_count   / max(1, num_days)) * 2), 1)

        # ── Styled Weekly Summary Card ────────────────────────────────────────
        avg_mtg_day  = total_meetings_week / max(1, num_days)
        load_color   = "#10b981" if total_hours_week <= 10 else ("#f59e0b" if total_hours_week <= 15 else "#ef4444")
        focus_color  = "#10b981" if focus_score >= 6 else ("#f59e0b" if focus_score >= 3 else "#ef4444")
        st.markdown(f'''
        <div style="background:linear-gradient(135deg,#0f172a,#1e293b);border-radius:16px;
                    padding:1.5rem 2rem;margin-bottom:1.5rem;box-shadow:0 8px 30px rgba(0,0,0,0.2);">
            <div style="font-size:0.72rem;font-weight:700;color:#64748b;text-transform:uppercase;
                        letter-spacing:0.1em;margin-bottom:1rem;">📊 Weekly Schedule Summary</div>
            <div style="display:grid;grid-template-columns:repeat(6,1fr);gap:12px;">
                <div style="text-align:center;">
                    <div style="font-size:1.6rem;font-weight:800;color:#f1f5f9;">{total_meetings_week}</div>
                    <div style="font-size:0.68rem;color:#64748b;margin-top:2px;">Total Meetings</div>
                </div>
                <div style="text-align:center;">
                    <div style="font-size:1.6rem;font-weight:800;color:{load_color};">{total_hours_week:.1f}h</div>
                    <div style="font-size:0.68rem;color:#64748b;margin-top:2px;">Meeting Time</div>
                </div>
                <div style="text-align:center;">
                    <div style="font-size:1.6rem;font-weight:800;color:#6366f1;">{int(total_free_mins//60)}h {int(total_free_mins%60)}m</div>
                    <div style="font-size:0.68rem;color:#64748b;margin-top:2px;">Free Time</div>
                </div>
                <div style="text-align:center;">
                    <div style="font-size:1.6rem;font-weight:800;color:{focus_color};">{focus_score}/10</div>
                    <div style="font-size:0.68rem;color:#64748b;margin-top:2px;">Focus Score</div>
                </div>
                <div style="text-align:center;">
                    <div style="font-size:1.6rem;font-weight:800;color:#f59e0b;">{late_meetings_count}</div>
                    <div style="font-size:0.68rem;color:#64748b;margin-top:2px;">Late Meetings</div>
                </div>
                <div style="text-align:center;">
                    <div style="font-size:1.6rem;font-weight:800;color:#f1f5f9;">{avg_mtg_day:.1f}</div>
                    <div style="font-size:0.68rem;color:#64748b;margin-top:2px;">Avg Meetings/Day</div>
                </div>
            </div>
        </div>''', unsafe_allow_html=True)

        # ── Meeting Load Heatmap ──────────────────────────────────────────────
        with st.expander("🔥 Meeting Load Heatmap", expanded=True):
            st.markdown("Hour-by-hour grid showing when meetings are concentrated. **Darker red = more meeting time.**")
            hours     = list(range(preferred_start_time.hour, min(earliest_leave_time.hour + 1, 24)))
            day_names = [d.strftime('%a %d') for d in sorted(dates)]
            hm_data   = np.zeros((len(hours), len(sorted(dates))))
            for di, d in enumerate(sorted(dates)):
                for _, row in event_df[event_df['Date'] == d].iterrows():
                    for hi, h in enumerate(hours):
                        slot_s = datetime.combine(d, time(h, 0))
                        slot_e = datetime.combine(d, time(min(h + 1, 23), 59))
                        ov_s   = max(slot_s, row['Start']); ov_e = min(slot_e, row['End'])
                        if ov_e > ov_s:
                            hm_data[hi, di] += (ov_e - ov_s).total_seconds() / 60

            fig_hm, ax_hm = plt.subplots(figsize=(max(6, len(day_names) * 1.4), max(4, len(hours) * 0.55)))
            fig_hm.patch.set_facecolor('#ffffff')
            im = ax_hm.imshow(hm_data, aspect='auto', cmap='RdYlGn_r', vmin=0, vmax=60, interpolation='nearest')
            ax_hm.set_xticks(range(len(day_names))); ax_hm.set_xticklabels(day_names, fontsize=9, fontweight='600', color='#374151')
            ax_hm.set_yticks(range(len(hours)));     ax_hm.set_yticklabels([f"{h:02d}:00" for h in hours], fontsize=8.5, color='#6b7280')
            for hi in range(len(hours)):
                for di in range(len(day_names)):
                    v = hm_data[hi, di]
                    if v > 0:
                        ax_hm.text(di, hi, f"{int(v)}m", ha='center', va='center',
                                   fontsize=7.5, fontweight='600', color='white' if v > 35 else '#374151')
            ax_hm.set_title("Meeting Minutes per Hour Slot", fontsize=10, fontweight='600', color='#111827', pad=10)
            ax_hm.spines[:].set_visible(False); ax_hm.tick_params(length=0)
            cbar = plt.colorbar(im, ax=ax_hm, shrink=0.8, pad=0.02)
            cbar.set_label('Minutes of meetings', fontsize=8, color='#6b7280')
            cbar.ax.tick_params(labelsize=7.5)
            plt.tight_layout()
            st.pyplot(fig_hm)
            st.caption("🟢 Green = free   🟡 Yellow = partially booked   🔴 Red = heavily booked")

        # ── What-If Schedule Simulator ────────────────────────────────────────
        with st.expander("🔮 What-If Schedule Simulator"):
            st.markdown("Simulate **removing meetings by keyword** and instantly see the impact on your free blocks and focus time.")
            sim_keyword = st.text_input("Meeting keyword to remove (e.g. 'standup', '1:1', 'sync')",
                                        placeholder="standup", key="whatif_keyword")
            if sim_keyword.strip():
                kw    = sim_keyword.strip().lower()
                mask  = event_df['Event'].str.lower().str.contains(kw, na=False)
                filt  = event_df[~mask]
                rm_cnt  = mask.sum()
                rm_mins = event_df[mask]['Duration (mins)'].sum()

                sim_free = 0; sim_blocks = 0
                for d in dates:
                    sim_evs = filt[filt['Date'] == d].sort_values('Start')
                    d_s = datetime.combine(d, preferred_start_time)
                    d_e = datetime.combine(d, earliest_leave_time)
                    l_e = d_s
                    for _, row in sim_evs.iterrows():
                        ev_s = max(d_s, row['Start']); ev_e = min(d_e, row['End'])
                        if ev_s > ev_e: ev_s, ev_e = ev_e, ev_s
                        if ev_s > l_e:
                            gap = (ev_s - l_e).total_seconds() / 60
                            sim_free += gap
                            if gap >= 60: sim_blocks += 1
                        l_e = max(l_e, ev_e)
                    if l_e < d_e:
                        gap = (d_e - l_e).total_seconds() / 60
                        sim_free += gap
                        if gap >= 60: sim_blocks += 1

                delta_free   = sim_free   - total_free_mins
                delta_blocks = sim_blocks - large_blocks_count

                if rm_cnt == 0:
                    st.warning(f'No meetings found matching **"{sim_keyword}"**.')
                else:
                    cs1, cs2, cs3, cs4 = st.columns(4)
                    cs1.metric("Meetings Removed",  rm_cnt,    f"-{rm_cnt}")
                    cs2.metric("Time Reclaimed",    f"{rm_mins/60:.1f}h", f"+{rm_mins/60:.1f}h")
                    cs3.metric("Free Time (total)", f"{int(sim_free//60)}h {int(sim_free%60)}m",
                               f"+{int(delta_free//60)}h {int(delta_free%60)}m" if delta_free >= 0 else f"{int(delta_free//60)}h {int(delta_free%60)}m")
                    cs4.metric("Focus Blocks ≥1h",  sim_blocks, f"+{delta_blocks}" if delta_blocks >= 0 else str(delta_blocks))
                    st.success(f"🎉 Removing **{rm_cnt}** \"{sim_keyword}\" meeting{'s' if rm_cnt > 1 else ''} would free up **{rm_mins/60:.1f} hours** and give you **{delta_blocks} more** deep-work blocks.")
            else:
                st.info("Type a keyword above to simulate removing those meetings from your schedule.")

        st.markdown("---")

        # ── Weekly Insights ───────────────────────────────────────────────────
        with st.container():
            st.subheader("💡 Weekly Insights")
            weekly_recs = []
            if total_hours_week > 15:
                weekly_recs.append({"priority": 90, "category": "Overload",
                    "message": f"You have {total_hours_week:.1f} hours of meetings this week. Prioritize delegating or declining non-essential invites.", "type": "warning"})
            if late_meetings_count >= 3:
                weekly_recs.append({"priority": 85, "category": "Balance",
                    "message": f"You have {late_meetings_count} meetings extending past your earliest leave time ({earliest_leave_time.strftime('%H:%M')}). Try to enforce a harder evening boundary.", "type": "warning"})
            weekly_recs.append({"priority": 80, "category": "Overload",
                "message": f"Your busiest day is {busiest_day_date.strftime('%A')} ({meetings_per_day.max()} meetings). Prepare in advance or avoid scheduling heavy tasks before/after.", "type": "warning"})
            weekly_recs.append({"priority": 75, "category": "Focus",
                "message": f"{best_day_date.strftime('%A')} is your lightest day ({meetings_per_day.min()} meetings) → guard this day aggressively for deep focus work.", "type": "success"})
            weekly_recs = sorted(weekly_recs, key=lambda x: x['priority'], reverse=True)[:3]
            for r in weekly_recs:
                if r['type'] == 'warning': st.warning(f"**{r['category']}:** {r['message']}")
                elif r['type'] == 'success': st.success(f"**{r['category']}:** {r['message']}")
                else: st.info(f"**{r['category']}:** {r['message']}")
            if not any(r['type'] == 'warning' for r in weekly_recs):
                st.success("✨ Your week looks structurally sound! Low overload risk detected.")

        st.markdown("---")

        # ── Daily Breakdown ───────────────────────────────────────────────────
        with st.container():
            st.subheader("📅 Daily Breakdown")
        for d in dates:
            day_events   = event_df[event_df['Date'] == d].copy().sort_values('Start')
            num_meetings = len(day_events)
            with st.expander(f"{d.strftime('%A, %d %B')} — {num_meetings} meeting{'s' if num_meetings != 1 else ''}"):
                day_total_mins    = day_events['Duration (mins)'].sum()
                first_meet        = day_events.iloc[0]['Start'].strftime('%H:%M') if num_meetings > 0 else "N/A"
                last_meet         = day_events.iloc[-1]['End'].strftime('%H:%M')   if num_meetings > 0 else "N/A"
                longest_meet_mins = day_events['Duration (mins)'].max()            if num_meetings > 0 else 0
                day_start = datetime.combine(d, preferred_start_time)
                day_end   = datetime.combine(d, earliest_leave_time)
                local_free_mins = 0
                last_e = day_start
                for _, row in day_events.iterrows():
                    ev_s = max(day_start, row['Start']); ev_e = min(day_end, row['End'])
                    if ev_s > ev_e: ev_s, ev_e = ev_e, ev_s
                    if ev_s > last_e: local_free_mins += (ev_s - last_e).total_seconds() / 60.0
                    last_e = max(last_e, ev_e)
                if last_e < day_end: local_free_mins += (day_end - last_e).total_seconds() / 60.0

                c1, c2, c3, c4, c5 = st.columns(5)
                c1.metric("Tot. Meet Time", f"{int(day_total_mins//60)}h {int(day_total_mins%60)}m")
                c2.metric("Free Time",      f"{int(local_free_mins//60)}h {int(local_free_mins%60)}m")
                c3.metric("Longest Meet",   f"{int(longest_meet_mins)}m")
                c4.metric("First Start",    first_meet)
                c5.metric("Last End",       last_meet)

                st.markdown("##### 📝 Schedule")
                agenda_html     = ['<div class="agenda-container">']
                last_end_agenda = datetime.combine(d, preferred_start_time)
                for _, row in day_events.iterrows():
                    ev_start = row['Start']; ev_end = row['End']
                    title = row['Event']; dur = row['Duration (mins)']
                    if ev_start > last_end_agenda:
                        gap = (ev_start - last_end_agenda).total_seconds() / 60.0
                        if gap >= 60:
                            agenda_html.append(f'<div class="agenda-focus-block">🚀 Deep Work Window: {last_end_agenda.strftime("%H:%M")} – {ev_start.strftime("%H:%M")} &nbsp;|&nbsp; {int(gap)} min</div>')
                        elif gap >= 30:
                            agenda_html.append(f'<div class="agenda-free">☕ {last_end_agenda.strftime("%H:%M")} – {ev_start.strftime("%H:%M")} | {int(gap)} min Free Block</div>')
                    color_class = "short" if dur < 30 else ("long" if dur > 90 else "normal")
                    agenda_html.append(
                        f'<div class="agenda-card {color_class}">'
                        f'<div class="agenda-time">{ev_start.strftime("%H:%M")} – {ev_end.strftime("%H:%M")}</div>'
                        f'<div class="agenda-title">🔹 {title}</div>'
                        f'<div class="agenda-duration">🕒 {int(dur)} mins</div></div>')
                    last_end_agenda = max(last_end_agenda, ev_end)
                day_end_agenda = datetime.combine(d, earliest_leave_time)
                if last_end_agenda < day_end_agenda:
                    gap = (day_end_agenda - last_end_agenda).total_seconds() / 60.0
                    if gap >= 60:
                        agenda_html.append(f'<div class="agenda-focus-block">🚀 Deep Work Window: {last_end_agenda.strftime("%H:%M")} – {day_end_agenda.strftime("%H:%M")} &nbsp;|&nbsp; {int(gap)} min</div>')
                    elif gap >= 30:
                        agenda_html.append(f'<div class="agenda-free">🚀 {last_end_agenda.strftime("%H:%M")} – {day_end_agenda.strftime("%H:%M")} | {int(gap)} min Focus / Wrap-up</div>')
                agenda_html.append('</div>')
                st.markdown("".join(agenda_html), unsafe_allow_html=True)

                with st.expander("Show raw events table"):
                    disp = day_events.copy()
                    disp['Start'] = disp['Start'].dt.strftime('%H:%M')
                    disp['End']   = disp['End'].dt.strftime('%H:%M')
                    st.dataframe(disp[['Event', 'Start', 'End', 'Duration (mins)']], use_container_width=True)

                st.markdown("##### 💡 Daily Advice")
                show_more = st.checkbox("Show more recommendations", key=f"show_more_{d}")
                max_recs  = 6 if show_more else 3
                recs = []
                lunch_start = datetime.combine(d, time(12, 0)); lunch_end = datetime.combine(d, time(14, 0))
                has_lunch = False; l_t = lunch_start
                for _, row in day_events.iterrows():
                    if row['Start'] > l_t and row['Start'] <= lunch_end:
                        if (row['Start'] - l_t).total_seconds() / 60 >= 30: has_lunch = True
                    l_t = max(l_t, row['End'])
                if l_t < lunch_end and (lunch_end - l_t).total_seconds() / 60 >= 30: has_lunch = True
                if not has_lunch and num_meetings > 0:
                    recs.append({"priority": 95, "category": "Break", "message": "No proper lunch break scheduled → guard 30+ minutes between 12:00 and 14:00.", "type": "warning"})
                if day_total_mins > 240:
                    recs.append({"priority": 90, "category": "Overload", "message": "Heavy meeting day (>4 hrs) → avoid demanding tasks immediately after meetings.", "type": "warning"})
                if num_meetings >= 5:
                    recs.append({"priority": 85, "category": "Overload", "message": f"{num_meetings} meetings today → evaluate deferring non-essential ones.", "type": "warning"})
                if longest_meet_mins > 90:
                    recs.append({"priority": 80, "category": "Buffer", "message": "You have a long meeting (>90 mins) → ensure a strict recovery buffer immediately afterward.", "type": "warning"})
                has_b2b = False
                for i_b in range(len(day_events) - 1):
                    curr_end   = day_events.iloc[i_b]['End']
                    next_start = day_events.iloc[i_b + 1]['Start']
                    gap = (next_start - curr_end).total_seconds() / 60.0
                    if 0 <= gap < 10: has_b2b = True
                    if gap >= 60:
                        recs.append({"priority": 65, "category": "Focus", "message": f"Large free block from {curr_end.strftime('%H:%M')} to {next_start.strftime('%H:%M')} → reserve exclusively for deep work.", "type": "success"})
                    elif 30 <= gap < 60:
                        recs.append({"priority": 60, "category": "Email", "message": f"Short gap from {curr_end.strftime('%H:%M')} to {next_start.strftime('%H:%M')} → optimal window for emails/admin.", "type": "info"})
                if has_b2b:
                    recs.append({"priority": 80, "category": "Buffer", "message": "Back-to-back meetings detected → consider 5-minute transition breaks between calls.", "type": "warning"})
                if num_meetings > 0:
                    first_m = day_events.iloc[0]['Start']
                    if first_m > day_start and (first_m - day_start).total_seconds() / 60 >= 60:
                        recs.append({"priority": 68, "category": "Focus", "message": f"Morning clear until {first_m.strftime('%H:%M')} → excellent time for uninterrupted focus.", "type": "success"})
                    last_m = day_events.iloc[-1]['End']
                    if last_m.hour < 13:
                        recs.append({"priority": 70, "category": "Focus", "message": "No afternoon meetings — great time to complete important tasks or admin work.", "type": "success"})
                    if last_m >= day_end:
                        arr_time = last_m + pd.Timedelta(minutes=commute_time)
                        recs.append({"priority": 50, "category": "Commute", "message": f"Last meeting runs until {last_m.strftime('%H:%M')}. With commute, you'd arrive home around {arr_time.strftime('%H:%M')}.", "type": "warning"})
                    else:
                        rem = (day_end - last_m).total_seconds() / 60.0
                        if rem <= 45:
                            recs.append({"priority": 60, "category": "Commute", "message": f"No meetings after {last_m.strftime('%H:%M')}. Leaving around {earliest_leave_time.strftime('%H:%M')} is realistic.", "type": "info"})
                        else:
                            recs.append({"priority": 58, "category": "Admin", "message": f"No meetings after {last_m.strftime('%H:%M')}. Use time until {earliest_leave_time.strftime('%H:%M')} for focused work or planning.", "type": "info"})

                recs = sorted(recs, key=lambda x: x['priority'], reverse=True)
                seen_cats = set(); final_recs = []
                for r in recs:
                    if r['category'] not in seen_cats:
                        final_recs.append(r); seen_cats.add(r['category'])
                final_recs = final_recs[:max_recs]
                if not final_recs: st.success("✨ Your day is perfectly balanced. Enjoy!")
                else:
                    for r in final_recs:
                        if r['type'] == 'warning': st.warning(f"**{r['category']}:** {r['message']}")
                        elif r['type'] == 'success': st.success(f"**{r['category']}:** {r['message']}")
                        else: st.info(f"**{r['category']}:** {r['message']}")

        st.markdown("---")

        # ── Behavioral Interpretation ─────────────────────────────────────────
        with st.container():
            st.subheader("🧩 Behavioral Interpretation")
            st.markdown("**Based on your weekly schedule patterns, your work rhythm is most similar to:**")
            if total_hours_week >= 15 and (focus_score < 4.0 or late_meetings_count >= 3):
                matched_profile = "The Overworked & Exhausted"
                match_reason = f"Your week shows a heavy meeting load ({total_hours_week:.1f} hours) with frequent interruptions, significantly reducing your opportunity for deep work."
                sugg_1 = f"You have {late_meetings_count} late meetings. Enforce a strict log-off boundary." if late_meetings_count > 0 else "Avoid scheduling complex tasks at end of day when fatigue is highest."
                sugg_2 = f"{best_day_date.strftime('%A')} is your lightest day — guard it aggressively for deep focus work."
                match_border = "#ef4444"; match_bg = "#fef2f2"; match_icon = "🚨"
            elif focus_score >= 6.0 and total_hours_week <= 12 and late_meetings_count <= 1:
                matched_profile = "The Balanced Worker"
                match_reason = "Your schedule maintains an excellent separation between collaboration and focus time."
                sugg_1 = f"Maintain the boundaries you've set, especially on {best_day_date.strftime('%A')} where you have the highest focus efficiency."
                sugg_2 = "Use 10-minute buffers after intense meetings to avoid accumulating cognitive fatigue."
                match_border = "#10b981"; match_bg = "#f0fdf4"; match_icon = "✅"
            elif fragmentation_score >= 6.0 or (total_hours_week < 15 and late_meetings_count >= 2):
                matched_profile = "The Sleep-Deprived / Fragmented"
                match_reason = "Your schedule is highly scattered. Frequent context-switching prevents meaningful progress and raises exhaustion."
                sugg_1 = f"Batch your meetings — {busiest_day_date.strftime('%A')} is loaded with disjointed blocks. Consolidate calls to open up contiguous free time."
                sugg_2 = "Turn off notifications during gaps shorter than 30 minutes to give your brain a true recovery transition."
                match_border = "#f59e0b"; match_bg = "#fffbeb"; match_icon = "⚠️"
            else:
                matched_profile = "The Flexible Worker"
                match_reason = "Your week shows a balanced workload, but ad-hoc meetings may reduce your focus efficiency."
                sugg_1 = f"Identify your best focus window on {best_day_date.strftime('%A')} and permanently block it in your calendar."
                sugg_2 = "Evaluate if recurring scattered meetings can be consolidated to one afternoon per week."
                match_border = "#3b82f6"; match_bg = "#eff6ff"; match_icon = "☕"

            st.markdown(f'''
            <div style="background-color:{match_bg};border-left:5px solid {match_border};border-radius:8px;
                        padding:1.5rem;margin-top:1rem;box-shadow:0 4px 6px -1px rgba(0,0,0,0.05);color:#1f2937;">
                <h3 style="margin-top:0;color:#111827;">{match_icon} {matched_profile}</h3>
                <p style="font-size:1.05rem;margin-bottom:1.5rem;line-height:1.6;"><strong>Why?</strong> {match_reason}</p>
                <h5 style="color:#374151;margin-bottom:0.5rem;font-weight:600;">Contextual Recommendations:</h5>
                <ul style="padding-left:1.5rem;margin-bottom:1.5rem;line-height:1.6;">
                    <li style="margin-bottom:0.5rem;">{sugg_1}</li>
                    <li>{sugg_2}</li>
                </ul>
                <p style="font-size:0.8rem;color:#6b7280;margin:0;font-style:italic;">
                    Note: This is an analytical estimation based purely on your calendar timeline. It functions independently of the machine learning clustering model.
                </p>
            </div>''', unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# WEARABLE & RECOVERY
# ══════════════════════════════════════════════════════════════════════════════
elif menu == "Wearable & Recovery":
    st.markdown('<div class="header-style">Wearable & Recovery</div>', unsafe_allow_html=True)
    st.markdown('<div class="subheader-style">Simulate biometric inputs to see your daily physiological readiness score and personalised recovery plan.</div>', unsafe_allow_html=True)

    BASELINE = {'sleep': 6.8, 'hr': 72, 'stress': 5.0, 'steps': 6000, 'fatigue': 5.0, 'sed': 120}

    with st.expander("⚙️  Adjust Biometric Inputs", expanded=True):
        ci1, ci2, ci3 = st.columns(3)
        with ci1:
            w_sleep   = st.slider("Sleep last night (h)",         2.0, 12.0, 6.5, 0.25)
            w_hr      = st.slider("Avg resting heart rate (bpm)", 40,  150,  74)
        with ci2:
            w_stress  = st.slider("Stress level (0–10)",          0.0, 10.0, 6.2, 0.1)
            w_steps   = st.slider("Steps today",                  0,   20000, 4200, 100)
        with ci3:
            w_fatigue = st.slider("Morning fatigue (1–10)",       1,   10,   7)
            w_sed     = st.slider("Sedentary time (min)",         0,   300,  160, 10)

    # ── Auto-save snapshot ────────────────────────────────────────────────────
    today_str    = datetime.now().strftime('%Y-%m-%d')
    new_snapshot = {'sleep': w_sleep, 'hr': w_hr, 'stress': w_stress,
                    'steps': w_steps, 'fatigue': w_fatigue, 'sed': w_sed, 'date': today_str}
    users = load_users()
    users[st.session_state['user_email']]['wearable_snapshot'] = new_snapshot
    save_users(users)
    user_data = users[st.session_state['user_email']]

    # ── Derived scores ─────────────────────────────────────────────────────────
    sleep_score    = max(0, min(100, (w_sleep  - 4)   * 25))
    stress_score   = max(0, min(100, (10 - w_stress) * 10))
    fatigue_score  = max(0, min(100, (10 - w_fatigue) * 11.1))
    activity_score = max(0, min(100, w_steps / 100))
    recovery_score = round(sleep_score * 0.40 + stress_score * 0.25 + fatigue_score * 0.25 + activity_score * 0.10)

    if   recovery_score >= 67: readiness_label, ring_color, ring_bg = "Optimal",  "#10b981", "#f0fdf4"
    elif recovery_score >= 34: readiness_label, ring_color, ring_bg = "Moderate", "#f59e0b", "#fffbeb"
    else:                      readiness_label, ring_color, ring_bg = "Low",       "#ef4444", "#fef2f2"

    stress_label  = "Low" if w_stress < 3.4 else ("Medium" if w_stress < 6.7 else "High")
    stress_colour = "#10b981" if w_stress < 3.4 else ("#f59e0b" if w_stress < 6.7 else "#ef4444")

    def delta(val, base, higher_is_better=True):
        d_val = val - base
        if abs(d_val) < 0.5: return "→ On par", "#9ca3af"
        if higher_is_better:
            return (f"↑ +{abs(d_val):.1f}", "#10b981") if d_val > 0 else (f"↓ -{abs(d_val):.1f}", "#ef4444")
        else:
            return (f"↑ +{abs(d_val):.1f}", "#ef4444") if d_val > 0 else (f"↓ -{abs(d_val):.1f}", "#10b981")

    sl_d, sl_c = delta(w_sleep,   BASELINE['sleep'],   True)
    hr_d, hr_c = delta(w_hr,      BASELINE['hr'],      False)
    st_d, st_c = delta(w_stress,  BASELINE['stress'],  False)
    sp_d, sp_c = delta(w_steps,   BASELINE['steps'],   True)
    ft_d, ft_c = delta(w_fatigue, BASELINE['fatigue'], False)
    sd_d, sd_c = delta(w_sed,     BASELINE['sed'],     False)

    # ── SVG Arc Gauge + Metric Grid ───────────────────────────────────────────
    st.markdown("<br>", unsafe_allow_html=True)
    left, right = st.columns([1, 2])

    with left:
        # SVG half-circle arc gauge
        arc_pct   = recovery_score / 100
        half_circ = 175.9  # π × r where r=56 (half of full circle)
        filled    = arc_pct * half_circ
        st.markdown(f'''
        <div style="background:{ring_bg};border:2px solid {ring_color};border-radius:16px;
                    padding:2rem 1.5rem;text-align:center;">
            <div style="font-size:0.72rem;font-weight:700;color:#6b7280;text-transform:uppercase;
                        letter-spacing:0.08em;margin-bottom:0.75rem;">Recovery Score</div>
            <svg width="150" height="90" viewBox="0 0 150 90" style="display:block;margin:0 auto 0.5rem;">
                <path d="M 12 75 A 63 63 0 0 1 138 75"
                      fill="none" stroke="#e5e7eb" stroke-width="12" stroke-linecap="round"/>
                <path d="M 12 75 A 63 63 0 0 1 138 75"
                      fill="none" stroke="{ring_color}" stroke-width="12" stroke-linecap="round"
                      stroke-dasharray="{filled:.1f} {half_circ:.1f}"/>
                <text x="75" y="68" text-anchor="middle" font-size="28" font-weight="800"
                      fill="{ring_color}" font-family="Inter, sans-serif">{recovery_score}</text>
            </svg>
            <div style="font-size:0.78rem;color:#9ca3af;">out of 100</div>
            <div style="background:{ring_color};color:#fff;border-radius:20px;padding:0.3rem 1.2rem;
                        display:inline-block;margin-top:0.75rem;font-weight:700;font-size:0.95rem;">
                {readiness_label}
            </div>
            <div style="font-size:0.75rem;color:#9ca3af;margin-top:0.75rem;">vs. your 7-day baseline</div>
        </div>''', unsafe_allow_html=True)

    with right:
        def metric_card(icon, label, value, unit, trend_txt, trend_col, bar_pct, bar_col):
            return f'''
            <div style="background:#fff;border:1px solid #e5e7eb;border-radius:12px;
                        padding:1rem 1.2rem;margin-bottom:10px;box-shadow:0 1px 4px rgba(0,0,0,0.05);">
                <div style="display:flex;justify-content:space-between;align-items:center;">
                    <div>
                        <div style="font-size:0.72rem;font-weight:600;color:#6b7280;text-transform:uppercase;letter-spacing:0.05em;">{icon} {label}</div>
                        <div style="font-size:1.5rem;font-weight:700;color:#111827;line-height:1.2;margin-top:2px;">
                            {value}<span style="font-size:0.85rem;color:#9ca3af;font-weight:400;margin-left:3px;">{unit}</span>
                        </div>
                    </div>
                    <div style="text-align:right;">
                        <span style="font-size:0.8rem;font-weight:600;color:{trend_col};">{trend_txt}</span>
                        <div style="font-size:0.7rem;color:#9ca3af;">vs baseline</div>
                    </div>
                </div>
                <div style="background:#f3f4f6;border-radius:4px;height:4px;margin-top:8px;">
                    <div style="background:{bar_col};width:{bar_pct}%;height:4px;border-radius:4px;"></div>
                </div>
            </div>'''

        sleep_bar = min(100, w_sleep / 10 * 100)
        hr_bar    = min(100, w_hr / 150 * 100)
        step_bar  = min(100, w_steps / 200)
        fat_bar   = w_fatigue * 10
        sed_bar   = min(100, w_sed / 300 * 100)
        cards_html = (
            metric_card("🌙", "Sleep",      f"{w_sleep:.1f}", "hrs",  sl_d, sl_c, sleep_bar, "#6366f1") +
            metric_card("💓", "Heart Rate", f"{w_hr}",        "bpm",  hr_d, hr_c, hr_bar,    "#ef4444") +
            metric_card("🧘", "Stress",     stress_label,     "/ 10", st_d, st_c, w_stress * 10, stress_colour) +
            metric_card("👟", "Steps",      f"{w_steps:,}",   "",     sp_d, sp_c, step_bar,  "#10b981") +
            metric_card("🔋", "Fatigue",    f"{w_fatigue}",   "/ 10", ft_d, ft_c, fat_bar,   "#f59e0b") +
            metric_card("🪑", "Sedentary",  f"{w_sed}",       "min",  sd_d, sd_c, sed_bar,   "#9ca3af")
        )
        st.markdown(cards_html, unsafe_allow_html=True)

    # ── 7-Day Biometric Trend Chart ───────────────────────────────────────────
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div class="section-header">📈 7-Day Biometric Trends</div>', unsafe_allow_html=True)
    st.caption("Simulated trend anchored to your current inputs — illustrates what continuous wearable tracking would look like.")

    days_lbl_w    = [(datetime.now() - timedelta(days=6 - i)).strftime('%a') for i in range(7)]
    sleep_tw      = generate_trend_data(w_sleep,   7, 0.5,  seed=10)
    fatigue_tw    = generate_trend_data(w_fatigue, 7, 0.8,  seed=11)
    stress_tw     = generate_trend_data(w_stress,  7, 5.0,  seed=12)
    steps_tw      = generate_trend_data(w_steps,   7, 400,  seed=13)

    fig_w, axes_w = plt.subplots(1, 4, figsize=(14, 3))
    fig_w.patch.set_facecolor('#f8fafc')
    wear_cfgs = [
        (sleep_tw,   "Sleep (hrs)",     "#6366f1", (4,   10)),
        (fatigue_tw, "Morning Fatigue", "#ef4444", (1,   10)),
        (stress_tw,  "Stress Level",    "#f59e0b", (0,  10)),
        (steps_tw,   "Daily Steps",     "#10b981", (0, 12000)),
    ]
    for ax_w, (data_w, title_w, color_w, ylim_w) in zip(axes_w, wear_cfgs):
        ax_w.set_facecolor('#ffffff')
        ax_w.fill_between(range(7), data_w, alpha=0.15, color=color_w)
        ax_w.plot(range(7), data_w, color=color_w, linewidth=2.5, marker='o', markersize=4)
        ax_w.plot(6, data_w[-1], 'o', color=color_w, markersize=8, zorder=5)
        ax_w.set_xticks(range(7)); ax_w.set_xticklabels(days_lbl_w, fontsize=7.5, color='#6b7280')
        ax_w.set_ylim(ylim_w)
        ax_w.set_title(title_w, fontsize=9, fontweight='600', color='#374151', pad=6)
        ax_w.tick_params(axis='y', labelsize=7.5, colors='#9ca3af')
        ax_w.spines[['top', 'right', 'left']].set_visible(False)
        ax_w.spines['bottom'].set_color('#e5e7eb')
        ax_w.grid(axis='y', color='#f3f4f6', linewidth=0.8)
        ax_w.annotate(f"{data_w[-1]:.1f}", xy=(6, data_w[-1]), xytext=(4, 6),
                      textcoords='offset points', fontsize=8, fontweight='700', color=color_w)
    plt.tight_layout(pad=1.5)
    st.pyplot(fig_w)

    # ── Cross-Section Conflict Banner ─────────────────────────────────────────
    cal_evs_w = st.session_state.get('calendar_events', [])
    if cal_evs_w and w_fatigue >= 7:
        cal_df_w        = pd.DataFrame(cal_evs_w)
        mpd_w           = cal_df_w.groupby('Date').size()
        busiest_w       = mpd_w.idxmax()
        today_w         = datetime.now().date()
        busiest_str_w   = busiest_w.strftime('%A, %d %b')
        if busiest_w == today_w:
            conf_msg = f"Today is your <strong>busiest calendar day</strong> ({mpd_w.max()} meetings) and your fatigue is <strong>{w_fatigue}/10</strong>. Consider deferring non-essential meetings and protecting focus blocks."
        else:
            conf_msg = f"Your busiest calendar day is <strong>{busiest_str_w}</strong> ({mpd_w.max()} meetings). With your current fatigue at <strong>{w_fatigue}/10</strong>, prepare recovery strategies before that day."
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown('<div class="section-header">⚠️ Schedule & Recovery Conflicts</div>', unsafe_allow_html=True)
        st.markdown(f'''
        <div style="background:#fffbeb;border-left:5px solid #f59e0b;border-radius:10px;
                    padding:1rem 1.25rem;margin-bottom:10px;">
            <div style="font-weight:700;color:#92400e;margin-bottom:0.4rem;">🗓️ Calendar + Wearable Conflict Detected</div>
            <div style="font-size:0.88rem;color:#78350f;">{conf_msg}</div>
        </div>''', unsafe_allow_html=True)

    # ── Top-3 Recommendations ─────────────────────────────────────────────────
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div class="section-header">Today\'s Top Recommendations</div>', unsafe_allow_html=True)
    all_recs = []
    if w_sleep < 5.5:
        all_recs.append((100, "🌙", "Critical sleep deficit",
            f"Only {w_sleep:.1f}h sleep — well below the 7h minimum. Reschedule optional afternoon meetings and target a 20-min nap before 15:00.", "#ef4444", "#fef2f2"))
    elif w_sleep < 7.0:
        all_recs.append((70, "🌙", "Mild sleep shortfall",
            f"{w_sleep:.1f}h is below your 7h target. Avoid cognitively heavy tasks before 10:00 to give your brain time to fully activate.", "#f59e0b", "#fffbeb"))
    if w_fatigue >= 8:
        all_recs.append((95, "🔋", "High fatigue — limit deep work",
            f"Fatigue {w_fatigue}/10 is in the danger zone. Confine deep-focus blocks to 45-minute sprints and build a 15-min recovery buffer after each meeting.", "#ef4444", "#fef2f2"))
    elif w_fatigue >= 6:
        all_recs.append((65, "🔋", "Moderate fatigue detected",
            f"Score {w_fatigue}/10 — use the Pomodoro method today (25 min on / 5 min off) to avoid a mid-afternoon energy crash.", "#f59e0b", "#fffbeb"))
    if w_stress >= 7.5:
        all_recs.append((90, "🧘", "Elevated stress — take recovery time",
            f"Stress at {w_stress:.1f}/10 is significantly above your baseline ({BASELINE['stress']}/10). Block 10–15 minutes mid-morning for a screen-free recovery window.", "#ef4444", "#fef2f2"))
    elif w_stress >= 5.5:
        all_recs.append((60, "🧘", "Moderate stress level",
            f"Stress at {w_stress:.1f}/10. Avoid stacking back-to-back meetings — a 10-min gap between calls helps your nervous system reset.", "#f59e0b", "#fffbeb"))
    if w_hr > 90:
        all_recs.append((75, "💓", "Elevated resting heart rate",
            f"Resting HR of {w_hr} bpm is {w_hr - BASELINE['hr']} bpm above your baseline. This often indicates residual stress. Prioritise light work only.", "#ef4444", "#fef2f2"))
    if w_sed > 180:
        all_recs.append((80, "🪑", "Prolonged sedentary period",
            f"Seated for {w_sed} min. Set a recurring 5-min movement break every hour — even a short walk improves circulation and focus by up to 15%.", "#6366f1", "#eef2ff"))
    elif w_sed > 90:
        all_recs.append((45, "🪑", "Moderate sedentary time",
            f"{w_sed} min without movement. Aim for a 3–5 min stretch between your next two meetings.", "#9ca3af", "#f9fafb"))
    if w_steps < 3000:
        all_recs.append((55, "👟", "Low step count",
            f"Only {w_steps:,} steps so far. A 15-min walk during lunch would significantly boost your afternoon energy and mood.", "#6366f1", "#eef2ff"))

    all_recs.sort(key=lambda x: x[0], reverse=True)
    top_recs = all_recs[:3]
    if not top_recs:
        st.markdown('''
        <div style="background:#f0fdf4;border:1px solid #bbf7d0;border-radius:12px;
                    padding:1.25rem 1.5rem;color:#065f46;font-weight:500;">
            ✅ All biometric indicators are within healthy ranges. Physiological conditions are optimal for high-stakes cognitive work today.
        </div>''', unsafe_allow_html=True)
    else:
        rec_cols = st.columns(len(top_recs))
        for i, (_, icon, title, msg, col, bg) in enumerate(top_recs):
            with rec_cols[i]:
                st.markdown(f'''
                <div style="background:{bg};border-left:4px solid {col};border-radius:12px;
                            padding:1.2rem;height:100%;box-shadow:0 2px 6px rgba(0,0,0,0.05);">
                    <div style="font-size:1.4rem;margin-bottom:0.4rem;">{icon}</div>
                    <div style="font-size:0.88rem;font-weight:700;color:#111827;margin-bottom:0.5rem;">{title}</div>
                    <div style="font-size:0.82rem;color:#374151;line-height:1.5;">{msg}</div>
                </div>''', unsafe_allow_html=True)

    # ── Profile Conflict flags ────────────────────────────────────────────────
    st.markdown("<br>", unsafe_allow_html=True)
    profile_name_saved = user_data.get('profile_name', None)
    conflict_flags = []
    if readiness_label == "Low":
        conflict_flags.append(("⚠️ Low readiness detected",
            "Your recovery score suggests today is not suitable for heavy cognitive work. If your calendar has back-to-back meetings, consider declining the lowest-priority ones.", "#f59e0b", "#fffbeb"))
    if w_fatigue >= 7 and w_sleep < 6.5:
        conflict_flags.append(("🚨 High fatigue + poor sleep combination",
            "This is the highest-risk pattern for afternoon decision fatigue. Avoid scheduling complex analyses or important presentations after 14:00.", "#ef4444", "#fef2f2"))
    if profile_name_saved and "Overworked" in profile_name_saved and w_fatigue >= 6:
        conflict_flags.append(("🔴 Profile conflict — Overworked & Exhausted",
            f"Your saved profile ({profile_name_saved}) already flags you as high-risk. Today's fatigue score reinforces this — enforce a hard stop at your usual leaving time.", "#ef4444", "#fef2f2"))
    if conflict_flags:
        st.markdown('<div class="section-header">Calendar & Profile Conflicts</div>', unsafe_allow_html=True)
        for flag_title, flag_msg, flag_col, flag_bg in conflict_flags:
            st.markdown(f'''
            <div style="background:{flag_bg};border-left:4px solid {flag_col};border-radius:10px;
                        padding:1rem 1.25rem;margin-bottom:10px;">
                <div style="font-weight:700;color:#111827;margin-bottom:0.3rem;">{flag_title}</div>
                <div style="font-size:0.85rem;color:#374151;">{flag_msg}</div>
            </div>''', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.caption("Prototype: all metrics are manually simulated. In a production build, this section would ingest live data from Apple Health, Google Fit, or WHOOP via API.")


# ══════════════════════════════════════════════════════════════════════════════
# PROFILE INSIGHTS  (unchanged)
# ══════════════════════════════════════════════════════════════════════════════
elif menu == "Profile Insights":
    st.markdown('<div class="header-style">Profile Insights</div>', unsafe_allow_html=True)
    st.markdown('<div class="subheader-style">Explore your habits, clustering profiles, and dataset analytics.</div>', unsafe_allow_html=True)

    action = st.radio("", ["Discover Your Person Type", "Explore Data Clusters", "Data Explorer"], horizontal=True)
    st.markdown("---")

    if action == "Discover Your Person Type":
        st.markdown('<div class="section-header">Discover Your Person Type</div>', unsafe_allow_html=True)
        st.markdown("Input your current habits to see which profile you match and get a tailored action plan.")
        final_k = 3
        final_scaler, final_kmeans, _, _, final_profiles = perform_clustering(df, cluster_features, final_k)
        saved = user_data.get('profile_inputs', {})

        col1, col2 = st.columns(2)
        with col1:
            c_work    = st.slider("Work Hours",            0.0, 16.0,  saved.get('work_hours', 8.0))
            c_meet    = st.slider("Number of Meetings",    0,   15,    saved.get('meetings_count', 3))
            c_breaks  = st.slider("Breaks Taken",          0,   10,    saved.get('breaks_taken', 3))
            c_tasks   = st.slider("Task Completion (%)",   0.0, 100.0, saved.get('task_completion', 80.0))
        with col2:
            c_after   = st.checkbox("Work after hours?",   value=bool(saved.get('after_hours_work', 0)))
            c_switches= st.slider("App Switches",          0,   150,   saved.get('app_switches', 50))
            c_sleep   = st.slider("Sleep Hours",           3.0, 12.0,  saved.get('sleep_hours', 7.0))
            c_iso     = st.slider("Isolation Index (1-10)",1,   10,    saved.get('isolation_index', 5))
            c_fatigue = st.slider("Fatigue Score (0-10)",  0.0, 10.0,  saved.get('fatigue_score', 5.0))

        if st.button("Analyze My Habits"):
            after_val = 1 if c_after else 0
            c_burnout = round(min(10.0, max(0.0, c_fatigue * 0.6 + max(0, c_work - 7) * 0.35)), 2)
            raw_input_dict = {
                'work_hours': [c_work], 'meetings_count': [c_meet], 'breaks_taken': [c_breaks],
                'after_hours_work': [after_val], 'app_switches': [c_switches], 'sleep_hours': [c_sleep],
                'task_completion': [c_tasks], 'isolation_index': [c_iso],
                'fatigue_score': [c_fatigue], 'burnout_score': [c_burnout]
            }
            input_data        = pd.DataFrame(raw_input_dict)[cluster_features]
            scaled_input      = final_scaler.transform(input_data)
            cluster_assignment= final_kmeans.predict(scaled_input)[0]
            distances         = final_kmeans.transform(scaled_input)[0]
            inv_dists         = 1 / (distances + 1e-5)
            confidence        = (inv_dists[cluster_assignment] / np.sum(inv_dists)) * 100
            assigned_profile  = final_profiles[cluster_assignment]
            profile_name_val  = assigned_profile['name'].split(':')[1].strip()

            users = load_users()
            users[st.session_state['user_email']]['profile_name']   = profile_name_val
            users[st.session_state['user_email']]['profile_inputs'] = {
                'work_hours': c_work, 'meetings_count': c_meet, 'breaks_taken': c_breaks,
                'after_hours_work': after_val, 'app_switches': c_switches, 'sleep_hours': c_sleep,
                'task_completion': c_tasks, 'isolation_index': c_iso, 'fatigue_score': c_fatigue,
            }
            users[st.session_state['user_email']]['profile_result'] = {
                'cluster_assignment': int(cluster_assignment), 'confidence': round(float(confidence), 1),
                'profile_name': profile_name_val, 'suggestion': assigned_profile['suggestion'],
            }
            save_users(users)
            st.rerun()

        saved_result = user_data.get('profile_result', None)
        if saved_result:
            final_k = 3
            _, _, _, final_centroids, _ = perform_clustering(df, cluster_features, final_k)
            cluster_assignment = saved_result['cluster_assignment']
            profile_avgs       = final_centroids.iloc[cluster_assignment]
            profile_name_disp  = saved_result['profile_name']
            confidence         = saved_result['confidence']
            suggestion         = saved_result['suggestion']
            saved_inputs       = user_data.get('profile_inputs', {})

            st.markdown("---")
            st.markdown('<div class="section-header">Your Work Profile Analysis</div>', unsafe_allow_html=True)
            st.markdown(f'''
            <div style="background:#f8fafc;border-left:5px solid #3b82f6;border-radius:8px;
                        padding:1.5rem;margin-top:1rem;box-shadow:0 4px 6px -1px rgba(0,0,0,0.05);">
                <h2 style="margin-top:0;color:#111827;">{profile_name_disp}</h2>
                <p style="font-size:1.05rem;color:#4b5563;margin-bottom:0;">
                    <strong>Match Confidence:</strong>
                    <span style="color:#10b981;font-weight:bold;">{confidence:.1f}%</span>
                    &nbsp;&nbsp;·&nbsp;&nbsp;
                    <span style="font-size:0.85rem;color:#9ca3af;">Last analysed with your saved inputs — adjust sliders and click Analyze to update.</span>
                </p>
            </div>''', unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)
            col_m1, col_m2 = st.columns(2)
            with col_m1:
                st.markdown("#### Why You Matched")
                st.markdown("Key inputs vs. profile centroid averages:")
                for var in ['work_hours', 'sleep_hours', 'fatigue_score', 'meetings_count']:
                    usr_val = saved_inputs.get(var, 0)
                    avg_val = profile_avgs[var]
                    diff    = usr_val - avg_val
                    trend   = "↑" if diff > 0 else "↓" if diff < 0 else "="
                    c_color = "red" if (var in ['work_hours', 'fatigue_score'] and diff > 0) \
                                    or (var == 'sleep_hours' and diff < 0) else "green"
                    st.markdown(f"**{var.replace('_', ' ').title()}:**")
                    st.markdown(f"↳ You: `{usr_val:.1f}` | Profile Avg: `{avg_val:.1f}` "
                                f"<span style='color:{c_color};font-weight:bold;'>{trend}</span>",
                                unsafe_allow_html=True)
            with col_m2:
                st.markdown("#### Tailored Action Plan")
                st.info(f"As a **{profile_name_disp}**, the model recommends the following:")
                st.markdown(suggestion)

    elif action == "Explore Data Clusters":
        with st.container():
            st.header("👥 Person Profiles Overview")
            st.markdown(f"Based on the data, employees fall into **{n_clusters_choice} distinct behavioral types**.")
            final_k = n_clusters_choice
            scaler_temp, kmeans_temp, labels_temp, centroids_temp, profiles_temp = perform_clustering(df, cluster_features, final_k)
            for idx in range(final_k):
                profile = profiles_temp[idx]
                with st.expander(f"**{profile['name']}**", expanded=True):
                    st.markdown(profile['suggestion'])
            st.markdown("---")
            st.subheader("📊 Cluster Characteristics")
            st.markdown("Average behaviors per profile type:")
            display_features = list(dict.fromkeys(['work_hours', 'sleep_hours', 'fatigue_score', 'burnout_score']))
            stat_df = df.copy(); stat_df['Cluster'] = labels_temp
            valid_features   = [c for c in display_features if c in stat_df.columns]
            cluster_summary  = stat_df.groupby('Cluster')[valid_features].mean()
            cluster_summary.index = [profiles_temp[i]['name'] for i in range(final_k)]
            if cluster_summary.columns.is_unique and cluster_summary.index.is_unique:
                st.dataframe(cluster_summary.style.highlight_max(axis=0, color='#fca5a5').highlight_min(axis=0, color='#bbf7d0'), use_container_width=True)
            else:
                st.dataframe(cluster_summary, use_container_width=True)
            st.markdown("---")
            st.subheader("🔍 Cluster Visualization")
            temp_df = df.copy(); temp_df['Cluster'] = labels_temp
            temp_df['Person Type'] = temp_df['Cluster'].apply(lambda x: profiles_temp[x]['name'])
            v_col1, v_col2 = st.columns([1, 2])
            with v_col1:
                x_axis = st.selectbox("X-Axis", display_features, index=0)
                y_axis = st.selectbox("Y-Axis", display_features, index=2)
                st.markdown("### ⚖️ Profile Comparison")
                st.info("🔹 **Type 0:** The primary profile, typically representing the most common behavioral pattern.")
                st.success("🔹 **Type 1:** Represents the first significant behavioral deviation from the norm.")
                st.warning("🔹 **Type 2:** Usually captures edge cases like extreme work hours or sleep deprivation.")
                if final_k > 3:
                    st.error("🔹 **Type 3:** Captures highly specific sub-patterns only visible at higher cluster resolutions.")
            with v_col2:
                fig, ax = plt.subplots(figsize=(7, 4))
                colors  = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444']
                sns.scatterplot(data=temp_df, x=x_axis, y=y_axis, hue='Person Type', ax=ax, palette=colors[:final_k])
                ax.set_xlabel(x_axis.replace('_', ' ').title())
                ax.set_ylabel(y_axis.replace('_', ' ').title())
                st.pyplot(fig)

    elif action == "Data Explorer":
        with st.container():
            st.header("📊 Behavior Insights Dashboard")
            st.markdown("Explore key trends and behavioral patterns in the remote work dataset.")
            st.subheader("📌 Dataset Overview")
            num_rows    = df.shape[0]; num_cols = df.shape[1]
            num_numeric = len(df.select_dtypes(include=[np.number]).columns)
            num_cat     = len(df.select_dtypes(exclude=[np.number]).columns)
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Total Rows", num_rows); c2.metric("Total Columns", num_cols)
            c3.metric("Numerical Vars", num_numeric); c4.metric("Categorical Vars", num_cat)
            with st.expander("Show raw dataset preview"):
                st.dataframe(df.head(10), use_container_width=True)
            st.markdown("---")
            st.subheader("🛡️ Data Quality Snapshot")
            missing_count   = df.isnull().sum().sum()
            duplicate_count = df.duplicated().sum()
            dq1, dq2 = st.columns(2)
            if missing_count > 0:   dq1.warning(f"⚠️ **{missing_count}** missing values detected.")
            else:                   dq1.success("✅ **0** missing values detected.")
            if duplicate_count > 0: dq2.warning(f"⚠️ **{duplicate_count}** duplicate rows detected.")
            else:                   dq2.success("✅ **0** duplicate rows detected.")
            st.markdown("---")
            st.subheader("📈 Key Behavioral Patterns")
            p1, p2 = st.columns(2)
            with p1:
                st.markdown("**A. Work Hours Distribution**")
                fig1, ax1 = plt.subplots(figsize=(6, 4))
                sns.histplot(data=df, x='work_hours', bins=20, kde=True, color='#3b82f6', ax=ax1)
                ax1.set_xlabel("Work Hours"); ax1.set_ylabel("Count"); st.pyplot(fig1)
                st.markdown("**C. Fatigue vs Burnout**")
                fig3, ax3 = plt.subplots(figsize=(6, 4))
                sns.scatterplot(data=df, x='fatigue_score', y='burnout_score', alpha=0.6, color='#ef4444', ax=ax3)
                ax3.set_xlabel("Fatigue Score"); ax3.set_ylabel("Burnout Score"); st.pyplot(fig3)
            with p2:
                st.markdown("**B. Sleep Hours Distribution**")
                fig2, ax2 = plt.subplots(figsize=(6, 4))
                sns.histplot(data=df, x='sleep_hours', bins=20, kde=True, color='#10b981', ax=ax2)
                ax2.set_xlabel("Sleep Hours"); ax2.set_ylabel("Count"); st.pyplot(fig2)
                st.markdown("**D. Work Hours vs Fatigue**")
                fig4, ax4 = plt.subplots(figsize=(6, 4))
                sns.scatterplot(data=df, x='work_hours', y='fatigue_score', alpha=0.6, color='#f59e0b', ax=ax4)
                ax4.set_xlabel("Work Hours"); ax4.set_ylabel("Fatigue Score"); st.pyplot(fig4)
            st.markdown("---")
            st.subheader("💡 Key Insights Summary")
            avg_work = df['work_hours'].mean(); avg_sleep = df['sleep_hours'].mean()
            avg_fatigue = df['fatigue_score'].mean(); avg_burnout = df['burnout_score'].mean()
            k1, k2, k3, k4 = st.columns(4)
            k1.metric("Avg Work Hours",  f"{avg_work:.1f} hr")
            k2.metric("Avg Sleep Hours", f"{avg_sleep:.1f} hr")
            k3.metric("Avg Fatigue",     f"{avg_fatigue:.1f} / 10")
            k4.metric("Avg Burnout",     f"{avg_burnout:.1f} / 100")
            st.info("📌 **Observation:** Higher work hours are intrinsically linked to elevated fatigue. Guaranteeing 7+ hours of sleep per night acts as the most aggressive buffer against compounding burnout scores.")
