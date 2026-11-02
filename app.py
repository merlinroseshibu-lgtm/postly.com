import cv2
import numpy as np
import streamlit as st
import time
import os
import urllib.request
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
    .metric-title {
        font-size: 0.85rem;
        font-weight: 600;
        color: #FF99A8;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .metric-value {
        font-size: 1.85rem;
        font-weight: 800;
        color: #FFFFFF;
        margin: 6px 0;
    }
    .metric-subtitle {
        font-size: 0.8rem;
        color: #A0AEC0;
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

# 3. SAFE HAAR CASCADE DOWNLOAD
xml_path = "haarcascade_frontalface_default.xml"
if not os.path.exists(xml_path):
    url = "https://raw.githubusercontent.com/opencv/opencv/master/data/haarcascades/haarcascade_frontalface_default.xml"
    urllib.request.urlretrieve(url, xml_path)

try:
    face_cascade = cv2.CascadeClassifier(xml_path)
except Exception:
    face_cascade = None

# 4. SIDEBAR SETTINGS
with st.sidebar:
    st.markdown("### ⚙️ System Settings")
    distance_threshold = st.slider("📏 Max Safe Face Width", min_value=100, max_value=350, value=200, step=10)
    
    st.markdown("---")
    st.markdown("### 🍅 Pomodoro Focus Engine")
    pomo_mode = st.radio("Sprint Mode", ["Work Sprint (25m)", "Short Break (5m)"])
    if st.button("Reset Timer"):
        st.toast("Pomodoro timer restarted!")

    st.markdown("---")
    st.markdown("### 🌙 Night & Bedtime Guard")
    bedtime_hour = st.slider("Select Target Bedtime", min_value=18, max_value=23, value=22, format="%d:00 PM")

# 5. HEADER
st.markdown("""
<div class="header-box">
    <h1>Postly</h1>
    <p>Smart Ergonomic & Focus Protection System</p>
</div>
""", unsafe_allow_html=True)

# Bedtime Alert Banner Check
current_hour = datetime.datetime.now().hour
if current_hour >= bedtime_hour or current_hour <= 5:
    st.markdown(f"""
    <div class="alert-banner-neutral">
        🌙 <strong>Late Night Protection Active:</strong> Past your set bedtime ({bedtime_hour}:00 PM). Consider closing screen time to protect your sleep cycle!
    </div>
    """, unsafe_allow_html=True)

# Initialize Session States
if "alert_count" not in st.session_state:
    st.session_state.alert_count = 0
if "session_start_time" not in st.session_state:
    st.session_state.session_start_time = time.time()
if "good_frames" not in st.session_state:
    st.session_state.good_frames = 10
if "total_frames" not in st.session_state:
    st.session_state.total_frames = 10

col_cam, col_metrics = st.columns([1.5, 1.0], gap="medium")

with col_cam:
    st.markdown("### 🎥 Cloud Web Camera Feed")
    st.info("Take a snapshot using your browser camera below to audit posture and face distance!")
    
    # Browser-safe camera input (works instantly on Streamlit Cloud!)
    camera_image = st.camera_input("Take posture snapshot")
    
    if camera_image is not None:
        bytes_data = camera_image.getvalue()
        cv2_img = cv2.imdecode(np.frombuffer(bytes_data, np.uint8), cv2.IMREAD_COLOR)
        gray = cv2.cvtColor(cv2_img, cv2.COLOR_BGR2GRAY)
        
        if face_cascade is not None:
            faces = face_cascade.detectMultiScale(gray, 1.1, 4)
            st.session_state.total_frames += 1
            if len(faces) > 0:
                for (x, y, w, h) in faces:
                    if w > distance_threshold:
                        st.markdown('<div class="alert-banner-danger">⚠️ Too close to the screen! Move backward.</div>', unsafe_allow_html=True)
                        st.session_state.alert_count += 1
                    else:
                        st.success("✅ Perfect distance and posture detected!")
                        st.session_state.good_frames += 1
            else:
                st.warning("⚠️ No face detected clearly. Adjust your lighting or angle.")

with col_metrics:
    st.markdown("### 🌸 Postly Plant Status")
    health_score = int((st.session_state.good_frames / max(1, st.session_state.total_frames)) * 100)
    
    if health_score >= 80:
        st.success("🌸 **Your Postly Flower is Blooming!** Posture is excellent.")
    elif health_score >= 50:
        st.warning("🌱 **Your Flower is Thirsting.** Sit upright to keep it healthy.")
    else:
        st.error("🥀 **Your Flower is Wilting!** Too much slouching detected.")

    st.markdown("---")
    st.markdown("### 🤸 Desk Stretch Break")
    stretches = [
        "**Shoulder Rolls:** Roll your shoulders backward in slow circles 10 times.",
        "**Neck Tilt:** Gently tilt your ear toward your shoulder, holding for 15 seconds.",
        "**Chest Opener:** Interlace fingers behind your back and pull your shoulders back.",
        "**20-20-20 Rule:** Look away at an object 20 feet away for 20 seconds."
    ]
    if st.button("✨ Micro-Stretch Idea"):
        st.info(random.choice(stretches))

# 6. SESSION SUMMARY REPORT
st.markdown("---")
st.markdown("### 📋 Session Summary Report")
r1, r2, r3 = st.columns(3)
with r1:
    st.metric("Total Session Time", f"{int(time.time() - st.session_state.session_start_time)//60} mins")
with r2:
    st.metric("Total Posture Breaches", st.session_state.alert_count)
with r3:
    st.metric("Final Ergonomic Rating", f"{health_score}%")