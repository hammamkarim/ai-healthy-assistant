# AI HEALTHY ASSISTANT
# UAS Gen AI
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


# =========================================================
# SESSION STATE INIT
# (akar dari banyak error sebelumnya: variabel ini dipakai
# di kode lama tapi tidak pernah di-set default-nya)
# =========================================================

if "page" not in st.session_state:
    st.session_state.page = "Dashboard"

if "chat" not in st.session_state:
    # list of tuple: ("user", text) atau ("ai", text, audio_path)
    st.session_state.chat = []

if "chat_history" not in st.session_state:
    # list of dict {"role": ..., "content": ...} -> memory utk LLM
    # ini PERSIS format yang dipakai parameter `history` di
    # generate_health_advice() pada main.py asli
    st.session_state.chat_history = []

if "profile" not in st.session_state:
    st.session_state.profile = None


def go(page):
    st.session_state.page = page
    st.rerun()


def profile_is_complete(profile):
    if not profile:
        return False
    required = ["gender", "age", "weight", "height", "activity", "goal"]
    return all(str(profile.get(k, "")).strip() != "" for k in required)


# SIDEBAR
st.sidebar.image(img("logo.png"), width=100)
st.sidebar.markdown("## AI Healthy Assistant")
st.sidebar.markdown("---")

if st.sidebar.button("🏠 Dashboard"):
    go("Dashboard")

if st.sidebar.button("👤 Profil"):
    go("Profil")

if st.sidebar.button("💬 Konsultasi"):
    go("Konsultasi")

if st.sidebar.button("📊 Insight"):
    go("Insight")

st.sidebar.markdown("---")
st.sidebar.caption("Asisten kesehatan berbasis AI")


# =========================================================
# DASHBOARD
# =========================================================
if st.session_state.page == "Dashboard":

    st.markdown("""
    <div style="
        text-align:center;
        padding:50px 20px;
    ">
        <h1>
            AI Healthy Assistant
        </h1>

        <p style="
            color:#64748B;
            font-size:18px;
        ">
            Asisten kesehatan berbasis AI yang memberikan
            rekomendasi personal berdasarkan kondisi kamu.
        </p>
    </div>
    """, unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)

    with c1:
        st.metric("AI Recommendation", "Aktif")

    with c2:
        st.metric("Voice Assistant", "Aktif")

    with c3:
        st.metric("Personal Health", "Aktif")

    st.divider()

    col1, col2, col3 = st.columns(3)

    with col1:
        st.info("💡 Rekomendasi kesehatan personal")

    with col2:
        st.info("🧠 AI mengingat riwayat konsultasi")

    with col3:
        st.info("🔊 Hasil dapat didengarkan")


# =========================================================
# PROFIL
# =========================================================
elif st.session_state.page == "Profil":

    st.title("👤 Profil Kesehatan")

    existing = st.session_state.profile or {}

    nama = st.text_input("Nama", value=existing.get("nama", ""))

    gender = st.selectbox(
        "Jenis Kelamin",
        ["Laki-laki", "Perempuan"],
        index=["Laki-laki", "Perempuan"].index(existing["gender"]) if existing.get("gender") in ["Laki-laki", "Perempuan"] else 0
    )

    umur = st.number_input(
        "Umur",
        min_value=1,
        max_value=100,
        value=int(existing.get("age", 1)) if str(existing.get("age", "")).isdigit() else 1
    )

    berat = st.number_input(
        "Berat Badan (kg)",
        min_value=1,
        value=int(existing.get("weight", 1)) if str(existing.get("weight", "")).isdigit() else 1
    )

    tinggi = st.number_input(
        "Tinggi Badan (cm)",
        min_value=1,
        value=int(existing.get("height", 1)) if str(existing.get("height", "")).isdigit() else 1
    )

    aktivitas = st.selectbox(
        "Aktivitas Harian",
        ["Rendah", "Sedang", "Tinggi"],
        index=["Rendah", "Sedang", "Tinggi"].index(existing["activity"]) if existing.get("activity") in ["Rendah", "Sedang", "Tinggi"] else 0
    )

    tujuan = st.text_area("Tujuan Kesehatan", value=existing.get("goal", ""))

    if st.button("Simpan Profil"):

        if not nama.strip() or not tujuan.strip():
            st.warning("Mohon lengkapi nama dan tujuan kesehatan terlebih dahulu.")
        else:
            # Catatan: main.py asli memakai profile['gender'], profile['age'], dst
            # sebagai bagian dari f-string (tidak perlu tipe data spesifik),
            # jadi int dari number_input tetap aman dipakai langsung.
            st.session_state.profile = {
                "nama": nama,
                "gender": gender,
                "age": umur,
                "weight": berat,
                "height": tinggi,
                "activity": aktivitas,
                "goal": tujuan
            }

            st.success("Profil berhasil disimpan")

    if tinggi:
        bmi = berat / ((tinggi / 100) ** 2)
        st.metric("BMI", f"{bmi:.1f}")


# =========================================================
# KONSULTASI
# =========================================================
elif st.session_state.page == "Konsultasi":

    st.title("💬 Konsultasi Kesehatan")

    if not profile_is_complete(st.session_state.profile):
        st.warning("Profil kamu belum lengkap. Silakan isi profil terlebih dahulu sebelum memulai konsultasi.")
        if st.button("Isi Profil Sekarang"):
            go("Profil")
        st.stop()

    # Tampilkan riwayat chat
    if not st.session_state.chat:
        st.markdown("""
        <div style="
            text-align:center;
            margin-top:20px;
            margin-bottom:40px;
            color:#94A3B8;
            font-size:16px;
        ">
            💬 Belum ada percakapan<br>
            Mulai dengan mengetik keluhan kamu di bawah
        </div>
        """, unsafe_allow_html=True)
    else:
        for entry in st.session_state.chat:
            role, text = entry[0], entry[1]
            if role == "user":
                st.markdown(f'<div class="user">{text}</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="ai">{text}</div>', unsafe_allow_html=True)
                audio_path = entry[2] if len(entry) > 2 else None
                if audio_path and os.path.exists(audio_path):
                    st.audio(audio_path, format="audio/wav")

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

    # Pakai st.form supaya input otomatis kosong setelah submit
    # (clear_on_submit=True) -> menghindari konflik widget key
    # yang sebelumnya bikin error saat reset manual.
    with st.form("chat_form", clear_on_submit=True):
        col1, col2 = st.columns([6, 1])

        with col1:
            user_input = st.text_input(
                "",
                key="input_box",
                placeholder="Ketik keluhan atau pertanyaan kamu...",
                label_visibility="collapsed"
            )

        with col2:
            send = st.form_submit_button("Kirim ➤", use_container_width=True)

    # SEND LOGIC
    if send:

        clean_input = user_input.strip()

        if not clean_input:
            st.toast("Input tidak boleh kosong!", icon="⚠️")
        else:
            try:
                with st.spinner("AI sedang menganalisis..."):

                    # generate_health_advice() di main.py ASLI
                    # mengembalikan 2 nilai: (response, sources)
                    response, sources = generate_health_advice(
                        clean_input,
                        st.session_state.chat_history,
                        st.session_state.profile
                    )

                    audio_file = text_to_audio(response)

                # Tambah ke chat untuk ditampilkan di UI
                st.session_state.chat.append(("user", clean_input))
                st.session_state.chat.append(("ai", response, audio_file))

                st.rerun()

            except Exception as e:
                st.toast("Gagal memproses permintaan", icon="❌")
                st.error(f"ERROR: {e}")

    if st.session_state.chat:
        if st.button("🗑️ Reset Percakapan"):
            st.session_state.chat = []
            st.session_state.chat_history.clear()
            st.rerun()


# =========================================================
# INSIGHT
# =========================================================
elif st.session_state.page == "Insight":

    st.title("📊 Insight Kesehatan")

    st.metric("Health Score", "82%")

    st.progress(82)

    st.markdown("### Prioritas Hari Ini")

    st.success("Tidur lebih teratur")
    st.success("Perbanyak minum air")
    st.success("Aktivitas fisik 30 menit")

    st.markdown("### Riwayat Konsultasi")

    if not st.session_state.chat:
        st.info("Belum ada riwayat konsultasi.")
    else:
        for entry in st.session_state.chat[-6:]:
            role, text = entry[0], entry[1]
            if role == "user":
                st.write("👤", text)


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