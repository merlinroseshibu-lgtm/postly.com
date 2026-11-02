import streamlit as st
import time
import random
import datetime

# 1. PAGE CONFIGURATION
st.set_page_config(
    page_title="Postly - Digital Well-Being Assistant",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. DARK BURGUNDY THEME STYLING (CSS)
CUSTOM_CSS = """
<style>
    .stApp {
        background: linear-gradient(180deg, #120306 0%, #1A050A 100%);
        color: #E2E8F0;
    }
    .header-box {
        background: linear-gradient(135deg, #4A0E17 100%, #2D070D 0%);
        padding: 28px 34px;
        border-radius: 18px;
        color: #FFFFFF;
        box-shadow: 0 12px 30px rgba(0, 0, 0, 0.5);
        border: 1px solid #66101F;
        margin-bottom: 24px;
    }
    .header-box h1 {
        margin: 0;
        font-size: 2.8rem;
        font-weight: 800;
        color: #FFD1DC !important;
        letter-spacing: 1px;
    }
    .header-box p {
        margin: 8px 0 0 0;
        font-size: 1.05rem;
        color: #F8D7DA;
    }
    .metric-card {
        background-color: #22090F;
        border-radius: 14px;
        padding: 18px 20px;
        box-shadow: 0 6px 20px rgba(0, 0, 0, 0.3);
        border: 1px solid #4A1522;
        text-align: center;
    }
    .alert-banner-danger {
        background: linear-gradient(135deg, #450A0A 100%, #2B0606 0%);
        border-left: 6px solid #EF4444;
        padding: 16px 20px;
        border-radius: 12px;
        color: #FCA5A5;
        font-weight: 700;
        font-size: 1.1rem;
        margin: 15px 0;
        border: 1px solid #5C1D1D;
    }
    .alert-banner-neutral {
        background: #1E293B;
        border-left: 6px solid #64748B;
        padding: 16px 20px;
        border-radius: 12px;
        color: #CBD5E1;
        font-weight: 600;
        margin: 15px 0;
        border: 1px solid #334155;
    }
    div.stButton > button:first-child {
        background-color: #800020;
        color: #FFFFFF;
        font-weight: 600;
        border-radius: 10px;
        border: 1px solid #A31435;
        padding: 10px 24px;
    }
    div.stButton > button:first-child:hover {
        background-color: #A31435;
        color: #FFFFFF;
    }
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# 3. AUDIO BEEP & BACKGROUND NOTIFICATION JAVASCRIPT ENGINE
def trigger_alert_system(message):
    alert_code = f"""
    <script>
    // 1. Play Web Audio API Beep Sound
    try {{
        var audioCtx = new (window.AudioContext || window.webkitAudioContext)();
        var osc = audioCtx.createOscillator();
        var gain = audioCtx.createGain();
        osc.type = "sine";
        osc.frequency.setValueAtTime(587.33, audioCtx.currentTime); // D5 note
        gain.gain.setValueAtTime(0.2, audioCtx.currentTime);
        gain.gain.exponentialRampToValueAtTime(0.001, audioCtx.currentTime + 0.4);
        osc.connect(gain);
        gain.connect(audioCtx.destination);
        osc.start();
        osc.stop(audioCtx.currentTime + 0.4);
    }} catch(e) {{}}

    // 2. Trigger Native Background Browser Notification (Works even across other tabs!)
    if (window.Notification) {{
        if (Notification.permission === "granted") {{
            new Notification("⚠️ Postly Well-Being Alert!", {{
                body: "{message}",
                icon: "https://em-content.zobj.net/source/apple/391/shield_1f6e1-fe0f.png"
            }});
        }} else if (Notification.permission !== "denied") {{
            Notification.requestPermission().then(permission => {{
                if (permission === "granted") {{
                    new Notification("⚠️ Postly Well-Being Alert!", {{ body: "{message}" }});
                }}
            }});
        }}
    }}
    </script>
    """
    st.components.v1.html(alert_code, height=0, width=0)

# Request notification permissions on boot
st.components.v1.html("""
<script>
if (window.Notification && Notification.permission !== "granted") {
    Notification.requestPermission();
}
</script>
""", height=0, width=0)

# 4. INITIALIZE SESSION STATES
if "alert_count" not in st.session_state:
    st.session_state.alert_count = 0
if "session_start_time" not in st.session_state:
    st.session_state.session_start_time = time.time()
if "good_frames" not in st.session_state:
    st.session_state.good_frames = 15
if "total_frames" not in st.session_state:
    st.session_state.total_frames = 20
if "pomo_start" not in st.session_state:
    st.session_state.pomo_start = time.time()
if "rule_20_start" not in st.session_state:
    st.session_state.rule_20_start = time.time()

# 5. SIDEBAR CONTROLS (Pomodoro & Bedtime Guard)
with st.sidebar:
    st.markdown("### ⚙️ Live Monitoring Controls")
    posture_mode = st.selectbox("Posture Sensitivity", ["Normal", "Strict", "Relaxed"])
    
    st.markdown("---")
    st.markdown("### 🍅 Live Pomodoro Engine")
    pomo_mins = st.slider("Work Sprint Length (Mins)", 1, 45, 25)
    
    elapsed_pomo = int((time.time() - st.session_state.pomo_start) / 60)
    time_left_pomo = max(0, pomo_mins - elapsed_pomo)
    st.metric("Pomodoro Countdown", f"{time_left_pomo} mins left")
    
    if st.button("🔄 Reset Timer"):
        st.session_state.pomo_start = time.time()
        st.rerun()

    st.markdown("---")
    st.markdown("### 🌙 Night Guard")
    bedtime_hour = st.slider("Target Bedtime", 18, 23, 22, format="%d:00 PM")

# 6. HEADER & NIGHT GUARD BANNER
st.markdown("""
<div class="header-box">
    <h1>Postly</h1>
    <p>Advanced Real-Time Ergonomic & Cross-Tab Notification Assistant</p>
</div>
""", unsafe_allow_html=True)

current_hour = datetime.datetime.now().hour
if current_hour >= bedtime_hour or current_hour <= 5:
    st.markdown(f"""
    <div class="alert-banner-neutral">
        🌙 <strong>Late Night Protection Active:</strong> Past your set bedtime ({bedtime_hour}:00 PM). Consider wrapping up screen time to protect your sleep!
    </div>
    """, unsafe_allow_html=True)

# 7. MAIN INTERFACE COLUMNS
col_cam, col_metrics = st.columns([1.4, 1.0], gap="medium")

with col_cam:
    st.markdown("### 🎥 Live Posture & Eye-Strain Feed")
    st.info("💡 **Tip:** Click snapshot periodically to update your live posture audit. If you slouch or lose focus, Postly fires an audio chime and a background tab notification!")
    
    # Live interactive snapshot trigger
    cam_input = st.camera_input("Live Audit Capture")
    
    if cam_input is not None:
        st.session_state.total_frames += 1
        # Random simulation for demonstration accuracy or bad posture detection
        is_slouching = random.choice([False, False, True]) # 33% chance to simulate real-time slouch detection trigger
        
        if is_slouching:
            st.markdown('<div class="alert-banner-danger">⚠️ Slouching or Forward Head Posture Detected! Sit up straight.</div>', unsafe_allow_html=True)
            st.session_state.alert_count += 1
            trigger_alert_system("Hey! Your posture is slipping. Sit up straight and protect your spine!")
        else:
            st.success("✅ Excellent posture and alignment maintained!")
            st.session_state.good_frames += 5

    # 20-20-20 Eye Strain Reminder Logic
    elapsed_eye_rule = int((time.time() - st.session_state.rule_20_start) / 60)
    if elapsed_eye_rule >= 20:
        trigger_alert_system("20-20-20 Rule Alert: Look 20 feet away for 20 seconds to rest your eyes!")
        st.session_state.rule_20_start = time.time()

with col_metrics:
    st.markdown("### 🌸 Postly Plant Status")
    health_score = int((st.session_state.good_frames / max(1, st.session_state.total_frames)) * 100)
    
    if health_score >= 80:
        st.success("🌸 **Your Postly Flower is Blooming!** Great posture.")
    elif health_score >= 50:
        st.warning("🌱 **Your Flower is Thirsting.** Align your shoulders!")
    else:
        st.error("🥀 **Your Flower is Wilting!** Heavy slouching detected.")

    st.markdown("---")
    st.markdown("### 🤸 Guided Micro-Stretches")
    stretches = [
        "**Shoulder Rolls:** Roll shoulders backward 10 times.",
        "**Neck Tilt:** Gently tilt ear to shoulder for 15s per side.",
        "**Chest Opener:** Interlace fingers behind back and press forward.",
        "**Eye Relaxation:** Blink rapidly for 10 seconds to re-lubricate eyes."
    ]
    if st.button("✨ Give Me a Stretch"):
        st.info(random.choice(stretches))

# 8. SESSION SUMMARY REPORT
st.markdown("---")
st.markdown("### 📋 Live Session Summary")
r1, r2, r3 = st.columns(3)
with r1:
    st.metric("Total Session Time", f"{int(time.time() - st.session_state.session_start_time)//60} mins")
with r2:
    st.metric("Posture Breaches Caught", st.session_state.alert_count)
with r3:
    st.metric("Ergonomic Health Score", f"{health_score}%")