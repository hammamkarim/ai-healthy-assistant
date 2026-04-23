# AI HEALTHY ASSISTANT 
import streamlit as st
import os
from main import generate_health_advice, text_to_audio

# CONFIG
st.set_page_config(
    page_title="AI Healthy Assistant",
    layout="wide",
    initial_sidebar_state="expanded"
)

# PATH
BASE_DIR = os.path.dirname(__file__)
def img(file):
    return os.path.join(BASE_DIR, "assets", file)

# COLOR SYSTEM
PRIMARY = "#2E7D66"
PRIMARY_LIGHT = "#4CAF50"
BG = "#F7FAF9"
TEXT = "#2D3748"
SUBTEXT = "#718096"

# STYLE
st.markdown(f"""
<style>

body {{
    background-color: {BG};
}}

.block-container {{
    padding-top: 2rem;
}}

/* Sidebar */
section[data-testid="stSidebar"] {{
    background: linear-gradient(180deg, #E8F5E9, #F1F8F5);
}}

/* Button */
.stButton > button {{
    background: {PRIMARY};
    color: white;
    border-radius: 25px;
    height: 45px;
    font-weight: 600;
}}

/* Hero */
.hero {{
    text-align: center;
    margin-top: 40px;
}}

.hero h1 {{
    font-size: 57px;
    font-weight: 700;
}}

.hero span {{
    color: {PRIMARY};
}}

.hero p {{
    font-size: 18px;
    color: {SUBTEXT};
}}

/* Chat */
.user {{
    background: {PRIMARY};
    color: white;
    padding: 12px;
    border-radius: 15px;
    margin-left: auto;
    max-width: 60%;
    margin-bottom: 10px;
}}

.ai {{
    background: #F8FAFC;
    padding: 12px;
    border-radius: 15px;
    max-width: 70%;
    margin-bottom: 10px;
}}

.footer {{
    margin-top: 80px;
    padding: 30px 20px;
    background: #ffffff;
    border-top: 1px solid #E2E8F0;
    text-align: center;
}}

</style>
""", unsafe_allow_html=True)


# NAVIGATION
if "page" not in st.session_state:
    st.session_state.page = "Beranda"

def go(page):
    st.session_state.page = page
    st.rerun()


# SIDEBAR
st.sidebar.image(img("logo.png"), width=100)
st.sidebar.markdown("## AI Healthy Assistant")
st.sidebar.markdown("---")

if st.sidebar.button("🏠 Beranda"):
    go("Beranda")

if st.sidebar.button("💬 Konsultasi"):
    go("Konsultasi")

st.sidebar.markdown("---")
st.sidebar.caption("Asisten kesehatan berbasis AI")


# BERANDA
if st.session_state.page == "Beranda":

    # HERO
    st.markdown(f"""
    <div class="hero">
        <h1><span style="color:black;">AI Healthy </span><span style="color:#2E7D66;">Assistant</span></h1>
        <p>Asisten pintar untuk membantu pola hidup sehat kamu</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # BUTTON
    col1, col2, col3 = st.columns([2.2,2,1])

    with col2:
        st.markdown("<div style='display:flex; justify-content:center;'>", unsafe_allow_html=True)
        
        if st.button("Mulai Konsultasi"):
            go("Konsultasi")
        
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<br><br>", unsafe_allow_html=True)

    # FEATURES
    col1, col2, col3 = st.columns(3)

    with col1:
        with st.container(border=True):
            st.image(img("chat.png"), width=80)
            st.markdown("### Chat dengan AI")
            st.write("Tanyakan kondisi kesehatan kamu secara langsung")

    with col2:
        with st.container(border=True):
            st.image(img("heart.png"), width=80)
            st.markdown("### Rekomendasi Sehat")
            st.write("Saran pola hidup sehat yang relevan")

    with col3:
        with st.container(border=True):
            st.image(img("audio.png"), width=80)
            st.markdown("### Audio Penjelasan")
            st.write("Dengarkan hasil rekomendasi dalam bentuk suara")


# KONSULTASI (UI Halaman 2)
elif st.session_state.page == "Konsultasi":

    st.markdown("## 💬 Konsultasi Kesehatan")
    st.markdown("<br>", unsafe_allow_html=True)

    # INIT
    if "chat" not in st.session_state:
        st.session_state.chat = []

    if "input_text" not in st.session_state:
        st.session_state.input_text = ""

    # CHAT AREA
    with st.container():
        for role, text in st.session_state.chat:

            if role == "user":
                st.markdown(f"""
                <div style="
                    display:flex;
                    justify-content:flex-end;
                    margin-bottom:12px;
                ">
                    <div style="
                        background:{PRIMARY};
                        color:white;
                        padding:12px 16px;
                        border-radius:20px 20px 4px 20px;
                        max-width:60%;
                        box-shadow:0 2px 6px rgba(0,0,0,0.08);
                        font-size:14px;
                    ">
                        {text}
                    </div>
                </div>
                """, unsafe_allow_html=True)

            else:
                st.markdown(f"""
                <div style="
                    display:flex;
                    justify-content:flex-start;
                    margin-bottom:12px;
                ">
                    <div style="
                        background:#ffffff;
                        padding:12px 16px;
                        border-radius:20px 20px 20px 4px;
                        max-width:70%;
                        border:1px solid #E2E8F0;
                        box-shadow:0 2px 6px rgba(0,0,0,0.05);
                        font-size:14px;
                    ">
                        {text}
                    </div>
                </div>
                """, unsafe_allow_html=True)

                # AUDIO MUNCUL HANYA UNTUK AI NYA
                audio = text_to_audio(text)
                if audio:
                    st.markdown("""
                    <div style="
                        margin-top:10px;
                        margin-bottom:12px;
                        padding:10px 12px;
                        border-radius:12px;
                        background:#F1F5F9;
                        border:1px solid #E2E8F0;
                        max-width:70%;
                    ">
                        <div style="
                            font-size:12px;
                            color:#64748B;
                            margin-bottom:6px;
                        ">
                            🔊 Audio penjelasan
                        </div>
                    """, unsafe_allow_html=True)

                    st.audio(audio)

                    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)


    # INPUT BAR
    st.markdown("""
    <style>
    .input-bar {
        background: white;
        padding: 10px;
        border-radius: 20px;
        border: 1px solid #E2E8F0;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
    }
    </style>
    """, unsafe_allow_html=True)

    if not st.session_state.chat:
        st.markdown("""
        <div style="
            text-align:center;
            margin-top:20px;
            margin-bottom:80px;
            color:#94A3B8;
            font-size:16px;
        ">
            💬 Belum ada percakapan<br>
            Mulai dengan mengetik keluhan kamu di bawah
        </div>
        """, unsafe_allow_html=True)


    col1, col2 = st.columns([6,1])

    with col1:
        user_input = st.text_input(
            "",
            value=st.session_state.input_text,
            key="input_box",
            placeholder="Ketik keluhan atau pertanyaan kamu...",
            label_visibility="collapsed"
        )

    with col2:
        send = st.button("Kirim ➤", use_container_width=True)


    # SEND LOGIC 
    if send:

        clean_input = user_input.strip()

        if not clean_input:
            st.toast("Input tidak boleh kosong!", icon="⚠️")
        else:
            try:
                with st.spinner("AI sedang menganalisis..."):
                    response = generate_health_advice(clean_input)

                # Tambah ke chat
                st.session_state.chat.append(("user", clean_input))
                st.session_state.chat.append(("ai", response))

                # Reset input
                st.session_state.input_text = ""

                st.rerun()

            except Exception as e:
                st.toast("Gagal memproses permintaan", icon="❌")
                print("ERROR:", e)


# FOOTER
st.markdown(
"""
<div class="footer">

<div style="font-weight:600; color:#2E7D66; font-size:16px;">
AI Healthy Assistant
</div>

<div style="margin-top:6px;">
Membantu kamu menjaga pola hidup sehat dengan bantuan AI
</div>

<div style="margin-top:10px; font-size:12px; color:#A0AEC0;">
Aplikasi ini hanya memberikan edukasi dan tidak menggantikan tenaga medis profesional.
</div>

</div>
""",
unsafe_allow_html=True
)