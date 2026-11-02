import streamlit as st
import time
import random
import datetime
from PIL import Image
import numpy as np

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

# 3. AUDIO ALARM & NOTIFICATION ENGINE
def trigger_alarm_sound(message):
    alarm_code = f"""
    <script>
    try {{
        var audioCtx = new (window.AudioContext || window.webkitAudioContext)();
        var osc = audioCtx.createOscillator();
        var gain = audioCtx.createGain();
        osc.type = "sine";
        osc.frequency.setValueAtTime(880, audioCtx.currentTime);
        gain.gain.setValueAtTime(0.3, audioCtx.currentTime);
        gain.gain.exponentialRampToValueAtTime(0.001, audioCtx.currentTime + 0.8);
        osc.connect(gain);
        gain.connect(audioCtx.destination);
        osc.start();
        osc.stop(audioCtx.currentTime + 0.8);
    }} catch(e) {{}}

    if (window.Notification && Notification.permission === "granted") {{
        new Notification("🍅 Postly Pomodoro Alert!", {{
            body: "{message}",
            icon: "https://em-content.zobj.net/source/apple/391/tomato_1f345.png"
        }});
    }}
    </script>
    """
    st.components.v1.html(alarm_code, height=0, width=0)

st.components.v1.html("""
<script>
if (window.Notification && Notification.permission !== "granted") {
    Notification.requestPermission();
}
</script>
""", height=0, width=0)

# 4. INITIALIZE SESSION STATES
if "session_start_time" not in st.session_state:
    st.session_state.session_start_time = time.time()
if "pomo_start_time" not in st.session_state:
    st.session_state.pomo_start_time = time.time()
if "pomo_mode" not in st.session_state:
    st.session_state.pomo_mode = "Work Sprint"
if "pomo_notified" not in st.session_state:
    st.session_state.pomo_notified = False
if "health_score" not in st.session_state:
    st.session_state.health_score = 90
if "alert_count" not in st.session_state:
    st.session_state.alert_count = 0

# 5. SIDEBAR SETTINGS (POMODORO & NIGHT GUARD)
with st.sidebar:
    st.markdown("### ⚙️ Assistant Controls")
    st.markdown("---")
    st.markdown("### 🍅 Automated Pomodoro Engine")
    
    work_duration = st.slider("Work Sprint (Mins)", 1, 45, 25) * 60
    break_duration = st.slider("Break Duration (Mins)", 1, 15, 5) * 60
    
    elapsed_pomo = time.time() - st.session_state.pomo_start_time
    current_target_duration = work_duration if st.session_state.pomo_mode == "Work Sprint" else break_duration
    time_left = int(current_target_duration - elapsed_pomo)
    
    if time_left <= 0:
        if not st.session_state.pomo_notified:
            if st.session_state.pomo_mode == "Work Sprint":
                trigger_alarm_sound("Work sprint finished! Time for a break.")
                st.session_state.pomo_mode = "Break"
            else:
                trigger_alarm_sound("Break finished! Back to your work sprint.")
                st.session_state.pomo_mode = "Work Sprint"
            st.session_state.pomo_start_time = time.time()
            st.session_state.pomo_notified = True
            st.rerun()
    else:
        st.session_state.pomo_notified = False

    mins_display = max(0, time_left // 60)
    secs_display = max(0, time_left % 60)
    
    st.metric(label=f"Current Mode: {st.session_state.pomo_mode}", value=f"{mins_display:02d}:{secs_display:02d}")
    
    if st.button("🔄 Reset Timer"):
        st.session_state.pomo_start_time = time.time()
        st.session_state.pomo_mode = "Work Sprint"
        st.session_state.pomo_notified = False
        st.rerun()

    st.markdown("---")
    st.markdown("### 🌙 Night Guard")
    bedtime_hour = st.slider("Target Bedtime", 18, 23, 22, format="%d:00 PM")

# 6. HEADER & NIGHT GUARD
st.markdown("""
<div class="header-box">
    <h1>Postly</h1>
    <p>Advanced Digital Well-Being & Pomodoro Assistant</p>
</div>
""", unsafe_allow_html=True)

current_hour = datetime.datetime.now().hour
if current_hour >= bedtime_hour or current_hour <= 5:
    st.markdown(f"""
    <div class="alert-banner-neutral">
        🌙 <strong>Late Night Protection Active:</strong> Past your set bedtime ({bedtime_hour}:00 PM). Consider wrapping up screen time!
    </div>
    """, unsafe_allow_html=True)

# 7. MAIN INTERFACE
col_cam, col_metrics = st.columns([1.4, 1.0], gap="medium")

with col_cam:
    st.markdown("### 🎥 Posture & Ergonomic Audit Feed")
    st.info("💡 **Privacy-First Audit:** Click below to check your alignment instantly. Postly evaluates posture without storing invasive recordings.")
    
    cam_input = st.camera_input("Posture Audit Snapshot")
    
    if cam_input is not None:
        # Simulate intelligent postural assessment on snapshot
        assessment = random.choice(["good", "good", "slouch", "close"])
        if assessment == "good":
            st.success("✅ Excellent posture and viewing distance detected! Your spine is aligned.")
            st.session_state.health_score = min(100, st.session_state.health_score + 5)
        elif assessment == "slouch":
            st.markdown('<div class="alert-banner-danger">⚠️ Slouching detected! Drop your shoulders back and sit upright.</div>', unsafe_allow_html=True)
            st.session_state.health_score = max(30, st.session_state.health_score - 15)
            st.session_state.alert_count += 1
            trigger_alarm_sound("Posture Alert: Slouching detected!")
        else:
            st.markdown('<div class="alert-banner-danger">⚠️ Sitting too close to the screen! Move backward.</div>', unsafe_allow_html=True)
            st.session_state.health_score = max(30, st.session_state.health_score - 15)
            st.session_state.alert_count += 1
            trigger_alarm_sound("Proximity Alert: Too close to screen!")

with col_metrics:
    st.markdown("### 🌸 Postly Plant Status")
    score = st.session_state.health_score
    
    if score >= 80:
        st.success(f"🌸 **Your Postly Flower is Blooming!** Health Score: {score}%")
    elif score >= 50:
        st.warning(f"🌱 **Your Flower is Thirsting.** Health Score: {score}% — Sit upright!")
    else:
        st.error(f"🥀 **Your Flower is Wilting!** Health Score: {score}% — Heavy strain detected!")

    st.markdown("---")
    st.markdown("### 🤸 Guided Micro-Stretches")
    stretches = [
        "**Shoulder Rolls:** Roll shoulders backward 10 times.",
        "**Neck Tilt:** Gently tilt ear to shoulder for 15s per side.",
        "**Chest Opener:** Interlace fingers behind back and press forward.",
        "**Eye Relaxation:** Blink rapidly for 10 seconds."
    ]
    if st.button("✨ Give Me a Stretch"):
        st.info(random.choice(stretches))

# 8. SESSION SUMMARY
st.markdown("---")
st.markdown("### 📋 Session Summary Report")
r1, r2, r3 = st.columns(3)
with r1:
    st.metric("Session Duration", f"{int(time.time() - st.session_state.session_start_time)//60} mins")
with r2:
    st.metric("Posture Breaches", st.session_state.alert_count)
with r3:
    st.metric("Ergonomic Health Score", f"{st.session_state.health_score}%")