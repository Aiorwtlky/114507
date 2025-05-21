import sys
import os
import av
import threading
import streamlit as st
import streamlit_nested_layout
from streamlit_webrtc import VideoHTMLAttributes, webrtc_streamer

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


from detection.audio_handling import AudioFrameHandler
from detection.drowsy_detection import VideoFrameHandler

# Define the audio file to use.
alarm_file_path = os.path.join("assets", "audio", "wake_up.wav")

# Streamlit Components
st.set_page_config(
    page_title="Drowsiness Detection | LearnOpenCV",
    page_icon="https://learnopencv.com/wp-content/uploads/2017/12/favicon.png",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        "About": "### Visit www.learnopencv.com for more exciting tutorials!!!",
    },
)

col1, col2 = st.columns(spec=[6, 2], gap="medium")

with col1:
    st.title("Drowsiness Detection!!!🥱😪😴")
    with st.container():
        c1, c2 = st.columns(spec=[1, 1])
        with c1:
            WAIT_TIME = st.slider("Seconds to wait before sounding alarm:", 0.0, 5.0, 1.0, 0.25)
        with c2:
            EAR_THRESH = st.slider("Eye Aspect Ratio threshold:", 0.0, 0.4, 0.18, 0.01)

thresholds = {
    "EAR_THRESH": EAR_THRESH,
    "WAIT_TIME": WAIT_TIME,
}

video_handler = VideoFrameHandler()
audio_handler = AudioFrameHandler(sound_file_path=alarm_file_path)

lock = threading.Lock()
shared_state = {"play_alarm": False}

def video_frame_callback(frame: av.VideoFrame):
    frame = frame.to_ndarray(format="bgr24")
    frame, play_alarm = video_handler.process(frame, thresholds)
    with lock:
        shared_state["play_alarm"] = play_alarm
    return av.VideoFrame.from_ndarray(frame, format="bgr24")

def audio_frame_callback(frame: av.AudioFrame):
    with lock:
        play_alarm = shared_state["play_alarm"]
    new_frame = audio_handler.process(frame, play_sound=play_alarm)
    return new_frame

with col1:
    ctx = webrtc_streamer(
        key="drowsiness-detection",
        video_frame_callback=video_frame_callback,
        audio_frame_callback=audio_frame_callback,
        rtc_configuration={"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]},
        media_stream_constraints={"video": {"height": {"ideal": 480}}, "audio": True},
        video_html_attrs=VideoHTMLAttributes(autoPlay=True, controls=False, muted=False),
    )

with col2:
    # 如果你沒有ads.py可以移除下面這段
    # st.markdown(css_string, unsafe_allow_html=True)
    pass
