import streamlit as st
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
from icalendar import Calendar
from datetime import datetime, time
import pickle
import warnings
import json
import os
import hashlib

warnings.filterwarnings('ignore')
st.set_page_config(page_title="FlowState Productivity", layout="wide", page_icon="⚡")
st.markdown('''
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
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
</style>
''', unsafe_allow_html=True)

USER_FILE = 'user_data/users.json'

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def load_users():
    if not os.path.exists('user_data'):
        os.makedirs('user_data')
    if not os.path.exists(USER_FILE):
        return {}
    with open(USER_FILE, 'r') as f:
        return json.load(f)

def save_users(users):
    with open(USER_FILE, 'w') as f:
        json.dump(users, f)

if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
if 'user_email' not in st.session_state:
    st.session_state['user_email'] = ""

if not st.session_state['logged_in']:
    # Hero / login page
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
            email = st.text_input("Email address", key="login_email", placeholder="you@example.com")
            password = st.text_input("Password", type="password", key="login_pass", placeholder="••••••••")
            if st.button("Sign In", use_container_width=True, key="btn_login"):
                users = load_users()
                if email in users and users[email]['password'] == hash_password(password):
                    st.session_state['logged_in'] = True
                    st.session_state['user_email'] = email
                    st.rerun()
                else:
                    st.error("Incorrect email or password.")
        with tab2:
            new_email = st.text_input("Email address", key="signup_email", placeholder="you@example.com")
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
                        'tasks': [],
                        'profile': {}
                    }
                    save_users(users)
                    st.success("Account created! Sign in to continue.")
    st.stop()

# ── Sidebar branding & navigation ──────────────────────────────────────────
user_initials = st.session_state['user_email'][:2].upper()
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
            <div style="font-size:0.78rem;color:#94a3b8;">Signed in as</div>
            <div style="font-size:0.82rem;color:#e2e8f0;font-weight:600;word-break:break-all;">{st.session_state['user_email']}</div>
        </div>
    </div>
''', unsafe_allow_html=True)
menu = st.sidebar.radio(
    "Navigation",
    [
        "Dashboard",
        "Task Prioritization",
        "Calendar Analyzer",
        "Wearable & Recovery",
        "Profile Insights"
    ],
    label_visibility="collapsed"
)

# Sidebar cluster settings if needed
if menu == "Profile Insights":
    st.sidebar.markdown("---")
    st.sidebar.markdown("**Model Settings**")
    n_clusters_choice = st.sidebar.radio(
        "Clusters:",
        options=[3, 4],
        index=0,
        help="Choose between 3 or 4 clusters"
    )

st.sidebar.markdown("---")
if st.sidebar.button("Sign Out", use_container_width=True):
    st.session_state['logged_in'] = False
    st.session_state['user_email'] = ""
    st.rerun()

users = load_users()

# Safety check: ensure user is logged in before accessing user_data
if not st.session_state['logged_in'] or not st.session_state['user_email']:
    st.warning("Please log in to continue.")
    st.stop()

if st.session_state['user_email'] not in users:
    users[st.session_state['user_email']] = {'tasks': [], 'profile_name': None, 'profile_result': {}, 'profile_inputs': {}}
    save_users(users)

user_data = users[st.session_state['user_email']]

# --------- Model & Utils Injection ---------

# ==========================================
# 1. MODEL & DATA LOADING
# ==========================================
@st.cache_resource
def load_model_data():
    """Loads the pre-trained model payload, including scaler, KMeans, features, and dataset."""
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


# ==========================================
# 2. CLUSTERING UTILITIES
# ==========================================

# NOTE: I removed the duplicate load_trained_model() from here! 
# It is already correctly defined at the top of your file.

@st.cache_data
def get_cluster_info(_scaler, _kmeans, data, features, n_clusters=3):
    """
    Extracts explicit data outputs (labels, centroids, profiles) safely.
    If n_clusters differs from the pre-trained model, it dynamically fits a new one.
    """
    scaled_data = _scaler.transform(data[features])
    
    if _kmeans.n_clusters != n_clusters:
        dynamic_kmeans = KMeans(n_clusters=n_clusters, random_state=42)
        dynamic_kmeans.fit(scaled_data)
        labels = dynamic_kmeans.predict(scaled_data)
        centroids = _scaler.inverse_transform(dynamic_kmeans.cluster_centers_)
        used_kmeans = dynamic_kmeans
    else:
        labels = _kmeans.predict(scaled_data)
        centroids = _scaler.inverse_transform(_kmeans.cluster_centers_)
        used_kmeans = _kmeans
    
    centroid_df = pd.DataFrame(centroids, columns=features)
    
    cluster_profiles = {}
    for i in range(n_clusters):
        work = centroid_df.loc[i, 'work_hours']
        sleep = centroid_df.loc[i, 'sleep_hours']
        fatigue = centroid_df.loc[i, 'fatigue_score']
        
        # Detailed naming and 6-month plans based on heuristics
        if fatigue > 6.5 and work > 9:
            name = "The Overworked & Exhausted"
            sugg = """🚨 **Status Review:** You are pushing dangerous hours and experiencing high fatigue. Immediate action is needed.
            
📅 **6-Month Improvement Plan:**
* **Months 1-2:** **Establish Boundaries.** Set a hard stop at 8 working hours. No after-hours emails. Start practicing a 30-minute wind-down routine before sleep without screens.
* **Months 3-4:** **Rebalance & Delegate.** Target consistent 7.5+ hour sleep schedules. Begin taking 10-minute micro-breaks every 90 minutes of work. If workload is impossible, actively delegate or drop non-essential meetings.
* **Months 5-6:** **Sustainable Rhythm.** Your fatigue should be dropping. Reintroduce a hobby or daily exercise. Maintain strict barriers between 'home' space and 'work' space to permanently lower burnout risk."""
        elif fatigue < 5 and sleep > 7:
            name = "The Balanced Worker"
            sugg = """✅ **Status Review:** Excellent! You maintain a strong functional balance between rest and work without sacrificing health.
            
📅 **6-Month Improvement Plan:**
* **Months 1-2:** **Solidify Routine.** Ensure your current sleep/work schedule is documented and protected from creeping meeting hours. 
* **Months 3-4:** **Optimize Focus.** Try batching your tasks to avoid app-switching fatigue, aiming for "deep work" blocks of 2 hours, followed by substantial offline breaks.
* **Months 5-6:** **Prevent Stagnation.** Having low burnout is great, but ensure you remain engaged. Pick up a low-stress learning opportunity or mentor someone else on how to achieve this balance!"""
        elif sleep < 6.5 and work <= 9:
            name = "The Sleep-Deprived"
            sugg = """🛌 **Status Review:** While your work hours are manageable, your sleep duration is unhealthy. This limits your recovery and fuels background fatigue.

📅 **6-Month Improvement Plan:**
* **Months 1-2:** **Sleep Hygiene.** Move all screens out of the bedroom. Go to bed 15 minutes earlier every week until you hit a 7-8 hour window. Reduce caffeine after 2 PM.
* **Months 3-4:** **Morning Optimization.** With better sleep, start a consistent morning routine before logging into work. Use the morning for 20 minutes of natural sunlight to reset your circadian rhythm.
* **Months 5-6:** **Performance Review.** As sleep stabilizes, you should notice sharper focus and faster task completion. Track if your App Switches decrease and actively defend your new sleep schedule."""
        elif work > 9 and fatigue <= 6.5:
            name = "The High-Achiever"
            sugg = """🔥 **Status Review:** You are working long hours but somehow managing the fatigue—for now. This phase is often the precursor to sudden burnout.

📅 **6-Month Improvement Plan:**
* **Months 1-2:** **Strategic Pullback.** Reduce meetings by 20% (decline non-essential invites). You are overworking; aim to shave 1 hour off your workday immediately by prioritizing high-impact tasks.
* **Months 3-4:** **Active Recovery.** Introduce forcing functions: schedule a mandatory 45-minute lunch away from the desk. Start logging off immediately when your core tasks are done, rather than 'finding' more work to fill the time.
* **Months 5-6:** **Efficiency over Volume.** Reduce work hours to 8.5/day. Focus entirely on task completion rates rather than time spent at the desk. You will find you produce the same quality in less time."""
        else:
            name = "The Moderate / Undefined"
            sugg = """☕ **Status Review:** You fall into a middle-ground pattern. Your habits aren't severely dangerous, but there is room to optimize your daily energy.

📅 **6-Month Improvement Plan:**
* **Months 1-2:** **Audit Your Days.** Spend 2 weeks tracking what exactly makes you tired (Is it specific meetings? App switching? Evening emails?). Start minimizing those specific triggers.
* **Months 3-4:** **Introduce Rhythm.** Adopt the Pomodoro technique (25 mins work, 5 mins rest) to ensure you aren't staring at screens for hours uninterrupted. Seek out 1 daily social interaction to combat isolation.
* **Months 5-6:** **Targeted Adjustment.** Depending on how your audit went, focus either on raising your sleep by 30 minutes or dropping your daily working hours by 45 minutes to find your personal sweet spot."""
            
        cluster_profiles[i] = {"name": f"Type {i}: {name}", "suggestion": sugg}
        
    return labels, centroid_df, cluster_profiles, used_kmeans

def perform_clustering(data, features, n_clusters):
    """
    Wrapper function to provide all variables cleanly using the pre-trained model or dynamically fitted model.
    """
    labels, centroid_df, profiles, used_kmeans = get_cluster_info(scaler, kmeans, data, features, n_clusters)
    return scaler, used_kmeans, labels, centroid_df, profiles


# ==========================================
# 3. UI TABS & HIGH-LEVEL STRUCTURE
# ==========================================

if menu == "Dashboard":
    # ── Pull saved data ───────────────────────────────────────────────────────
    all_tasks     = user_data.get('tasks', [])
    pending_tasks = [t for t in all_tasks if t['status'] == 'Pending']
    done_tasks    = [t for t in all_tasks if t['status'] == 'Completed']
    high_tasks    = [t for t in pending_tasks if t['priority'] == 'High']
    profile_name  = user_data.get('profile_name', None)
    profile_result= user_data.get('profile_result', {})
    profile_inputs= user_data.get('profile_inputs', {})

    # ── Header ────────────────────────────────────────────────────────────────
    greeting_hour = datetime.now().hour
    greeting = "Good morning" if greeting_hour < 12 else ("Good afternoon" if greeting_hour < 18 else "Good evening")
    user_first = st.session_state['user_email'].split('@')[0].split('.')[0].capitalize()

    st.markdown(f'<div class="header-style">{greeting}, {user_first}</div>', unsafe_allow_html=True)
    st.markdown('<div class="subheader-style">Here is your productivity snapshot for today.</div>', unsafe_allow_html=True)

    # ── Top KPI strip ─────────────────────────────────────────────────────────
    pct = round(len(done_tasks) / max(1, len(all_tasks)) * 100)
    k1, k2, k3, k4 = st.columns(4)
    def mini_kpi(label, value, sub, accent="#2563eb"):
        return f'''<div style="background:#fff;border-radius:12px;padding:1.1rem 1.25rem;
                   border:1px solid #e5e7eb;box-shadow:0 2px 6px rgba(0,0,0,0.04);">
            <div style="font-size:0.7rem;font-weight:700;color:#6b7280;text-transform:uppercase;
                        letter-spacing:0.06em;margin-bottom:0.35rem;">{label}</div>
            <div style="font-size:1.7rem;font-weight:800;color:{accent};line-height:1;">{value}</div>
            <div style="font-size:0.75rem;color:#9ca3af;margin-top:0.2rem;">{sub}</div>
        </div>'''

    with k1: st.markdown(mini_kpi("Pending Tasks",    len(pending_tasks), f"{len(high_tasks)} high priority", "#2563eb"), unsafe_allow_html=True)
    with k2: st.markdown(mini_kpi("Completed",        len(done_tasks),    f"of {len(all_tasks)} total",       "#10b981"), unsafe_allow_html=True)
    with k3: st.markdown(mini_kpi("Completion Rate",  f"{pct}%",          "tasks resolved",                   "#6366f1"), unsafe_allow_html=True)
    with k4:
        conf = profile_result.get('confidence', None)
        conf_str = f"{conf:.0f}% match" if conf else "Not analysed"
        st.markdown(mini_kpi("Profile Confidence", conf_str, profile_name or "Run Profile Insights", "#f59e0b"), unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Pull saved calendar data ──────────────────────────────────────────────
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
                    'End': datetime.fromisoformat(ev['End']),
                    'Duration (mins)': ev['Duration (mins)'],
                    'Date': datetime.fromisoformat(ev['Date']).date()
                })
            st.session_state['calendar_events'] = loaded_events
            st.session_state['calendar_filename'] = user_data.get('calendar_filename', "Saved Calendar.ics")
            active_events = loaded_events

    has_calendar = len(active_events) > 0
    if has_calendar:
        import pandas as pd
        event_df = pd.DataFrame(active_events)
        event_df = event_df.sort_values('Start').reset_index(drop=True)
        dates = event_df['Date'].unique()
        num_days = len(dates)
        
        preferred_start_time = time(9, 0)
        earliest_leave_time = time(17, 0)
        
        # 1. Focus Score
        large_blocks_count = 0
        total_free_mins = 0
        for d in dates:
            day_events = event_df[event_df['Date'] == d].sort_values('Start')
            day_start = datetime.combine(d, preferred_start_time)
            day_end = datetime.combine(d, earliest_leave_time)
            
            last_end_tracker = day_start
            for _, row in day_events.iterrows():
                ev_start = max(day_start, row['Start'])
                ev_end = min(day_end, row['End'])
                if ev_start > ev_end: 
                    ev_start, ev_end = ev_end, ev_start
                    
                if ev_start > last_end_tracker:
                    gap = (ev_start - last_end_tracker).total_seconds() / 60.0
                    total_free_mins += gap
                    if gap >= 60: large_blocks_count += 1
                    
                last_end_tracker = max(last_end_tracker, ev_end)
                
            if last_end_tracker < day_end:
                gap = (day_end - last_end_tracker).total_seconds() / 60.0
                total_free_mins += gap
                if gap >= 60: large_blocks_count += 1
                
        focus_score = round(min(10.0, (large_blocks_count / max(1, num_days)) * 3), 1)
        
        # 2. Busiest Day
        meetings_per_day = event_df.groupby('Date').size()
        busiest_day_date = meetings_per_day.idxmax()
        busiest_day_str = busiest_day_date.strftime('%a') # e.g. Mon, Tue
        
        # 3. Free Blocks
        free_blocks_str = f"{large_blocks_count} blocks"
        
        # 4. Late Meetings
        late_meetings_count = len(event_df[event_df['End'].dt.time > earliest_leave_time])
        late_meetings_str = f"{late_meetings_count} meetings"
        
        cal_status_txt = "Active"
        cal_status_bg = "#dcfce7"
        cal_status_color = "#15803d"
        cal_desc = f"Analyzing <b>{st.session_state.get('calendar_filename', 'Saved Calendar')}</b> with {len(event_df)} events this week."
    else:
        focus_score = "—"
        busiest_day_str = "—"
        free_blocks_str = "—"
        late_meetings_str = "—"
        cal_status_txt = "Upload to activate"
        cal_status_bg = "#eff6ff"
        cal_status_color = "#2563eb"
        cal_desc = "Upload your <strong>.ics calendar file</strong> to unlock your weekly schedule analysis, focus block scoring, meeting load, and daily recommendations."

    # ── Three main panels ─────────────────────────────────────────────────────
    p1, p2, p3 = st.columns(3)

    # ── Panel 1: Work Profile ─────────────────────────────────────────────────
    with p1:
        has_profile = bool(profile_result)
        accent = "#6366f1"
        if has_profile:
            pname  = profile_result.get('profile_name', 'Unknown')
            pconf  = profile_result.get('confidence', 0)
            p_work = profile_inputs.get('work_hours', '—')
            p_slp  = profile_inputs.get('sleep_hours', '—')
            p_fat  = profile_inputs.get('fatigue_score', '—')

            # Map profile name to a short descriptor
            if "Overworked" in pname:    desc, status_col, status_txt = "High workload + fatigue pattern detected.", "#ef4444", "At Risk"
            elif "Balanced" in pname:    desc, status_col, status_txt = "Healthy work-life equilibrium maintained.", "#10b981", "Optimal"
            elif "Sleep" in pname:       desc, status_col, status_txt = "Sleep deprivation affecting recovery.",      "#f59e0b", "Watch"
            elif "High-Achiever" in pname: desc, status_col, status_txt = "High output — monitor burnout risk.",      "#f59e0b", "Caution"
            else:                        desc, status_col, status_txt = "Mixed patterns — room to optimise.",         "#9ca3af", "Moderate"

            st.markdown(f'''
            <div style="background:#fff;border-radius:14px;padding:1.5rem;border:1px solid #e5e7eb;
                        box-shadow:0 2px 8px rgba(0,0,0,0.05);height:100%;">
                <div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:1rem;">
                    <div style="font-size:0.72rem;font-weight:700;color:#6b7280;text-transform:uppercase;
                                letter-spacing:0.07em;">Work Profile</div>
                    <span style="background:{status_col}20;color:{status_col};font-size:0.7rem;
                                 font-weight:700;padding:2px 10px;border-radius:20px;">{status_txt}</span>
                </div>
                <div style="font-size:1.05rem;font-weight:700;color:#111827;margin-bottom:0.4rem;
                            border-left:3px solid {accent};padding-left:0.6rem;">{pname}</div>
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
                <div style="font-size:0.75rem;color:#9ca3af;">
                    Match confidence: <strong style="color:{accent};">{pconf:.0f}%</strong>
                    &nbsp;·&nbsp; ML clustering model (K=3)
                </div>
            </div>''', unsafe_allow_html=True)
        else:
            st.markdown(f'''
            <div style="background:#fff;border-radius:14px;padding:1.5rem;border:1px solid #e5e7eb;
                        box-shadow:0 2px 8px rgba(0,0,0,0.05);height:100%;">
                <div style="font-size:0.72rem;font-weight:700;color:#6b7280;text-transform:uppercase;
                            letter-spacing:0.07em;margin-bottom:1rem;">Work Profile</div>
                <div style="color:#9ca3af;font-size:0.9rem;margin-bottom:0.75rem;">
                    No profile analysed yet.
                </div>
                <div style="font-size:0.82rem;color:#6b7280;">
                    Go to <strong>Profile Insights → Discover Your Person Type</strong>
                    and click Analyze My Habits to get your ML-matched work profile.
                </div>
            </div>''', unsafe_allow_html=True)

    # ── Panel 2: Calendar Overview ────────────────────────────────────────────
    with p2:
        accent2 = "#2563eb"
        st.markdown(f'''
        <div style="background:#fff;border-radius:14px;padding:1.5rem;border:1px solid #e5e7eb;
                    box-shadow:0 2px 8px rgba(0,0,0,0.05);height:100%;">
            <div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:1rem;">
                <div style="font-size:0.72rem;font-weight:700;color:#6b7280;text-transform:uppercase;
                            letter-spacing:0.07em;">Calendar Analyzer</div>
                <span style="background:{cal_status_bg};color:{cal_status_color};font-size:0.7rem;
                             font-weight:700;padding:2px 10px;border-radius:20px;">{cal_status_txt}</span>
            </div>
            <div style="font-size:1rem;font-weight:600;color:#111827;margin-bottom:0.5rem;">
                Schedule Health Overview
            </div>
            <div style="font-size:0.82rem;color:#6b7280;margin-bottom:1.1rem;min-height:3.6rem;line-height:1.4;">
                {cal_desc}
            </div>
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
            <div style="font-size:0.75rem;color:#9ca3af;">
                Navigate to <strong>Calendar Analyzer</strong> to upload and analyse your schedule.
            </div>
        </div>''', unsafe_allow_html=True)

    # ── Panel 3: Wearable / Recovery ──────────────────────────────────────────
    with p3:
        accent3 = "#10b981"
        # Show last-session wearable defaults as a preview
        # (sliders default to 6.5h sleep, 62 stress, etc. — same as the Wearable page)
        w_prev_sleep   = 6.5
        w_prev_fatigue = 7
        w_prev_stress  = 62
        w_prev_steps   = 4200

        # Recompute a quick recovery score from defaults
        _sl = max(0, min(100, (w_prev_sleep  - 4) * 25))
        _st = max(0, min(100, 100 - w_prev_stress))
        _ft = max(0, min(100, (10 - w_prev_fatigue) * 11.1))
        _ac = max(0, min(100, w_prev_steps / 100))
        _rs = round(_sl * 0.40 + _st * 0.25 + _ft * 0.25 + _ac * 0.10)

        if   _rs >= 67: _rl, _rc = "Optimal",  "#10b981"
        elif _rs >= 34: _rl, _rc = "Moderate", "#f59e0b"
        else:           _rl, _rc = "Low",      "#ef4444"

        def small_metric(icon, label, val, col="#374151"):
            return f'''<div style="display:flex;align-items:center;gap:8px;padding:0.5rem 0;
                                   border-bottom:1px solid #f3f4f6;">
                <span style="font-size:1rem;">{icon}</span>
                <span style="font-size:0.82rem;color:#6b7280;flex:1;">{label}</span>
                <span style="font-size:0.88rem;font-weight:700;color:{col};">{val}</span>
            </div>'''

        s_label = "Low" if w_prev_stress < 34 else ("Medium" if w_prev_stress < 67 else "High")
        s_col   = "#10b981" if w_prev_stress < 34 else ("#f59e0b" if w_prev_stress < 67 else "#ef4444")

        rows = (
            small_metric("🌙", "Sleep",         f"{w_prev_sleep}h",      "#6366f1" if w_prev_sleep >= 7 else "#ef4444") +
            small_metric("🔋", "Morning Fatigue",f"{w_prev_fatigue}/10",  "#ef4444" if w_prev_fatigue >= 7 else "#10b981") +
            small_metric("🧘", "Stress",         s_label,                 s_col) +
            small_metric("👟", "Steps",          f"{w_prev_steps:,}",     "#10b981" if w_prev_steps >= 5000 else "#f59e0b")
        )

        st.markdown(f'''
        <div style="background:#fff;border-radius:14px;padding:1.5rem;border:1px solid #e5e7eb;
                    box-shadow:0 2px 8px rgba(0,0,0,0.05);height:100%;">
            <div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:1rem;">
                <div style="font-size:0.72rem;font-weight:700;color:#6b7280;text-transform:uppercase;
                            letter-spacing:0.07em;">Wearable & Recovery</div>
                <span style="background:{_rc}20;color:{_rc};font-size:0.7rem;
                             font-weight:700;padding:2px 10px;border-radius:20px;">{_rl}</span>
            </div>
            <div style="display:flex;align-items:baseline;gap:10px;margin-bottom:0.25rem;">
                <div style="font-size:2.5rem;font-weight:800;color:{_rc};line-height:1;">{_rs}</div>
                <div style="font-size:0.82rem;color:#9ca3af;">/ 100 recovery score</div>
            </div>
            <div style="font-size:0.78rem;color:#9ca3af;margin-bottom:1rem;">
                Based on default biometric inputs — update in Wearable & Recovery.
            </div>
            {rows}
            <div style="font-size:0.75rem;color:#9ca3af;margin-top:0.75rem;">
                Navigate to <strong>Wearable & Recovery</strong> to adjust your inputs and get personalised recommendations.
            </div>
        </div>''', unsafe_allow_html=True)

    # ── Secondary: Task Summary ───────────────────────────────────────────────
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div class="section-header">Pending Tasks</div>', unsafe_allow_html=True)

    if pending_tasks:
        t_cols = st.columns(2)
        half = (len(pending_tasks[:6]) + 1) // 2
        for idx, t in enumerate(pending_tasks[:6]):
            badge_cls = f"badge-{t['priority'].lower()}"
            with t_cols[0 if idx < half else 1]:
                st.markdown(f'''
                <div class="task-row">
                    <span class="task-name">{t['name']}</span>
                    <span class="{badge_cls}">{t['priority']}</span>
                </div>''', unsafe_allow_html=True)
        if len(pending_tasks) > 6:
            st.caption(f"+{len(pending_tasks)-6} more — open Task Prioritization to view all.")
    else:
        st.success("All tasks are complete.")


elif menu == "Task Prioritization":
    st.markdown('<div class="header-style">Task Prioritization</div>', unsafe_allow_html=True)
    st.markdown('<div class="subheader-style">Manage your priorities, eliminate the noise.</div>', unsafe_allow_html=True)

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
            users = load_users()
            user_data = users[st.session_state['user_email']]
            if 'tasks' not in user_data:
                user_data['tasks'] = []
            user_data['tasks'].append({"name": task_name, "priority": priority, "status": "Pending"})
            save_users(users)
            st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="section-header">Your Tasks</div>', unsafe_allow_html=True)
    if 'tasks' in user_data and user_data['tasks']:
        for i, task in enumerate(user_data['tasks']):
            with st.container():
                col1, col2, col3, col4 = st.columns([5, 2, 2, 1])
                with col1:
                    done_style = "task-name done" if task['status'] == 'Completed' else "task-name"
                    st.markdown(f"<span class='{done_style}'>{task['name']}</span>", unsafe_allow_html=True)
                with col2:
                    badge = f"badge-{task['priority'].lower()}"
                    st.markdown(f"<span class='{badge}'>{task['priority']}</span>", unsafe_allow_html=True)
                with col3:
                    status_badge = "badge-done" if task['status'] == 'Completed' else "badge-pending"
                    st.markdown(f"<span class='{status_badge}'>{task['status']}</span>", unsafe_allow_html=True)
                with col4:
                    if task['status'] == "Pending":
                        if st.button("Done", key=f"done_{i}"):
                            users = load_users()
                            users[st.session_state['user_email']]['tasks'][i]['status'] = "Completed"
                            save_users(users)
                            st.rerun()
                    else:
                        if st.button("Delete", key=f"del_{i}"):
                            users = load_users()
                            users[st.session_state['user_email']]['tasks'].pop(i)
                            save_users(users)
                            st.rerun()
                st.markdown("<hr style='margin:0.4rem 0;border-color:#f3f4f6;'>", unsafe_allow_html=True)
    else:
        st.info("No tasks yet. Add your first task above.")

elif menu == "Calendar Analyzer":
    st.markdown('<div class="header-style">Calendar Analyzer</div>', unsafe_allow_html=True)
    st.markdown('<div class="subheader-style">Upload your .ics file for a structured, professional view of your week.</div>', unsafe_allow_html=True)
    
    # -----------------------------------
    # 4. Preferred Working Hours
    # -----------------------------------
    col_a, col_b, col_c = st.columns([1, 1, 1])
    with col_a:
        preferred_start_time = st.time_input("Preferred Start Time", value=time(9, 0))
    with col_b:
        earliest_leave_time = st.time_input("Earliest realistic time you can leave work", value=time(17, 0))
    with col_c:
        commute_time = st.slider("How long does it take you to get home? (minutes)", 0, 120, 10)
    
    # Initialize session state keys for calendar data if not present
    if 'calendar_events' not in st.session_state:
        users = load_users()
        user_data = users[st.session_state['user_email']]
        saved_events = user_data.get('calendar_events', [])
        if saved_events:
            loaded_events = []
            for ev in saved_events:
                # Convert ISO string values back to python datetime/date objects
                loaded_events.append({
                    'Event': ev['Event'],
                    'Start': datetime.fromisoformat(ev['Start']),
                    'End': datetime.fromisoformat(ev['End']),
                    'Duration (mins)': ev['Duration (mins)'],
                    'Date': datetime.fromisoformat(ev['Date']).date()
                })
            st.session_state['calendar_events'] = loaded_events
            st.session_state['calendar_filename'] = user_data.get('calendar_filename', "Saved Calendar.ics")
        else:
            st.session_state['calendar_events'] = []
            st.session_state['calendar_filename'] = ""

    uploaded_file = st.file_uploader("Upload a Calendar File (.ics)", type=["ics"])
    if uploaded_file is not None:
        try:
            cal = Calendar.from_ical(uploaded_file.read())
            events = []
            saved_to_json = []
            for component in cal.walk():
                if component.name == "VEVENT":
                    summary = component.get('summary')
                    dtstart_val = component.get('dtstart')
                    dtend_val = component.get('dtend')
                    
                    if dtstart_val and dtend_val:
                        dtstart = dtstart_val.dt
                        dtend = dtend_val.dt
                        
                        # Only keep events with datetime
                        if isinstance(dtstart, datetime) and isinstance(dtend, datetime):
                            dtstart = dtstart.replace(tzinfo=None)
                            dtend = dtend.replace(tzinfo=None)
                            duration = (dtend - dtstart).total_seconds() / 60.0
                            
                            events.append({
                                'Event': str(summary),
                                'Start': dtstart,
                                'End': dtend,
                                'Duration (mins)': duration,
                                'Date': dtstart.date()
                            })
                            saved_to_json.append({
                                'Event': str(summary),
                                'Start': dtstart.isoformat(),
                                'End': dtend.isoformat(),
                                'Duration (mins)': duration,
                                'Date': dtstart.date().isoformat()
                            })
            
            if len(events) == 0:
                st.warning("No timed events found in the calendar.")
            else:
                # Store in session state for instant retrieval
                st.session_state['calendar_events'] = events
                st.session_state['calendar_filename'] = uploaded_file.name
                
                # Store in JSON database for persistent storage
                users = load_users()
                users[st.session_state['user_email']]['calendar_events'] = saved_to_json
                users[st.session_state['user_email']]['calendar_filename'] = uploaded_file.name
                save_users(users)
                
                st.success(f"Successfully loaded and persisted: {uploaded_file.name}")
                st.rerun()
        except Exception as e:
            st.error(f"Error parsing the calendar file: {e}")

    # Render main content if calendar is loaded
    active_events = st.session_state.get('calendar_events', [])
    if active_events:
        st.markdown('<div class="card-container" style="border-left:4px solid #10b981; margin-bottom:1.5rem;">', unsafe_allow_html=True)
        col_info, col_clear = st.columns([4, 1])
        with col_info:
            st.markdown(f"📅 **Active Calendar:** `{st.session_state.get('calendar_filename', 'Loaded Calendar')}`")
        with col_clear:
            if st.button("🗑️ Clear Calendar", use_container_width=True):
                st.session_state['calendar_events'] = []
                st.session_state['calendar_filename'] = ""
                users = load_users()
                users[st.session_state['user_email']]['calendar_events'] = []
                users[st.session_state['user_email']]['calendar_filename'] = ""
                save_users(users)
                st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

        event_df = pd.DataFrame(active_events)
        event_df = event_df.sort_values('Start').reset_index(drop=True)
        dates = event_df['Date'].unique()
        num_days = len(dates)
                
        # Global week aggregations
        total_meetings_week = len(event_df)
        total_hours_week = event_df['Duration (mins)'].sum() / 60.0
        late_meetings_count = len(event_df[event_df['End'].dt.time > earliest_leave_time])
        
        meetings_per_day = event_df.groupby('Date').size()
        busiest_day_date = meetings_per_day.idxmax()
        best_day_date = meetings_per_day.idxmin()
        
        total_free_mins = 0
        large_blocks_count = 0
        short_gaps_count = 0
        
        # Pre-calculate global free time metrics
        for d in dates:
            day_events = event_df[event_df['Date'] == d].sort_values('Start')
            day_start = datetime.combine(d, preferred_start_time)
            day_end = datetime.combine(d, earliest_leave_time)
            
            last_end_tracker = day_start
            for _, row in day_events.iterrows():
                ev_start = max(day_start, row['Start'])
                ev_end = min(day_end, row['End'])
                if ev_start > ev_end: 
                    ev_start, ev_end = ev_end, ev_start
                    
                if ev_start > last_end_tracker:
                    gap = (ev_start - last_end_tracker).total_seconds() / 60.0
                    total_free_mins += gap
                    if gap >= 60: large_blocks_count += 1
                    if 0 < gap < 30: short_gaps_count += 1
                    
                last_end_tracker = max(last_end_tracker, ev_end)
                
            if last_end_tracker < day_end:
                gap = (day_end - last_end_tracker).total_seconds() / 60.0
                total_free_mins += gap
                if gap >= 60: large_blocks_count += 1
                if 0 < gap < 30: short_gaps_count += 1
    
        # Calculate Scores (0-10) heuristically
        focus_score = round(min(10.0, (large_blocks_count / max(1, num_days)) * 3), 1)
        fragmentation_score = round(min(10.0, (short_gaps_count / max(1, num_days)) * 2), 1)
    
        # -----------------------------------
        # 1. Weekly Overview
        # -----------------------------------
        with st.container():
            st.subheader("📊 Weekly Overview")
            
            col1, col2, col3 = st.columns(3)
            col1.metric("Total Meetings", total_meetings_week)
            col2.metric("Total Meeting Time", f"{total_hours_week:.1f}h")
            col3.metric("Total Free Time", f"{int(total_free_mins//60)}h {int(total_free_mins%60)}m")
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            col4, col5, col6 = st.columns(3)
            col4.metric("Focus Time Score", f"{focus_score} / 10")
            col5.metric("Fragmentation Score", f"{fragmentation_score} / 10")
            col6.metric("Late Meetings", late_meetings_count)
            
            st.markdown("---")
    
        # -----------------------------------
        # 2. Weekly Insights
        # -----------------------------------
        with st.container():
            st.subheader("💡 Weekly Insights")
            weekly_recs = []
        
        if total_hours_week > 15:
            weekly_recs.append({"priority": 90, "category": "Overload", "message": f"You have {total_hours_week:.1f} hours of meetings this week. Prioritize delegating or declining non-essential invites.", "type": "warning"})
        
        if late_meetings_count >= 3:
            weekly_recs.append({"priority": 85, "category": "Balance", "message": f"You have {late_meetings_count} meetings extending past your earliest leave time ({earliest_leave_time.strftime('%H:%M')}). Try to enforce a harder evening boundary.", "type": "warning"})
            
        weekly_recs.append({"priority": 80, "category": "Overload", "message": f"Your busiest day is {busiest_day_date.strftime('%A')} ({meetings_per_day.max()} meetings). Prepare in advance or avoid scheduling heavy tasks immediately before/after.", "type": "warning"})
        weekly_recs.append({"priority": 75, "category": "Focus", "message": f"{best_day_date.strftime('%A')} is your lightest day ({meetings_per_day.min()} meetings) → guard this day aggressively for deep focus work.", "type": "success"})
        
        weekly_recs = sorted(weekly_recs, key=lambda x: x['priority'], reverse=True)[:3]
        
        for r in weekly_recs:
            if r['type'] == 'warning':
                st.warning(f"**{r['category']}:** {r['message']}")
            elif r['type'] == 'success':
                st.success(f"**{r['category']}:** {r['message']}")
            else:
                st.info(f"**{r['category']}:** {r['message']}")
        
        if not any(r['type'] == 'warning' for r in weekly_recs):
            st.success("✨ Your week looks structurally sound! Low overload risk detected.")
    
        st.markdown("---")
    
        # -----------------------------------
        # 3. Daily Breakdown
        # -----------------------------------
        with st.container():
            st.subheader("📅 Daily Breakdown")
        
        for d in dates:
            day_events = event_df[event_df['Date'] == d].copy()
            day_events = day_events.sort_values('Start')
            num_meetings = len(day_events)
            day_name_str = d.strftime('%A, %d %B')
            
            with st.expander(f"{day_name_str} — {num_meetings} meeting{'s' if num_meetings != 1 else ''}"):
                day_total_mins = day_events['Duration (mins)'].sum()
                first_meet = day_events.iloc[0]['Start'].strftime('%H:%M') if num_meetings > 0 else "N/A"
                last_meet = day_events.iloc[-1]['End'].strftime('%H:%M') if num_meetings > 0 else "N/A"
                longest_meet_mins = day_events['Duration (mins)'].max() if num_meetings > 0 else 0
                
                # Find Free Time for the specific day between preferred start and earliest leave
                day_start = datetime.combine(d, preferred_start_time)
                day_end = datetime.combine(d, earliest_leave_time)
                local_free_mins = 0
                
                last_e = day_start
                for _, row in day_events.iterrows():
                    ev_s = max(day_start, row['Start'])
                    ev_e = min(day_end, row['End'])
                    if ev_s > ev_e: ev_s, ev_e = ev_e, ev_s
                    if ev_s > last_e:
                        gap = (ev_s - last_e).total_seconds() / 60.0
                        local_free_mins += gap
                    last_e = max(last_e, ev_e)
                
                if last_e < day_end:
                    gap = (day_end - last_e).total_seconds() / 60.0
                    local_free_mins += gap
                
                # Display Daily Metrics
                c1, c2, c3, c4, c5 = st.columns(5)
                c1.metric("Tot. Meet Time", f"{int(day_total_mins//60)}h {int(day_total_mins%60)}m")
                c2.metric("Free Time", f"{int(local_free_mins//60)}h {int(local_free_mins%60)}m")
                c3.metric("Longest Meet", f"{int(longest_meet_mins)}m")
                c4.metric("First Start", first_meet)
                c5.metric("Last End", last_meet)
                
                # Visual Agenda Display
                st.markdown("##### 📝 Schedule")
                
                agenda_html = ['<div class="agenda-container">']
                last_end_agenda = datetime.combine(d, preferred_start_time)
                
                for _, row in day_events.iterrows():
                    ev_start = row['Start']
                    ev_end = row['End']
                    title = row['Event']
                    dur = row['Duration (mins)']
                    
                    # Free block logic
                    if ev_start > last_end_agenda:
                        gap = (ev_start - last_end_agenda).total_seconds() / 60.0
                        if gap >= 30:
                            agenda_html.append(
                                '<div class="agenda-free">'
                                f"☕ {last_end_agenda.strftime('%H:%M')} – {ev_start.strftime('%H:%M')} | {int(gap)} min Free Block"
                                '</div>'
                            )
                    
                    # Meeting card logic
                    color_class = "normal"
                    if dur < 30: color_class = "short"
                    elif dur > 90: color_class = "long"
                    
                    agenda_html.append(
                        f'<div class="agenda-card {color_class}">'
                        f'<div class="agenda-time">{ev_start.strftime("%H:%M")} – {ev_end.strftime("%H:%M")}</div>'
                        f'<div class="agenda-title">🔹 {title}</div>'
                        f'<div class="agenda-duration">🕒 {int(dur)} mins</div>'
                        '</div>'
                    )
                    
                    last_end_agenda = max(last_end_agenda, ev_end)
                
                # Free block logic to end of day boundary
                day_end_agenda = datetime.combine(d, earliest_leave_time)
                if last_end_agenda < day_end_agenda:
                    gap = (day_end_agenda - last_end_agenda).total_seconds() / 60.0
                    if gap >= 30:
                        agenda_html.append(
                            '<div class="agenda-free">'
                            f"🚀 {last_end_agenda.strftime('%H:%M')} – {day_end_agenda.strftime('%H:%M')} | {int(gap)} min Focus / Wrap-up"
                            '</div>'
                        )
    
                agenda_html.append('</div>')
                st.markdown("".join(agenda_html), unsafe_allow_html=True)
                
                with st.expander("Show raw events table"):
                    display_df = day_events.copy()
                    display_df['Start'] = display_df['Start'].dt.strftime('%H:%M')
                    display_df['End'] = display_df['End'].dt.strftime('%H:%M')
                    st.dataframe(display_df[['Event', 'Start', 'End', 'Duration (mins)']], use_container_width=True)
                
                # Daily Recommendations
                st.markdown("##### 💡 Daily Advice")
                show_more_day = st.checkbox("Show more recommendations", key=f"show_more_{d}")
                max_recs = 6 if show_more_day else 3
                
                recs = []
                
                # Rule 1: Lunch verification
                lunch_start = datetime.combine(d, time(12, 0))
                lunch_end = datetime.combine(d, time(14, 0))
                has_lunch = False
                l_track = lunch_start
                for _, row in day_events.iterrows():
                    ev_start = row['Start']
                    if ev_start > l_track and ev_start <= lunch_end:
                        if (ev_start - l_track).total_seconds() / 60.0 >= 30:
                            has_lunch = True
                    l_track = max(l_track, row['End'])
                if l_track < lunch_end and (lunch_end - l_track).total_seconds() / 60.0 >= 30:
                    has_lunch = True
                    
                if not has_lunch and num_meetings > 0:
                    recs.append({"priority": 95, "category": "Break", "message": "No proper lunch break scheduled → guard 30+ minutes between 12:00 and 14:00.", "type": "warning"})
    
                # Rule 2: Overloads
                if day_total_mins > 240:
                    recs.append({"priority": 90, "category": "Overload", "message": "Heavy meeting day (>4 hrs) → avoid demanding tasks immediately after meetings.", "type": "warning"})
                if num_meetings >= 5:
                    recs.append({"priority": 85, "category": "Overload", "message": f"{num_meetings} meetings today → evaluate deferring non-essential ones.", "type": "warning"})
                    
                # Rule 3: Buffer integration (long / back-to-back)
                if longest_meet_mins > 90:
                    recs.append({"priority": 80, "category": "Buffer", "message": "You have a long meeting (>90 mins) → ensure you take a strict recovery buffer immediately afterward.", "type": "warning"})
    
                has_b2b = False
                for i in range(len(day_events) - 1):
                    curr_end = day_events.iloc[i]['End']
                    next_start = day_events.iloc[i+1]['Start']
                    gap = (next_start - curr_end).total_seconds() / 60.0
                    
                    # Back-to-back buffer
                    if 0 <= gap < 10:
                        has_b2b = True
                        
                    # Focus block / Email window (integrate directly)
                    if gap >= 60:
                        recs.append({"priority": 65, "category": "Focus", "message": f"Large free block from {curr_end.strftime('%H:%M')} to {next_start.strftime('%H:%M')} → reserve this exclusively for deep work.", "type": "success"})
                    elif 30 <= gap < 60:
                        recs.append({"priority": 60, "category": "Email", "message": f"Short gap from {curr_end.strftime('%H:%M')} to {next_start.strftime('%H:%M')} → optimal window for processing emails/admin.", "type": "info"})
                        
                if has_b2b:
                    recs.append({"priority": 80, "category": "Buffer", "message": "You have consecutive back-to-back meetings → consider stepping away for short 5-minute transition breaks.", "type": "warning"})
                    
                # Rule 4: Preferred bounds and commute
                if num_meetings > 0:
                    first_m = day_events.iloc[0]['Start']
                    if first_m > day_start and (first_m - day_start).total_seconds() / 60.0 >= 60:
                        recs.append({"priority": 68, "category": "Focus", "message": f"Your morning is entirely clear until {first_m.strftime('%H:%M')} → excellent time for uninterrupted focus.", "type": "success"})
    
                    last_m = day_events.iloc[-1]['End']
                    
                    # No afternoon meetings check (After 13:00)
                    if last_m.hour < 13:
                        recs.append({"priority": 70, "category": "Focus", "message": "You do not have meetings in the afternoon, so this is a great time to complete important tasks or admin work.", "type": "success"})
                    
                    if last_m >= day_end:
                        arr_time = last_m + pd.Timedelta(minutes=commute_time)
                        recs.append({"priority": 50, "category": "Commute", "message": f"Last meeting runs until {last_m.strftime('%H:%M')}. With commute, you'd arrive home around {arr_time.strftime('%H:%M')}.", "type": "warning"})
                    else:
                        rem_mins = (day_end - last_m).total_seconds() / 60.0
                        if rem_mins <= 45:
                            recs.append({"priority": 60, "category": "Commute", "message": f"No meetings after {last_m.strftime('%H:%M')}. Assuming tasks are complete, leaving around your earliest departure ({earliest_leave_time.strftime('%H:%M')}) is realistic.", "type": "info"})
                        else:
                            recs.append({"priority": 58, "category": "Admin", "message": f"No meetings after {last_m.strftime('%H:%M')}. Use the remaining time until {earliest_leave_time.strftime('%H:%M')} for focused work or end-of-day planning.", "type": "info"})
                    
                # Sort and trim daily recommendations
                recs = sorted(recs, key=lambda x: x['priority'], reverse=True)
                final_recs = []
                seen_cats = set()
                for r in recs:
                    # Filter to max 1 per category for diversity
                    if r['category'] not in seen_cats:
                        final_recs.append(r)
                        seen_cats.add(r['category'])
                
                final_recs_trimmed = final_recs[:max_recs]
                
                if not final_recs_trimmed:
                    st.success("✨ Your day is perfectly balanced. Enjoy!")
                else:
                    for r in final_recs_trimmed:
                        if r['type'] == 'warning':
                            st.warning(f"**{r['category']}:** {r['message']}")
                        elif r['type'] == 'success':
                            st.success(f"**{r['category']}:** {r['message']}")
                        else:
                            st.info(f"**{r['category']}:** {r['message']}")
    
        st.markdown("---")
        
        # -----------------------------------
        # 4. Behavioral Interpretation
        # -----------------------------------
        with st.container():
            st.subheader("🧩 Behavioral Interpretation")
            st.markdown("**Based on your weekly schedule patterns, your work rhythm is most similar to:**")
            
            # Rule-based heuristic match leveraging contextual week variables
            if total_hours_week >= 15 and (focus_score < 4.0 or late_meetings_count >= 3):
                matched_profile = "The Overworked & Exhausted"
                match_reason = f"Your week shows a heavy meeting load ({total_hours_week:.1f} hours) with frequent interruptions, significantly reducing your opportunity for deep work."
                sugg_1 = f"You have {late_meetings_count} late meetings this week. Consider enforcing a strict log-off boundary to avoid compounding exhaustion." if late_meetings_count > 0 else "Avoid scheduling complex tasks at the end of the day when background fatigue is highest."
                sugg_2 = f"{best_day_date.strftime('%A')} is your lightest day. Guard this block aggressively for uninterrupted deep work to catch up without distractions."
                match_border = "#ef4444"
                match_bg = "#fef2f2"
                match_icon = "🚨"
                
            elif focus_score >= 6.0 and total_hours_week <= 12 and late_meetings_count <= 1:
                matched_profile = "The Balanced Worker"
                match_reason = f"Your schedule maintains an excellent separation between collaboration and focus time."
                sugg_1 = f"Maintain the boundaries you've set, especially on {best_day_date.strftime('%A')} where you have the highest focus efficiency."
                sugg_2 = "Use short 10-minute buffers after intense meetings to avoid accumulating cognitive fatigue throughout the day."
                match_border = "#10b981"
                match_bg = "#f0fdf4"
                match_icon = "✅"
                
            elif fragmentation_score >= 6.0 or (total_hours_week < 15 and late_meetings_count >= 2):
                matched_profile = "The Sleep-Deprived / Fragmented"
                match_reason = f"Your schedule is highly scattered. Even with fewer total hours, frequent context-switching prevents meaningful progress and raises overall exhaustion."
                sugg_1 = f"Batch your meetings! For example, {busiest_day_date.strftime('%A')} is loaded with disjointed blocks. Consolidate those calls to open up contiguous free blocks."
                sugg_2 = "Turn off notifications entirely during gaps shorter than 30 minutes to give your brain a true recovery transition."
                match_border = "#f59e0b"
                match_bg = "#fffbeb"
                match_icon = "⚠️"
                
            else:
                matched_profile = "The Flexible Worker"
                match_reason = "Your week shows a balanced workload, but frequent interruptions or ad-hoc meetings may reduce your focus efficiency."
                sugg_1 = f"Identify your best focus window on {best_day_date.strftime('%A')} (your lightest day) and permanently block it out directly in your calendar."
                sugg_2 = "Evaluate if any of your recurring scattered meetings across the week can be consolidated to an afternoon."
                match_border = "#3b82f6"
                match_bg = "#eff6ff"
                match_icon = "☕"
            
            st.markdown(f'''
            <div style="background-color: {match_bg}; border-left: 5px solid {match_border}; border-radius: 8px; padding: 1.5rem; margin-top: 1rem; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05); color: #1f2937;">
                <h3 style="margin-top: 0; color: #111827;">{match_icon} {matched_profile}</h3>
                <p style="font-size: 1.05rem; margin-bottom: 1.5rem; line-height: 1.6;"><strong>Why?</strong> {match_reason}</p>
                <h5 style="color: #374151; margin-bottom: 0.5rem; font-weight: 600;">Contextual Recommendations:</h5>
                <ul style="padding-left: 1.5rem; margin-bottom: 1.5rem; line-height: 1.6;">
                    <li style="margin-bottom: 0.5rem;">{sugg_1}</li>
                    <li>{sugg_2}</li>
                </ul>
                <p style="font-size: 0.8rem; color: #6b7280; margin: 0; font-style: italic;">
                    Note: This is an analytical estimation based purely on your calendar timeline. It functions independently of the machine learning clustering model.
                </p>
            </div>
            ''', unsafe_allow_html=True)
    
    # ==========================================
    # 5. WEARABLE INTEGRATION PROTOTYPE
    # ==========================================
    

elif menu == "Wearable & Recovery":
    st.markdown('<div class="header-style">Wearable & Recovery</div>', unsafe_allow_html=True)
    st.markdown('<div class="subheader-style">Simulate biometric inputs to see your daily physiological readiness score and personalised recovery plan.</div>', unsafe_allow_html=True)

    # ── Reference baselines (weekly averages — static prototype values) ──────
    BASELINE = {
        'sleep': 6.8, 'hr': 72, 'stress': 50,
        'steps': 6000, 'fatigue': 5.0, 'sed': 120
    }

    # ── Input panel ──────────────────────────────────────────────────────────
    with st.expander("⚙️  Adjust Biometric Inputs", expanded=True):
        ci1, ci2, ci3 = st.columns(3)
        with ci1:
            w_sleep   = st.slider("Sleep last night (h)",          2.0, 12.0, 6.5, 0.25)
            w_hr      = st.slider("Avg resting heart rate (bpm)",  40,  150,  74)
        with ci2:
            w_stress  = st.slider("Stress level (0–100)",          0,   100,  62)
            w_steps   = st.slider("Steps today",                   0,   20000,4200, 100)
        with ci3:
            w_fatigue = st.slider("Morning fatigue (1–10)",        1,   10,   7)
            w_sed     = st.slider("Sedentary time (min)",          0,   300,  160, 10)

    # ── Derived scores ────────────────────────────────────────────────────────
    sleep_score    = max(0, min(100, (w_sleep  - 4)   * 25))
    stress_score   = max(0, min(100, 100 - w_stress))
    fatigue_score  = max(0, min(100, (10 - w_fatigue) * 11.1))
    activity_score = max(0, min(100, w_steps / 100))
    recovery_score = round(
        sleep_score * 0.40 + stress_score * 0.25 +
        fatigue_score * 0.25 + activity_score * 0.10
    )

    if   recovery_score >= 67: readiness_label, ring_color, ring_bg = "Optimal",  "#10b981", "#f0fdf4"
    elif recovery_score >= 34: readiness_label, ring_color, ring_bg = "Moderate", "#f59e0b", "#fffbeb"
    else:                      readiness_label, ring_color, ring_bg = "Low",       "#ef4444", "#fef2f2"

    stress_label  = "Low" if w_stress < 34 else ("Medium" if w_stress < 67 else "High")
    stress_colour = "#10b981" if w_stress < 34 else ("#f59e0b" if w_stress < 67 else "#ef4444")

    # ── Helper: trend delta ───────────────────────────────────────────────────
    def delta(val, base, higher_is_better=True):
        d = val - base
        if abs(d) < 0.5: return "→ On par", "#9ca3af"
        if higher_is_better:
            return (f"↑ +{abs(d):.1f}", "#10b981") if d > 0 else (f"↓ -{abs(d):.1f}", "#ef4444")
        else:
            return (f"↑ +{abs(d):.1f}", "#ef4444") if d > 0 else (f"↓ -{abs(d):.1f}", "#10b981")

    sl_d, sl_c = delta(w_sleep,   BASELINE['sleep'],   True)
    hr_d, hr_c = delta(w_hr,      BASELINE['hr'],      False)
    st_d, st_c = delta(w_stress,  BASELINE['stress'],  False)
    sp_d, sp_c = delta(w_steps,   BASELINE['steps'],   True)
    ft_d, ft_c = delta(w_fatigue, BASELINE['fatigue'], False)
    sd_d, sd_c = delta(w_sed,     BASELINE['sed'],     False)

    # ── Layout: recovery ring + metric grid ───────────────────────────────────
    st.markdown("<br>", unsafe_allow_html=True)
    left, right = st.columns([1, 2])

    with left:
        st.markdown(f'''
        <div style="background:{ring_bg};border:2px solid {ring_color};border-radius:16px;
                    padding:2rem 1.5rem;text-align:center;">
            <div style="font-size:0.72rem;font-weight:700;color:#6b7280;text-transform:uppercase;
                        letter-spacing:0.08em;margin-bottom:0.5rem;">Recovery Score</div>
            <div style="font-size:4rem;font-weight:800;color:{ring_color};line-height:1;">
                {recovery_score}
            </div>
            <div style="font-size:0.8rem;color:#9ca3af;margin-bottom:1rem;">out of 100</div>
            <div style="background:{ring_color};color:#fff;border-radius:20px;
                        padding:0.3rem 1.2rem;display:inline-block;
                        font-weight:700;font-size:0.95rem;">
                {readiness_label}
            </div>
            <div style="font-size:0.75rem;color:#9ca3af;margin-top:1rem;">
                vs. your 7-day baseline
            </div>
        </div>
        ''', unsafe_allow_html=True)

    with right:
        def metric_card(icon, label, value, unit, trend_txt, trend_col, bar_pct, bar_col):
            return f'''
            <div style="background:#fff;border:1px solid #e5e7eb;border-radius:12px;
                        padding:1rem 1.2rem;margin-bottom:10px;
                        box-shadow:0 1px 4px rgba(0,0,0,0.05);">
                <div style="display:flex;justify-content:space-between;align-items:center;">
                    <div>
                        <div style="font-size:0.72rem;font-weight:600;color:#6b7280;
                                    text-transform:uppercase;letter-spacing:0.05em;">
                            {icon} {label}
                        </div>
                        <div style="font-size:1.5rem;font-weight:700;color:#111827;
                                    line-height:1.2;margin-top:2px;">
                            {value}<span style="font-size:0.85rem;color:#9ca3af;
                                           font-weight:400;margin-left:3px;">{unit}</span>
                        </div>
                    </div>
                    <div style="text-align:right;">
                        <span style="font-size:0.8rem;font-weight:600;color:{trend_col};">
                            {trend_txt}
                        </span>
                        <div style="font-size:0.7rem;color:#9ca3af;">vs baseline</div>
                    </div>
                </div>
                <div style="background:#f3f4f6;border-radius:4px;height:4px;margin-top:8px;">
                    <div style="background:{bar_col};width:{bar_pct}%;height:4px;
                                border-radius:4px;"></div>
                </div>
            </div>'''

        sleep_bar = min(100, w_sleep / 10 * 100)
        hr_bar    = min(100, w_hr / 150 * 100)
        step_bar  = min(100, w_steps / 200)
        fat_bar   = w_fatigue * 10
        sed_bar   = min(100, w_sed / 300 * 100)

        cards_html = (
            metric_card("🌙", "Sleep",        f"{w_sleep:.1f}", "hrs",  sl_d, sl_c, sleep_bar, "#6366f1") +
            metric_card("💓", "Heart Rate",   f"{w_hr}",        "bpm",  hr_d, hr_c, hr_bar,    "#ef4444") +
            metric_card("🧘", "Stress",       stress_label,    "",     st_d, st_c, w_stress,  stress_colour) +
            metric_card("👟", "Steps",        f"{w_steps:,}",  "",     sp_d, sp_c, step_bar,  "#10b981") +
            metric_card("🔋", "Fatigue",      f"{w_fatigue}",  "/ 10", ft_d, ft_c, fat_bar,   "#f59e0b") +
            metric_card("🪑", "Sedentary",    f"{w_sed}",      "min",  sd_d, sd_c, sed_bar,   "#9ca3af")
        )
        st.markdown(cards_html, unsafe_allow_html=True)

    # ── Top-3 Recommendations ─────────────────────────────────────────────────
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div class="section-header">Today\'s Top Recommendations</div>', unsafe_allow_html=True)

    all_recs = []

    # Sleep
    if w_sleep < 5.5:
        all_recs.append((100, "🌙", "Critical sleep deficit",
            f"Only {w_sleep:.1f}h sleep recorded — well below the 7h minimum. "
            "Reschedule any optional afternoon meetings and target a 20-min nap before 15:00.",
            "#ef4444", "#fef2f2"))
    elif w_sleep < 7.0:
        all_recs.append((70, "🌙", "Mild sleep shortfall",
            f"{w_sleep:.1f}h is below your 7h target. Avoid scheduling cognitively heavy tasks "
            "before 10:00 to give your brain time to fully activate.",
            "#f59e0b", "#fffbeb"))

    # Fatigue
    if w_fatigue >= 8:
        all_recs.append((95, "🔋", "High fatigue — limit deep work",
            f"Fatigue score {w_fatigue}/10 is in the danger zone. Confine deep-focus blocks to "
            "45-minute sprints max and build a 15-min recovery buffer after each meeting.",
            "#ef4444", "#fef2f2"))
    elif w_fatigue >= 6:
        all_recs.append((65, "🔋", "Moderate fatigue detected",
            f"Score {w_fatigue}/10 — consider using the Pomodoro method today (25 min on / 5 min off) "
            "to avoid a mid-afternoon energy crash.",
            "#f59e0b", "#fffbeb"))

    # Stress
    if w_stress >= 75:
        all_recs.append((90, "🧘", "Elevated stress — take recovery time",
            f"Stress at {w_stress}% is significantly above your baseline ({BASELINE['stress']}%). "
            "Block 10–15 minutes mid-morning for a screen-free recovery window before your first meeting.",
            "#ef4444", "#fef2f2"))
    elif w_stress >= 55:
        all_recs.append((60, "🧘", "Moderate stress level",
            f"Stress at {w_stress}%. Avoid stacking back-to-back meetings today — "
            "a minimum 10-min gap between calls helps your nervous system reset.",
            "#f59e0b", "#fffbeb"))

    # HR
    if w_hr > 90:
        all_recs.append((75, "💓", "Elevated resting heart rate",
            f"Resting HR of {w_hr} bpm is {w_hr - BASELINE['hr']} bpm above your baseline. "
            "This often indicates residual stress or inadequate sleep. Prioritise light work only.",
            "#ef4444", "#fef2f2"))

    # Steps / Sedentary
    if w_sed > 180:
        all_recs.append((80, "🪑", "Prolonged sedentary period",
            f"You've been seated for {w_sed} min. Set a recurring 5-min movement break every hour — "
            "even a short walk improves circulation and focus by up to 15%.",
            "#6366f1", "#eef2ff"))
    elif w_sed > 90:
        all_recs.append((45, "🪑", "Moderate sedentary time",
            f"{w_sed} min without movement. Aim for a 3–5 min stretch between your next two meetings.",
            "#9ca3af", "#f9fafb"))

    if w_steps < 3000:
        all_recs.append((55, "👟", "Low step count",
            f"Only {w_steps:,} steps so far. A 15-min walk during your lunch window would significantly "
            "boost your afternoon energy and mood.",
            "#6366f1", "#eef2ff"))

    # Sort by priority, take top 3
    all_recs.sort(key=lambda x: x[0], reverse=True)
    top_recs = all_recs[:3]

    if not top_recs:
        st.markdown(f'''
        <div style="background:#f0fdf4;border:1px solid #bbf7d0;border-radius:12px;
                    padding:1.25rem 1.5rem;color:#065f46;font-weight:500;">
            ✅ All biometric indicators are within healthy ranges.
            Physiological conditions are optimal for high-stakes cognitive work today.
        </div>''', unsafe_allow_html=True)
    else:
        rec_cols = st.columns(len(top_recs))
        for i, (_, icon, title, msg, col, bg) in enumerate(top_recs):
            with rec_cols[i]:
                st.markdown(f'''
                <div style="background:{bg};border-left:4px solid {col};border-radius:12px;
                            padding:1.2rem;height:100%;box-shadow:0 2px 6px rgba(0,0,0,0.05);">
                    <div style="font-size:1.4rem;margin-bottom:0.4rem;">{icon}</div>
                    <div style="font-size:0.88rem;font-weight:700;color:#111827;
                                margin-bottom:0.5rem;">{title}</div>
                    <div style="font-size:0.82rem;color:#374151;line-height:1.5;">{msg}</div>
                </div>''', unsafe_allow_html=True)

    # ── Calendar conflict detection ────────────────────────────────────────────
    st.markdown("<br>", unsafe_allow_html=True)
    profile_name_saved = user_data.get('profile_name', None)
    conflict_flags = []

    if readiness_label == "Low":
        conflict_flags.append(("⚠️ Low readiness detected",
            "Your recovery score suggests today is not suitable for heavy cognitive work. "
            "If your calendar has back-to-back meetings, consider declining the lowest-priority ones.",
            "#f59e0b", "#fffbeb"))

    if w_fatigue >= 7 and w_sleep < 6.5:
        conflict_flags.append(("🚨 High fatigue + poor sleep combination",
            "This is the highest-risk pattern for afternoon decision fatigue. "
            "Avoid scheduling complex analyses or important presentations after 14:00.",
            "#ef4444", "#fef2f2"))

    if profile_name_saved and "Overworked" in profile_name_saved and w_fatigue >= 6:
        conflict_flags.append(("🔴 Profile conflict — Overworked & Exhausted",
            f"Your saved profile ({profile_name_saved}) already flags you as high-risk. "
            "Today's fatigue score reinforces this — enforce a hard stop at your usual leaving time.",
            "#ef4444", "#fef2f2"))

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


elif menu == "Profile Insights":
    st.markdown('<div class="header-style">Profile Insights</div>', unsafe_allow_html=True)
    st.markdown('<div class="subheader-style">Explore your habits, clustering profiles, and dataset analytics.</div>', unsafe_allow_html=True)

    action = st.radio("", ["Discover Your Person Type", "Explore Data Clusters", "Data Explorer"], horizontal=True)
    st.markdown("---")

    if action == "Discover Your Person Type":
        st.markdown('<div class="section-header">Discover Your Person Type</div>', unsafe_allow_html=True)
        st.markdown("Input your current habits to see which profile you match and get a tailored action plan.")

        # Use fixed final model K=3 for predictions in this tab
        final_k = 3
        final_scaler, final_kmeans, _, _, final_profiles = perform_clustering(df, cluster_features, final_k)

        # Load previously saved inputs for this user (pre-populate sliders)
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

            # burnout_score is required by the scaler — estimate from fatigue + work hours
            c_burnout = round(min(10.0, max(0.0, c_fatigue * 0.6 + max(0, c_work - 7) * 0.35)), 2)

            raw_input_dict = {
                'work_hours':       [c_work],
                'meetings_count':   [c_meet],
                'breaks_taken':     [c_breaks],
                'after_hours_work': [after_val],
                'app_switches':     [c_switches],
                'sleep_hours':      [c_sleep],
                'task_completion':  [c_tasks],
                'isolation_index':  [c_iso],
                'fatigue_score':    [c_fatigue],
                'burnout_score':    [c_burnout]
            }

            input_data = pd.DataFrame(raw_input_dict)
            input_data = input_data[cluster_features]

            scaled_input      = final_scaler.transform(input_data)
            cluster_assignment= final_kmeans.predict(scaled_input)[0]
            distances         = final_kmeans.transform(scaled_input)[0]

            inv_dists  = 1 / (distances + 1e-5)
            confidence = (inv_dists[cluster_assignment] / np.sum(inv_dists)) * 100

            assigned_profile = final_profiles[cluster_assignment]
            profile_name     = assigned_profile['name'].split(':')[1].strip()

            # Persist everything to user_data so the result survives tab switches
            users = load_users()
            users[st.session_state['user_email']]['profile_name'] = profile_name
            users[st.session_state['user_email']]['profile_inputs'] = {
                'work_hours':       c_work,
                'meetings_count':   c_meet,
                'breaks_taken':     c_breaks,
                'after_hours_work': after_val,
                'app_switches':     c_switches,
                'sleep_hours':      c_sleep,
                'task_completion':  c_tasks,
                'isolation_index':  c_iso,
                'fatigue_score':    c_fatigue,
            }
            users[st.session_state['user_email']]['profile_result'] = {
                'cluster_assignment': int(cluster_assignment),
                'confidence':         round(float(confidence), 1),
                'profile_name':       profile_name,
                'suggestion':         assigned_profile['suggestion'],
            }
            save_users(users)
            st.rerun()   # rerun so the result renders cleanly below

        # Always render the result if one is saved (survives tab switches)
        saved_result = user_data.get('profile_result', None)
        if saved_result:
            final_k     = 3
            _, _, _, final_centroids, _ = perform_clustering(df, cluster_features, final_k)
            cluster_assignment = saved_result['cluster_assignment']
            profile_avgs       = final_centroids.iloc[cluster_assignment]
            profile_name       = saved_result['profile_name']
            confidence         = saved_result['confidence']
            suggestion         = saved_result['suggestion']
            saved_inputs       = user_data.get('profile_inputs', {})

            st.markdown("---")
            st.markdown('<div class="section-header">Your Work Profile Analysis</div>', unsafe_allow_html=True)

            st.markdown(f'''
            <div style="background:#f8fafc;border-left:5px solid #3b82f6;border-radius:8px;
                        padding:1.5rem;margin-top:1rem;box-shadow:0 4px 6px -1px rgba(0,0,0,0.05);">
                <h2 style="margin-top:0;color:#111827;">{profile_name}</h2>
                <p style="font-size:1.05rem;color:#4b5563;margin-bottom:0;">
                    <strong>Match Confidence:</strong>
                    <span style="color:#10b981;font-weight:bold;">{confidence:.1f}%</span>
                    &nbsp;&nbsp;·&nbsp;&nbsp;
                    <span style="font-size:0.85rem;color:#9ca3af;">
                        Last analysed with your saved inputs — adjust sliders and click Analyze to update.
                    </span>
                </p>
            </div>
            ''', unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)

            col_m1, col_m2 = st.columns(2)
            with col_m1:
                st.markdown("#### Why You Matched")
                st.markdown("Key inputs vs. profile centroid averages:")

                critical_vars = ['work_hours', 'sleep_hours', 'fatigue_score', 'meetings_count']
                for var in critical_vars:
                    usr_val = saved_inputs.get(var, 0)
                    avg_val = profile_avgs[var]
                    diff    = usr_val - avg_val
                    trend   = "↑" if diff > 0 else "↓" if diff < 0 else "="
                    c_color = "red" if (var in ['work_hours', 'fatigue_score'] and diff > 0) \
                                    or (var == 'sleep_hours' and diff < 0) else "green"
                    st.markdown(f"**{var.replace('_', ' ').title()}:**")
                    st.markdown(
                        f"↳ You: `{usr_val:.1f}` | Profile Avg: `{avg_val:.1f}` "
                        f"<span style='color:{c_color};font-weight:bold;'>{trend}</span>",
                        unsafe_allow_html=True
                    )

            with col_m2:
                st.markdown("#### Tailored Action Plan")
                st.info(f"As a **{profile_name}**, the model recommends the following:")
                st.markdown(suggestion)


    elif action == "Explore Data Clusters":
        with st.container():
            st.header("👥 Person Profiles Overview")
            st.markdown(f"Based on the data, employees fall into **{n_clusters_choice} distinct behavioral types**. Below is the final model categorization.")
            
            # Use dynamic K from sidebar
            final_k = n_clusters_choice
            scaler_temp, kmeans_temp, labels_temp, centroids_temp, profiles_temp = perform_clustering(df, cluster_features, final_k)
            
            # -----------------------------------
            # 1. Section: Person Profiles Overview
            # -----------------------------------
            for idx in range(final_k):
                profile = profiles_temp[idx]
                with st.expander(f"**{profile['name']}**", expanded=True):
                    st.markdown(profile['suggestion'])
        
            st.markdown("---")
            
            # -----------------------------------
            # 2. Section: Cluster Characteristics
            # -----------------------------------
            st.subheader("📊 Cluster Characteristics")
            st.markdown("Average behaviors per profile type:")
            
            display_features = ['work_hours', 'sleep_hours', 'fatigue_score', 'burnout_score']
            display_features = list(dict.fromkeys(display_features))
            
            stat_df = df.copy()
            stat_df['Cluster'] = labels_temp
            
            valid_display_features = [col for col in display_features if col in stat_df.columns]
            
            cluster_summary = stat_df.groupby('Cluster')[valid_display_features].mean()
            cluster_summary.index = [profiles_temp[i]['name'].split(':')[1].strip() for i in range(final_k)]
            
            if cluster_summary.columns.is_unique and cluster_summary.index.is_unique:
                st.dataframe(cluster_summary.style.highlight_max(axis=0, color='#fca5a5').highlight_min(axis=0, color='#bbf7d0'), use_container_width=True)
            else:
                st.dataframe(cluster_summary, use_container_width=True)
        
            st.markdown("---")
            
            # -----------------------------------
            # 3. Section: Cluster Visualization & Comparison
            # -----------------------------------
            st.subheader("🔍 Cluster Visualization")
            
            temp_df = df.copy()
            temp_df['Cluster'] = labels_temp
            temp_df['Person Type'] = temp_df['Cluster'].apply(lambda x: profiles_temp[x]['name'].split(':')[1].strip())
            
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
                colors = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444']
                sns.scatterplot(data=temp_df, x=x_axis, y=y_axis, hue='Person Type', ax=ax, palette=colors[:final_k])
                ax.set_xlabel(x_axis.replace('_', ' ').title())
                ax.set_ylabel(y_axis.replace('_', ' ').title())
                st.pyplot(fig)
        
        
        

    elif action == "Data Explorer":
        with st.container():
            st.header("📊 Behavior Insights Dashboard")
            st.markdown("Explore key trends and behavioral patterns in the remote work dataset.")
            
            # -----------------------------------
            # 1. Dataset Overview
            # -----------------------------------
            st.subheader("📌 Dataset Overview")
            num_rows = df.shape[0]
            num_cols = df.shape[1]
            num_numeric = len(df.select_dtypes(include=[np.number]).columns)
            num_cat = len(df.select_dtypes(exclude=[np.number]).columns)
            
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Total Rows", num_rows)
            c2.metric("Total Columns", num_cols)
            c3.metric("Numerical Vars", num_numeric)
            c4.metric("Categorical Vars", num_cat)
            
            with st.expander("Show raw dataset preview"):
                st.dataframe(df.head(10), use_container_width=True)
        
            st.markdown("---")
        
            # -----------------------------------
            # 2. Data Quality Snapshot
            # -----------------------------------
            st.subheader("🛡️ Data Quality Snapshot")
            missing_count = df.isnull().sum().sum()
            duplicate_count = df.duplicated().sum()
            
            dq1, dq2 = st.columns(2)
            if missing_count > 0:
                dq1.warning(f"⚠️ **{missing_count}** missing values detected.")
            else:
                dq1.success("✅ **0** missing values detected.")
                
            if duplicate_count > 0:
                dq2.warning(f"⚠️ **{duplicate_count}** duplicate rows detected.")
            else:
                dq2.success("✅ **0** duplicate rows detected.")
        
            st.markdown("---")
        
            # -----------------------------------
            # 3. Key Behavioral Patterns
            # -----------------------------------
            st.subheader("📈 Key Behavioral Patterns")
            
            p1, p2 = st.columns(2)
            
            with p1:
                st.markdown("**A. Work Hours Distribution**")
                fig1, ax1 = plt.subplots(figsize=(6, 4))
                sns.histplot(data=df, x='work_hours', bins=20, kde=True, color='#3b82f6', ax=ax1)
                ax1.set_xlabel("Work Hours")
                ax1.set_ylabel("Count")
                st.pyplot(fig1)
                
                st.markdown("**C. Fatigue vs Burnout**")
                fig3, ax3 = plt.subplots(figsize=(6, 4))
                sns.scatterplot(data=df, x='fatigue_score', y='burnout_score', alpha=0.6, color='#ef4444', ax=ax3)
                ax3.set_xlabel("Fatigue Score")
                ax3.set_ylabel("Burnout Score")
                st.pyplot(fig3)
        
            with p2:
                st.markdown("**B. Sleep Hours Distribution**")
                fig2, ax2 = plt.subplots(figsize=(6, 4))
                sns.histplot(data=df, x='sleep_hours', bins=20, kde=True, color='#10b981', ax=ax2)
                ax2.set_xlabel("Sleep Hours")
                ax2.set_ylabel("Count")
                st.pyplot(fig2)
        
                st.markdown("**D. Work Hours vs Fatigue**")
                fig4, ax4 = plt.subplots(figsize=(6, 4))
                sns.scatterplot(data=df, x='work_hours', y='fatigue_score', alpha=0.6, color='#f59e0b', ax=ax4)
                ax4.set_xlabel("Work Hours")
                ax4.set_ylabel("Fatigue Score")
                st.pyplot(fig4)
        
            st.markdown("---")
        
            # -----------------------------------
            # 4. Key Insights Section
            # -----------------------------------
            st.subheader("💡 Key Insights Summary")
            
        
            avg_work = df['work_hours'].mean()
            avg_sleep = df['sleep_hours'].mean()
            avg_fatigue = df['fatigue_score'].mean()
            avg_burnout = df['burnout_score'].mean()
            
            k1, k2, k3, k4 = st.columns(4)
            k1.metric("Avg Work Hours", f"{avg_work:.1f} hr")
            k2.metric("Avg Sleep Hours", f"{avg_sleep:.1f} hr")
            k3.metric("Avg Fatigue", f"{avg_fatigue:.1f} / 10")
            k4.metric("Avg Burnout", f"{avg_burnout:.1f} / 100")
            
            st.info("📌 **Observation:** Higher work hours are intrinsically linked to elevated fatigue. Guaranteeing 7+ hours of sleep per night acts as the most aggressive buffer against compounding burnout scores.")
        
        

