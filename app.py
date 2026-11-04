import cv2
import numpy as np
import streamlit as st
import time
import os
import urllib.request

# 1. PAGE CONFIGURATION
st.set_page_config(
    page_title="Postly - Digital Well-Being Assistant",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. THEME STATE INITIALIZATION
if "theme_mode" not in st.session_state:
    st.session_state.theme_mode = "Dark Burgundy"

# 3. SIDEBAR SETTINGS & THEME SWITCHER
with st.sidebar:
    st.markdown("### 🎨 Appearance")
    theme_choice = st.radio("Select Theme Mode", ["Dark Burgundy", "Clean Light Mode"], index=0 if st.session_state.theme_mode == "Dark Burgundy" else 1)
    st.session_state.theme_mode = theme_choice
    
    st.markdown("---")
    st.markdown("### ⚙️ System Settings")
    # Increased default threshold so you don't have to sit far away!
    distance_threshold = st.slider("📏 Proximity Sensitivity (Max Width)", min_value=200, max_value=600, value=420, step=10, help="Higher means you can sit closer without 'Too Close' alerts.")
    sound_enabled = st.toggle("🔔 Enable Audio Alert Beeps", value=True)
    camera_id = st.number_input("📹 Camera Device Index", min_value=0, max_value=5, value=0, step=1)
    
    st.markdown("---")
    st.markdown("### 🍅 Pomodoro Engine")
    work_mins = st.slider("Work Sprint (Mins)", 1, 45, 25) * 60
    break_mins = st.slider("Break Duration (Mins)", 1, 15, 5) * 60

    st.markdown("---")
    st.markdown("### 💡 Ergonomic Tip")
    st.info("Sit comfortably with your screen at eye level.")

# 4. DYNAMIC CSS STYLING
if st.session_state.theme_mode == "Dark Burgundy":
    CUSTOM_CSS = """
    <style>
        .stApp {
            background: linear-gradient(180deg, #1A0509 0%, #0F0205 100%);
            font-family: 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
            color: #F7FAFC;
        }
        .header-box {
            background: linear-gradient(135deg, #800020 0%, #4A0E17 100%);
            padding: 24px 30px;
            border-radius: 16px;
            color: #FFFFFF;
            box-shadow: 0 10px 25px rgba(128, 0, 32, 0.4);
            margin-bottom: 24px;
            border: 1px solid #A31D34;
        }
        .header-box h1 { margin: 0; font-size: 2.1rem; font-weight: 800; color: #FFFFFF !important; }
        .header-box p { margin: 6px 0 0 0; font-size: 1.05rem; color: #F8D7DA; }
        .metric-card {
            background-color: #2D0C13;
            border-radius: 14px;
            padding: 18px 20px;
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3);
            border: 1px solid #5C1D29;
            text-align: center;
        }
        .metric-title { font-size: 0.85rem; font-weight: 600; color: #FF99AA; text-transform: uppercase; }
        .metric-value { font-size: 1.85rem; font-weight: 800; color: #FFFFFF; margin: 6px 0; }
        .metric-subtitle { font-size: 0.8rem; color: #CBD5E0; }
        .alert-banner-danger {
            background: linear-gradient(135deg, #4A1515 0%, #3B0A0A 100%);
            border-left: 6px solid #EF4444;
            padding: 16px 20px; border-radius: 12px; color: #FCA5A5; font-weight: 700; font-size: 1.1rem; margin: 15px 0;
        }
        .alert-banner-success {
            background: linear-gradient(135deg, #064E3B 0%, #022C22 100%);
            border-left: 6px solid #10B981;
            padding: 16px 20px; border-radius: 12px; color: #A7F3D0; font-weight: 700; font-size: 1.1rem; margin: 15px 0;
        }
        .alert-banner-neutral {
            background: #2D3748; border-left: 6px solid #A0AEC0; padding: 16px 20px; border-radius: 12px; color: #E2E8F0; font-weight: 600; margin: 15px 0;
        }
        div.stButton > button:first-child {
            background-color: #800020; color: #FFFFFF; font-weight: 600; border-radius: 10px; border: none; padding: 10px 24px;
        }
        div.stButton > button:first-child:hover { background-color: #A31D34; color: #FFFFFF; }
    </style>
    """
else:
    CUSTOM_CSS = """
    <style>
        .stApp {
            background: linear-gradient(180deg, #FDFBFB 0%, #FAF2F4 100%);
            font-family: 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
            color: #2D3748;
        }
        .header-box {
            background: linear-gradient(135deg, #800020 0%, #4A0E17 100%);
            padding: 24px 30px;
            border-radius: 16px;
            color: #FFFFFF;
            box-shadow: 0 10px 25px rgba(128, 0, 32, 0.22);
            margin-bottom: 24px;
        }
        .header-box h1 { margin: 0; font-size: 2.1rem; font-weight: 800; color: #FFFFFF !important; }
        .header-box p { margin: 6px 0 0 0; font-size: 1.05rem; color: #F8D7DA; }
        .metric-card {
            background-color: #FFFFFF;
            border-radius: 14px;
            padding: 18px 20px;
            box-shadow: 0 4px 15px rgba(128, 0, 32, 0.06);
            border: 1px solid #F1DFE3;
            text-align: center;
        }
        .metric-title { font-size: 0.85rem; font-weight: 600; color: #800020; text-transform: uppercase; }
        .metric-value { font-size: 1.85rem; font-weight: 800; color: #1A202C; margin: 6px 0; }
        .metric-subtitle { font-size: 0.8rem; color: #718096; }
        .alert-banner-danger {
            background: linear-gradient(135deg, #FFEBEB 0%, #FEE2E2 100%);
            border-left: 6px solid #DC2626; padding: 16px 20px; border-radius: 12px; color: #991B1B; font-weight: 700; font-size: 1.1rem; margin: 15px 0;
        }
        .alert-banner-success {
            background: linear-gradient(135deg, #ECFDF5 0%, #D1FAE5 100%);
            border-left: 6px solid #059669; padding: 16px 20px; border-radius: 12px; color: #065F46; font-weight: 700; font-size: 1.1rem; margin: 15px 0;
        }
        .alert-banner-neutral {
            background: #F3F4F6; border-left: 6px solid #6B7280; padding: 16px 20px; border-radius: 12px; color: #374151; font-weight: 600; margin: 15px 0;
        }
        div.stButton > button:first-child {
            background-color: #800020; color: #FFFFFF; font-weight: 600; border-radius: 10px; border: none; padding: 10px 24px;
        }
        div.stButton > button:first-child:hover { background-color: #5C0017; color: #FFFFFF; }
    </style>
    """

st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# 5. AUDIO ALERT FUNCTION
def play_beep_js():
    beep_code = """
    <script>
    try {
        var audioCtx = new (window.AudioContext || window.webkitAudioContext)();
        var osc = audioCtx.createOscillator();
        var gain = audioCtx.createGain();
        osc.type = "sine";
        osc.frequency.setValueAtTime(659.25, audioCtx.currentTime);
        gain.gain.setValueAtTime(0.15, audioCtx.currentTime);
        gain.gain.exponentialRampToValueAtTime(0.001, audioCtx.currentTime + 0.35);
        osc.connect(gain);
        gain.connect(audioCtx.destination);
        osc.start();
        osc.stop(audioCtx.currentTime + 0.35);
    } catch(e) {}
    </script>
    """
    st.components.v1.html(beep_code, height=0, width=0)

# 6. INITIALIZE SESSION STATES
if "camera_running" not in st.session_state:
    st.session_state.camera_running = False
if "alert_count" not in st.session_state:
    st.session_state.alert_count = 0
if "session_start_time" not in st.session_state:
    st.session_state.session_start_time = None
if "health_score" not in st.session_state:
    st.session_state.health_score = 90
if "pomo_start_time" not in st.session_state:
    st.session_state.pomo_start_time = time.time()
if "pomo_mode" not in st.session_state:
    st.session_state.pomo_mode = "Work Sprint"

# 7. HEADER
st.markdown("""
<div class="header-box">
    <h1>Postly</h1>
    <p>AI Shoulder Slump & Posture Tracking Assistant</p>
</div>
""", unsafe_allow_html=True)

col_cam, col_metrics = st.columns([1.5, 1.0], gap="medium")

with col_cam:
    st.markdown("### 🎥 Live Posture & Slump Feed")
    b1, b2 = st.columns(2)
    with b1:
        if st.button("▶️ Start Webcam", use_container_width=True):
            st.session_state.camera_running = True
            if st.session_state.session_start_time is None:
                st.session_state.session_start_time = time.time()
    with b2:
        if st.button("⏹️ Stop Webcam", use_container_width=True):
            st.session_state.camera_running = False

    camera_placeholder = st.empty()
    if not st.session_state.camera_running:
        camera_placeholder.info("Click **'▶️ Start Webcam'** above to begin monitoring.")

with col_metrics:
    st.markdown("### 📊 Real-Time Status & Metrics")
    alert_placeholder = st.empty()
    alert_placeholder.markdown('<div class="alert-banner-neutral">ℹ️ Camera is inactive. Start camera to view alerts.</div>', unsafe_allow_html=True)
    
    m1, m2 = st.columns(2)
    with m1:
        dist_metric = st.empty()
        dist_metric.markdown('<div class="metric-card"><div class="metric-title">Shoulder Span</div><div class="metric-value">-- px</div><div class="metric-subtitle">Proximity metric</div></div>', unsafe_allow_html=True)
    with m2:
        posture_metric = st.empty()
        posture_metric.markdown('<div class="metric-card"><div class="metric-title">Posture Status</div><div class="metric-value">Idle</div><div class="metric-subtitle">Awaiting feed</div></div>', unsafe_allow_html=True)

    pomo_metric_placeholder = st.empty()
    plant_metric_placeholder = st.empty()

# 8. RUN WEBCAM WITH CALIBRATED POSTURE & SLUMP TRACKING
if st.session_state.camera_running:
    xml_path = "haarcascade_frontalface_default.xml"
    if not os.path.exists(xml_path):
        url = "https://raw.githubusercontent.com/opencv/opencv/master/data/haarcascades/haarcascade_frontalface_default.xml"
        urllib.request.urlretrieve(url, xml_path)

    face_cascade = cv2.CascadeClassifier(xml_path)
    cap = cv2.VideoCapture(int(camera_id))
    
    if not cap.isOpened() or face_cascade.empty():
        st.error("❌ Could not open camera or load detection model.")
        st.session_state.camera_running = False
    else:
        last_beep_time = 0
        baseline_y = None  # To lock in your normal posture height when you first start!
        
        while cap.isOpened() and st.session_state.camera_running:
            success, frame = cap.read()
            if not success:
                break
            
            frame = cv2.flip(frame, 1)
            height, width_frame, _ = frame.shape
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(40, 40))
            
            elapsed_sec = int(time.time() - st.session_state.session_start_time) if st.session_state.session_start_time else 0
            mins, secs = divmod(elapsed_sec, 60)
            time_str = f"{mins:02d}:{secs:02d}"

            elapsed_pomo = time.time() - st.session_state.pomo_start_time
            target_pomo = work_mins if st.session_state.pomo_mode == "Work Sprint" else break_mins
            pomo_time_left = int(target_pomo - elapsed_pomo)
            
            if pomo_time_left <= 0:
                if st.session_state.pomo_mode == "Work Sprint":
                    st.session_state.pomo_mode = "Break"
                else:
                    st.session_state.pomo_mode = "Work Sprint"
                st.session_state.pomo_start_time = time.time()
                pomo_time_left = work_mins if st.session_state.pomo_mode == "Work Sprint" else break_mins

            pomo_mins_disp, pomo_secs_disp = divmod(max(0, pomo_time_left), 60)

            if len(faces) > 0:
                (x, y, w, h) = max(faces, key=lambda f: f[2] * f[3])
                
                # Dynamic shoulder mapping coordinates
                shoulder_width = int(w * 2.2)
                shoulder_left_x = max(10, x - int(w * 0.6))
                shoulder_right_x = min(width_frame - 10, x + w + int(w * 0.6))
                shoulder_y = min(height - 10, y + h + int(h * 0.7))
                
                current_head_y = y + (h // 2)
                
                # Set baseline posture height during the first few frames you sit straight
                if baseline_y is None:
                    baseline_y = current_head_y
                
                # Slump calculation based on how much your head drops *relative to your starting upright position*
                slump_drop = current_head_y - baseline_y
                
                is_too_close = shoulder_width > distance_threshold
                is_slumping = slump_drop > 45  # Triggers if you slouch/drop down by 45+ pixels
                
                if is_too_close:
                    status = "TOO CLOSE"
                    box_color = (0, 0, 255)
                    alert_msg = f"🚨 <strong>Warning: Sitting too close to screen!</strong>"
                elif is_slumping:
                    status = "SLUMPING DETECTED"
                    box_color = (0, 140, 255)
                    alert_msg = "⚠️ <strong>Posture Alert: Slouching/Slump detected!</strong> Sit back up."
                else:
                    status = "OPTIMAL POSTURE"
                    box_color = (0, 200, 80)
                    alert_msg = "✅ <strong>Optimal Posture & Alignment!</strong> Keep it up!"

                if is_too_close or is_slumping:
                    alert_placeholder.markdown(f'<div class="alert-banner-danger">{alert_msg}</div>', unsafe_allow_html=True)
                    st.session_state.health_score = max(20, st.session_state.health_score - 1)
                    if time.time() - last_beep_time > 2.0:
                        st.session_state.alert_count += 1
                        if sound_enabled:
                            play_beep_js()
                        last_beep_time = time.time()
                else:
                    alert_placeholder.markdown(f'<div class="alert-banner-success">{alert_msg}</div>', unsafe_allow_html=True)
                    st.session_state.health_score = min(100, st.session_state.health_score + 1)

                # Draw Shoulder & Posture Line on Feed
                cv2.rectangle(frame, (x, y), (x+w, y+h), box_color, 2)
                cv2.circle(frame, (shoulder_left_x, shoulder_y), 8, box_color, -1)
                cv2.circle(frame, (shoulder_right_x, shoulder_y), 8, box_color, -1)
                cv2.line(frame, (shoulder_left_x, shoulder_y), (shoulder_right_x, shoulder_y), box_color, 3)
                cv2.putText(frame, f"Status: {status}", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, box_color, 2)
                
                dist_metric.markdown(f'<div class="metric-card"><div class="metric-title">Shoulder Span</div><div class="metric-value">{shoulder_width} px</div><div class="metric-subtitle">Limit: {distance_threshold}px</div></div>', unsafe_allow_html=True)
                posture_metric.markdown(f'<div class="metric-card"><div class="metric-title">Posture Status</div><div class="metric-value">{status}</div><div class="metric-subtitle">Slump drop: {int(slump_drop)}px</div></div>', unsafe_allow_html=True)
            else:
                alert_placeholder.markdown('<div class="alert-banner-neutral">🔍 <strong>Searching for upper body...</strong><br>Center yourself in front of the camera.</div>', unsafe_allow_html=True)
                dist_metric.markdown(f'<div class="metric-card"><div class="metric-title">Shoulder Span</div><div class="metric-value">-- px</div><div class="metric-subtitle">No user found</div></div>', unsafe_allow_html=True)
                posture_metric.markdown(f'<div class="metric-card"><div class="metric-title">Posture Status</div><div class="metric-value">Searching</div><div class="metric-subtitle">No user</div></div>', unsafe_allow_html=True)

            score = st.session_state.health_score
            if score >= 85:
                plant_level = "🌸 Level 3: Blooming Flower"
            elif score >= 50:
                plant_level = "🌱 Level 2: Growing Bud"
            else:
                plant_level = "🥀 Level 1: Wilting Sprout"

            pomo_metric_placeholder.markdown(f'<div class="metric-card" style="margin-top:12px;"><div class="metric-title">🍅 Pomodoro ({st.session_state.pomo_mode})</div><div class="metric-value">{pomo_mins_disp:02d}:{pomo_secs_disp:02d}</div><div class="metric-subtitle">Active Sprint Timer</div></div>', unsafe_allow_html=True)
            plant_metric_placeholder.markdown(f'<div class="metric-card" style="margin-top:12px;"><div class="metric-title">🌿 Postly Plant Status</div><div class="metric-value">{score}%</div><div class="metric-subtitle">{plant_level}</div></div>', unsafe_allow_html=True)

            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            camera_placeholder.image(frame_rgb, channels="RGB", use_container_width=True)
            time.sleep(0.03)

        cap.release()

# 9. SESSION SUMMARY REPORT SECTION (Bottom)
st.markdown("---")
st.markdown("### 📋 Session Summary Report")
r1, r2, r3 = st.columns(3)
with r1:
    session_duration_mins = int((time.time() - st.session_state.session_start_time) // 60) if st.session_state.session_start_time else 0
    st.metric("Total Session Time", f"{session_duration_mins} mins")
with r2:
    st.metric("Total Posture Alerts Caught", st.session_state.alert_count)
with r3:
    st.metric("Ergonomic Health Score", f"{st.session_state.health_score}%")