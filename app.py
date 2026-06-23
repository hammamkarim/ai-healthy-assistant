# ============================================
# FILE INI: app.py  (BUKAN main.py)
# ============================================
# AI HEALTHY ASSISTANT
# UAS Gen AI
import streamlit as st
import os
import html

# main.py TIDAK diubah sama sekali.
# Import ini akan otomatis menjalankan semua proses loading
# (LLM, embedding model, FAISS, Piper voice) yang ada di
# top-level main.py -> ini NORMAL, hanya terjadi sekali saat
# proses Streamlit pertama kali start (Python cache modul
# yang sudah di-import, jadi tidak akan reload berulang
# setiap user berinteraksi di UI).
from main import generate_health_advice, generate_health_advice_stream, get_last_sources, text_to_audio

# CONFIG
st.set_page_config(
    page_title="AI Healthy Assistant",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ===============================
# HIDE STREAMLIT HEADER
# ===============================
st.markdown("""
<style>

/* Header atas */
header {
    visibility: hidden;
}

/* Toolbar (Deploy & menu) */
[data-testid="stToolbar"] {
    display: none;
}

/* Header Streamlit */
[data-testid="stHeader"] {
    display: none;
}

/* Garis dekorasi atas */
[data-testid="stDecoration"] {
    display: none;
}

/* Menu kanan atas */
#MainMenu {
    visibility: hidden;
}

/* Footer bawaan Streamlit */
footer {
    visibility: hidden;
}

</style>
""", unsafe_allow_html=True)
#############################################

# PATH
BASE_DIR = os.path.dirname(__file__)
def img(file):
    return os.path.join(BASE_DIR, "assets", file)


def icon(name: str, size: int = 20) -> str:
    """Render satu Material Symbols icon sebagai HTML span."""
    return f'<span class="material-symbols-outlined" style="font-size:{size}px; vertical-align:middle;">{name}</span>'


# =========================================================
# COLOR SYSTEM (diturunkan dari design inspiration)
# =========================================================
PRIMARY = "#07644E"
PRIMARY_CONTAINER = "#2E7D66"
PRIMARY_LIGHT = "#88D6BA"
SECONDARY = "#006E1C"
SECONDARY_CONTAINER = "#91F78E"
TERTIARY = "#4243CF"
TERTIARY_CONTAINER = "#5B5EE9"
BG_FROM = "#F6FAF9"
BG_TO = "#E0F2F1"
TEXT = "#181C1C"
SUBTEXT = "#3F4944"
OUTLINE = "#BEC9C3"
ERROR = "#BA1A1A"


# =========================================================
# GLOBAL STYLE
# =========================================================
st.markdown(f"""
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:opsz,wght,FILL,GRAD@20..48,100..700,0..1,-50..200&display=swap">

<style>

html, body, [class*="css"] {{
    font-family: 'Inter', sans-serif;
}}

.material-symbols-outlined {{
    font-variation-settings: 'FILL' 0, 'wght' 400, 'GRAD' 0, 'opsz' 24;
}}

.stApp {{
    background: linear-gradient(135deg, {BG_FROM} 0%, {BG_TO} 100%);
}}

.block-container {{
    padding-top: 2rem;
    padding-bottom: 3rem;
    max-width: 1280px;
}}

/* ---------------- SIDEBAR ---------------- */
section[data-testid="stSidebar"] {{
    background: rgba(255,255,255,0.55);
    backdrop-filter: blur(16px);
    border-right: 1px solid rgba(255,255,255,0.6);
}}

section[data-testid="stSidebar"] .stButton > button {{
    background: transparent;
    color: {SUBTEXT};
    border: none;
    border-radius: 16px;
    text-align: left;
    font-weight: 600;
    height: 48px;
    width: 100%;
    transition: all 0.2s ease;
}}

section[data-testid="stSidebar"] .stButton > button:hover {{
    background: rgba(255,255,255,0.6);
    color: {PRIMARY};
}}

section[data-testid="stSidebar"] .stButton > button:focus {{
    box-shadow: none;
}}

.sidebar-brand {{
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 4px 4px 20px 4px;
}}

.sidebar-brand-icon {{
    width: 42px;
    height: 42px;
    border-radius: 14px;
    background: {PRIMARY};
    display: flex;
    align-items: center;
    justify-content: center;
    box-shadow: 0 4px 14px rgba(7,100,78,0.25);
    flex-shrink: 0;
}}

.sidebar-brand-icon .material-symbols-outlined {{
    color: white;
    font-variation-settings: 'FILL' 1;
}}

.sidebar-brand h1 {{
    font-size: 19px;
    font-weight: 800;
    color: {PRIMARY};
    margin: 0;
    line-height: 1.1;
}}

.sidebar-brand p {{
    font-size: 10px;
    font-weight: 700;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    color: {SUBTEXT};
    opacity: 0.6;
    margin: 0;
}}

/* Active nav item override via data attribute trick is not available in
   pure Streamlit, so the active page is indicated with a colored badge
   rendered separately above the button group (see sidebar code). */

/* ---------------- BUTTONS (general) ---------------- */
.stButton > button {{
    border-radius: 16px;
    font-weight: 700;
}}

div[data-testid="stForm"] .stButton > button,
.main .stButton > button {{
    background: {PRIMARY};
    color: white;
    border: none;
    height: 46px;
    box-shadow: 0 4px 14px rgba(7,100,78,0.2);
    transition: all 0.2s ease;
}}

.main .stButton > button:hover {{
    filter: brightness(1.08);
    transform: translateY(-1px);
}}



.glass-card:hover {{
    transform: translateY(-3px);
    box-shadow: 0 12px 36px rgba(7,100,78,0.10);
}}

.glass-card-flat {{
    backdrop-filter: blur(20px);
    background: rgba(255,255,255,0.45);
    border: 1px solid rgba(255,255,255,0.6);
    border-radius: 24px;
    padding: 22px;
}}

/* ---------------- HERO ---------------- */
.hero-section {{
    position: relative;
    overflow: hidden;
    border-radius: 32px;
    padding: 48px 44px;
    background: linear-gradient(135deg, rgba(7,100,78,0.10), rgba(7,100,78,0.03) 60%, transparent);
    border: 1px solid rgba(255,255,255,0.5);
    margin-top: 25px;
}}

.hero-eyebrow {{
    display: inline-block;
    padding: 5px 16px;
    border-radius: 999px;
    background: rgba(7,100,78,0.10);
    color: {PRIMARY};
    font-weight: 800;
    font-size: 11px;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    margin-bottom: 18px;
}}

.hero-title {{
    font-size: 44px;
    line-height: 1.1;
    font-weight: 800;
    letter-spacing: -0.02em;
    color: {PRIMARY};
    margin: 0 0 14px 0;
}}

.hero-desc {{
    font-size: 17px;
    line-height: 1.6;
    color: {SUBTEXT};
    max-width: 560px;
    margin: 0;
}}

/* ---------------- METRIC CARDS ---------------- */
.metric-card {{
    backdrop-filter: blur(20px);
    background: rgba(255,255,255,0.45);
    border: 1px solid rgba(255,255,255,0.6);
    border-left: 4px solid var(--accent, {PRIMARY});
    border-radius: 26px;
    padding: 26px;
    height: 100%;
}}

.metric-card-top {{
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    margin-bottom: 22px;
}}

.metric-icon-box {{
    width: 44px;
    height: 44px;
    border-radius: 16px;
    background: var(--accent-soft, rgba(7,100,78,0.10));
    display: flex;
    align-items: center;
    justify-content: center;
}}

.metric-icon-box .material-symbols-outlined {{
    color: var(--accent, {PRIMARY});
    font-variation-settings: 'FILL' 1;
}}

.metric-badge {{
    padding: 4px 12px;
    border-radius: 999px;
    background: var(--accent-soft, rgba(7,100,78,0.10));
    color: var(--accent, {PRIMARY});
    font-size: 9px;
    font-weight: 900;
    text-transform: uppercase;
    letter-spacing: 0.04em;
}}

.metric-title {{
    font-size: 18px;
    font-weight: 700;
    color: {TEXT};
    margin: 0 0 4px 0;
}}

.metric-sub {{
    font-size: 13px;
    color: {SUBTEXT};
    opacity: 0.75;
    margin: 0 0 14px 0;
}}

.metric-value {{
    font-size: 26px;
    font-weight: 800;
    color: var(--accent, {PRIMARY});
}}

/* ---------------- INFO CARDS ---------------- */
.info-card {{
    backdrop-filter: blur(20px);
    background: rgba(255,255,255,0.45);
    border: 1px solid rgba(255,255,255,0.6);
    border-radius: 22px;
    padding: 20px;
    display: flex;
    gap: 16px;
    align-items: flex-start;
    height: 100%;
}}

.info-card-icon {{
    width: 50px;
    height: 50px;
    flex-shrink: 0;
    border-radius: 16px;
    background: rgba(255,255,255,0.7);
    border: 1px solid rgba(255,255,255,0.8);
    display: flex;
    align-items: center;
    justify-content: center;
    color: {PRIMARY};
}}

.info-card h4 {{
    font-size: 15px;
    font-weight: 700;
    color: {TEXT};
    margin: 0 0 4px 0;
}}

.info-card p {{
    font-size: 13px;
    color: {SUBTEXT};
    line-height: 1.5;
    margin: 0;
}}

/* ---------------- CHAT BUBBLES ---------------- */
.chat-row {{
    display: flex;
    margin-bottom: 14px;
    gap: 10px;
}}

.chat-row.user {{
    justify-content: flex-end;
}}

.chat-avatar {{
    width: 36px;
    height: 36px;
    border-radius: 50%;
    background: {PRIMARY};
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
}}

.chat-avatar .material-symbols-outlined {{
    color: white;
    font-size: 18px;
}}

.bubble-user {{
    background: {PRIMARY};
    color: white;
    padding: 14px 18px;
    border-radius: 18px 18px 4px 18px;
    max-width: 65%;
    font-size: 15px;
    line-height: 1.5;
}}

.bubble-ai {{
    background: rgba(255,255,255,0.65);
    backdrop-filter: blur(10px);
    border: 1px solid rgba(255,255,255,0.7);
    color: {TEXT};
    padding: 14px 18px;
    border-radius: 18px 18px 18px 4px;
    max-width: 70%;
    font-size: 15px;
    line-height: 1.6;
    white-space: pre-wrap;
}}

.chat-empty {{
    text-align: center;
    padding: 50px 20px;
    color: {SUBTEXT};
    opacity: 0.6;
}}

.chat-empty .material-symbols-outlined {{
    font-size: 40px;
    margin-bottom: 10px;
    display: block;
}}

/* ---------------- TEXT INPUTS ---------------- */
.stTextInput input, .stNumberInput input, .stTextArea textarea {{
    background: rgba(255,255,255,0.6) !important;
    border-radius: 14px !important;
    border: 1px solid rgba(255,255,255,0.8) !important;
}}

.stSelectbox > div > div {{
    background: rgba(255,255,255,0.6) !important;
    border-radius: 14px !important;
}}

/* ---------------- SECTION HEADER ---------------- */
.section-title {{
    font-size: 26px;
    font-weight: 700;
    color: {TEXT};
    margin: 0 0 4px 0;
    display: flex;
    align-items: center;
    gap: 10px;
}}

.section-title .material-symbols-outlined {{
    color: {PRIMARY};
    font-size: 28px;
}}

.section-sub {{
    font-size: 14px;
    color: {SUBTEXT};
    opacity: 0.7;
    margin-bottom: 24px;
}}

/* ---------------- FOOTER ---------------- */
.app-footer {{
    margin-top: 60px;
    padding: 26px 28px;
    border-radius: 22px;
    backdrop-filter: blur(16px);
    background: rgba(255,255,255,0.4);
    border: 1px solid rgba(255,255,255,0.6);
    text-align: center;
}}

.app-footer .footer-title {{
    font-weight: 800;
    color: {PRIMARY};
    font-size: 15px;
}}

.app-footer .footer-sub {{
    margin-top: 4px;
    font-size: 13px;
    color: {SUBTEXT};
}}

.app-footer .footer-disclaimer {{
    margin-top: 10px;
    font-size: 11px;
    color: {SUBTEXT};
    opacity: 0.6;
}}

/* ---------------- MISC ---------------- */
hr {{
    border-color: rgba(190,201,195,0.3) !important;
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


def calculate_bmi(weight, height):
    if not height:
        return None
    return weight / ((height / 100) ** 2)


def bmi_category(bmi):
    if bmi is None:
        return "-"
    if bmi < 18.5:
        return "Underweight"
    if bmi < 25:
        return "Ideal"
    if bmi < 30:
        return "Overweight"
    return "Obese"


# =========================================================
# SIDEBAR
# =========================================================
NAV_ITEMS = [
    ("Dashboard", "dashboard"),
    ("Profil", "person"),
    ("Konsultasi", "chat_bubble"),
    ("Insight", "monitoring"),
]

with st.sidebar:

    st.markdown(f"""
    <div class="sidebar-brand">
        <div class="sidebar-brand-icon">{icon('health_metrics', 22)}</div>
        <div>
            <h1>AI Healthy</h1>
            <p>Health Assistant</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    for page_name, icon_name in NAV_ITEMS:
        is_active = st.session_state.page == page_name

        if is_active:
            st.markdown(f"""
            <div style="
                background:{PRIMARY};
                color:white;
                border-radius:16px;
                padding:13px 16px;
                margin-bottom:6px;
                font-weight:700;
                font-size:14px;
                display:flex;
                align-items:center;
                gap:10px;
                box-shadow:0 4px 14px rgba(7,100,78,0.25);
            ">
                <span class="material-symbols-outlined" style="font-variation-settings:'FILL' 1; font-size:20px;">{icon_name}</span>
                {page_name}
            </div>
            """, unsafe_allow_html=True)
        else:
            if st.button(f"{page_name}", key=f"nav_{page_name}", use_container_width=True, icon=f":material/{icon_name}:"):
                go(page_name)

    st.markdown("<div style='margin: 18px 0;'></div>", unsafe_allow_html=True)

    if st.button("Mulai Konsultasi", key="nav_start_consult", use_container_width=True, icon=":material/add_circle:", type="primary"):
        go("Konsultasi")

    st.markdown("<hr style='margin:20px 0; opacity:0.3;'>", unsafe_allow_html=True)
    st.caption("Asisten kesehatan berbasis AI")


# =========================================================
# DASHBOARD
# =========================================================
if st.session_state.page == "Dashboard":

    profile = st.session_state.profile
    profile_name = profile.get("nama") if profile else None
    total_consult = len([1 for e in st.session_state.chat if e[0] == "user"])

    # --- HERO ---
    st.markdown(f"""
    <div class="hero-section">
        <span class="hero-eyebrow">{'Selamat Datang Kembali' if profile_name else 'Selamat Datang'}</span>
        <h1 class="hero-title">AI Healthy Assistant</h1>
        <p class="hero-desc">
            Asisten kesehatan berbasis AI yang memberikan rekomendasi personal
            berdasarkan kondisi kamu. Konsultasikan keluhanmu kapan saja, di mana saja.
        </p>
    </div>
    """, unsafe_allow_html=True)

    st.write("")

    bcol1, bcol2 = st.columns([1, 1])
    with bcol1:
        if st.button("Mulai Konsultasi", icon=":material/add_circle:", type="primary", use_container_width=True):
            go("Konsultasi")
    with bcol2:
        if st.button("Lengkapi Profil", icon=":material/edit:", use_container_width=True):
            go("Profil")

    st.write("")
    st.write("")

    # --- METRIC CARDS (bento row) ---
    m1, m2, m3 = st.columns(3)

    with m1:
        st.markdown(f"""
        <div class="metric-card" style="--accent:{PRIMARY}; --accent-soft:rgba(7,100,78,0.10);">
            <div class="metric-card-top">
                <div class="metric-icon-box">{icon('recommend', 22)}</div>
                <span class="metric-badge">Aktif</span>
            </div>
            <p class="metric-title">AI Recommendation</p>
            <p class="metric-sub">Rekomendasi berbasis RAG</p>
            <div class="metric-value">{total_consult} sesi</div>
        </div>
        """, unsafe_allow_html=True)

    with m2:
        st.markdown(f"""
        <div class="metric-card" style="--accent:{TERTIARY}; --accent-soft:rgba(66,67,207,0.10);">
            <div class="metric-card-top">
                <div class="metric-icon-box">{icon('mic', 22)}</div>
                <span class="metric-badge">Aktif</span>
            </div>
            <p class="metric-title">Voice Assistant</p>
            <p class="metric-sub">Jawaban dalam audio natural</p>
            <div class="metric-value">Siap Bicara</div>
        </div>
        """, unsafe_allow_html=True)

    with m3:
        bmi_val = None
        if profile and profile.get("weight") and profile.get("height"):
            try:
                bmi_val = calculate_bmi(float(profile["weight"]), float(profile["height"]))
            except (ValueError, ZeroDivisionError):
                bmi_val = None

        bmi_display = f"{bmi_val:.1f}" if bmi_val else "-"

        st.markdown(f"""
        <div class="metric-card" style="--accent:{SECONDARY}; --accent-soft:rgba(0,110,28,0.10);">
            <div class="metric-card-top">
                <div class="metric-icon-box">{icon('monitor_heart', 22)}</div>
                <span class="metric-badge">{'Aktif' if profile else 'Belum Diisi'}</span>
            </div>
            <p class="metric-title">Personal Health</p>
            <p class="metric-sub">Indeks Massa Tubuh (BMI)</p>
            <div class="metric-value">{bmi_display}</div>
        </div>
        """, unsafe_allow_html=True)

    st.write("")
    st.write("")

    # --- INFO CARDS ---
    i1, i2, i3 = st.columns(3)

    info_items = [
        ("medical_information", "Rekomendasi kesehatan personal", "Analisis berbasis profil dan riwayat kesehatanmu untuk saran yang relevan."),
        ("history_edu", "AI mengingat riwayat konsultasi", "Setiap sesi disimpan untuk memberikan konteks lebih baik pada saran berikutnya."),
        ("headset_mic", "Hasil dapat didengarkan", "Ubah jawaban AI menjadi audio yang jernih dengan suara natural."),
    ]

    for col, (icon_name, title, desc) in zip([i1, i2, i3], info_items):
        with col:
            st.markdown(f"""
            <div class="info-card">
                <div class="info-card-icon">{icon(icon_name, 24)}</div>
                <div>
                    <h4>{title}</h4>
                    <p>{desc}</p>
                </div>
            </div>
            """, unsafe_allow_html=True)


# =========================================================
# PROFIL
# =========================================================
elif st.session_state.page == "Profil":

    st.markdown(f"""
    <p class="section-title">{icon('person', 28)} Profil Kesehatan</p>
    <p class="section-sub">Lengkapi data dirimu agar AI bisa memberi rekomendasi yang akurat.</p>
    """, unsafe_allow_html=True)

    existing = st.session_state.profile or {}

    col_form, col_summary = st.columns([3, 2], gap="large")

    with col_form:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)

        nama = st.text_input("Nama", value=existing.get("nama", ""))

        fcol1, fcol2 = st.columns(2)
        with fcol1:
            gender = st.selectbox(
                "Jenis Kelamin",
                ["Laki-laki", "Perempuan"],
                index=["Laki-laki", "Perempuan"].index(existing["gender"]) if existing.get("gender") in ["Laki-laki", "Perempuan"] else 0
            )
        with fcol2:
            umur = st.number_input(
                "Umur",
                min_value=1,
                max_value=100,
                value=int(existing.get("age", 1)) if str(existing.get("age", "")).isdigit() else 1
            )

        fcol3, fcol4 = st.columns(2)
        with fcol3:
            berat = st.number_input(
                "Berat Badan (kg)",
                min_value=1,
                value=int(existing.get("weight", 1)) if str(existing.get("weight", "")).isdigit() else 1
            )
        with fcol4:
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

        if st.button("Simpan Profil", icon=":material/save:", type="primary", use_container_width=True):
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
                st.rerun()

        st.markdown('</div>', unsafe_allow_html=True)

    with col_summary:
        bmi = calculate_bmi(berat, tinggi)
        category = bmi_category(bmi)

        category_color = {
            "Underweight": TERTIARY,
            "Ideal": SECONDARY,
            "Overweight": "#B8860B",
            "Obese": ERROR,
        }.get(category, PRIMARY)

        st.markdown(f"""
        <div class="glass-card-flat" style="margin-bottom:18px;">
            <p style="font-size:13px; font-weight:700; color:{SUBTEXT}; text-transform:uppercase; letter-spacing:0.04em; margin:0 0 4px 0;">BMI Terhitung</p>
            <div style="display:flex; align-items:baseline; gap:10px;">
                <span style="font-size:38px; font-weight:800; color:{PRIMARY};">{f"{bmi:.1f}" if bmi else "-"}</span>
                <span style="font-size:13px; font-weight:700; color:{category_color};">{category}</span>
            </div>
            <p style="font-size:13px; color:{SUBTEXT}; margin-top:10px; line-height:1.5;">
                {"BMI kamu berada dalam kategori " + category.lower() + ". Pertahankan pola makan seimbang dan aktivitas fisik teratur." if bmi else "Isi berat dan tinggi badan untuk melihat BMI kamu."}
            </p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown(f"""
        <div class="glass-card-flat">
            <p style="font-weight:700; font-size:15px; color:{TEXT}; margin:0 0 14px 0; display:flex; align-items:center; gap:8px;">
                {icon('auto_awesome', 18)} Ringkasan
            </p>
            <div style="display:flex; flex-direction:column; gap:10px;">
                <div style="display:flex; align-items:center; gap:8px; font-size:13px; color:{SUBTEXT};">
                    {icon('check_circle', 16)} Aktivitas: {aktivitas if existing else '-'}
                </div>
                <div style="display:flex; align-items:center; gap:8px; font-size:13px; color:{SUBTEXT};">
                    {icon('check_circle', 16)} Status Profil: {'Lengkap' if profile_is_complete(st.session_state.profile) else 'Belum Lengkap'}
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)


# =========================================================
# KONSULTASI
# =========================================================
elif st.session_state.page == "Konsultasi":

    st.markdown(f"""
    <p class="section-title">{icon('chat_bubble', 28)} Konsultasi Kesehatan</p>
    <p class="section-sub">Tanyakan keluhan atau pertanyaan seputar kesehatan kamu ke AI.</p>
    """, unsafe_allow_html=True)

    if not profile_is_complete(st.session_state.profile):
        st.warning("Profil kamu belum lengkap. Silakan isi profil terlebih dahulu sebelum memulai konsultasi.")
        if st.button("Isi Profil Sekarang", icon=":material/person:", type="primary"):
            go("Profil")
        st.stop()

    # Tampilkan riwayat chat
    if not st.session_state.chat:
        st.markdown(f"""
        <div class="chat-empty">
            {icon('forum', 40)}
            Belum ada percakapan<br>
            Mulai dengan mengetik keluhan kamu di bawah
        </div>
        """, unsafe_allow_html=True)
    else:
        for entry in st.session_state.chat:
            role, text = entry[0], entry[1]
            safe_text = html.escape(text).replace("\n", "<br>")

            if role == "user":
                st.markdown(f"""
                <div class="chat-row user">
                    <div class="bubble-user">{safe_text}</div>
                    <div class="chat-avatar">{icon('person', 18)}</div>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="chat-row ai">
                    <div class="chat-avatar">{icon('smart_toy', 18)}</div>
                    <div class="bubble-ai">{safe_text}</div>
                </div>
                """, unsafe_allow_html=True)
                audio_path = entry[2] if len(entry) > 2 else None
                if audio_path and os.path.exists(audio_path):
                    st.audio(audio_path, format="audio/wav")
                    
                    rag_sources = entry[3] if len(entry) > 3 else []

                    if rag_sources:

                        st.caption("📚 Referensi RAG")

                        for source in sorted(set(rag_sources)):
                            st.markdown(f"- {source}")

    st.write("")

    # Pakai st.form supaya input otomatis kosong setelah submit
    # (clear_on_submit=True) -> menghindari konflik widget key
    # yang sebelumnya bikin error saat reset manual.
    with st.form("chat_form", clear_on_submit=True):
        col1, col2 = st.columns([6, 1])

        with col1:
            user_input = st.text_input(
                "Keluhan atau pertanyaan kamu",
                key="input_box",
                placeholder="Ketik keluhan atau pertanyaan kamu...",
                label_visibility="collapsed"
            )

        with col2:
            send = st.form_submit_button("Kirim", icon=":material/send:", use_container_width=True)

    # SEND LOGIC
    if send:

        clean_input = user_input.strip()

        if not clean_input:
            st.toast("Input tidak boleh kosong!", icon=":material/warning:")
        else:
            try:
                safe_input = html.escape(clean_input).replace("\n", "<br>")

                # Tampilkan bubble user langsung
                st.markdown(f"""
                <div class="chat-row user">
                    <div class="bubble-user">{safe_input}</div>
                    <div class="chat-avatar">{icon('person', 18)}</div>
                </div>
                """, unsafe_allow_html=True)

                # Ambil sumber RAG dulu (cepat, tidak perlu nunggu LLM)
                sources = get_last_sources(clean_input)

                # Tampilkan jawaban AI secara streaming (kata per kata).
                # Catatan: st.write_stream menampilkan teks dengan gaya
                # default Streamlit (bukan bubble custom .bubble-ai), karena
                # st.markdown tidak bisa membungkus elemen lain secara
                # DOM yang reliable. Bubble custom akan muncul kembali
                # setelah rerun (lihat riwayat chat di atas).
                with st.spinner("AI sedang menganalisis..."):

                    placeholder = st.empty()

                    full_response = ""

                    for chunk in generate_health_advice_stream(
                        clean_input,
                        st.session_state.chat_history,
                        st.session_state.profile
                    ):

                        full_response += chunk

                        placeholder.markdown(
                            f"""
                <div class="chat-row ai">
                    <div class="chat-avatar">{icon('smart_toy',18)}</div>
                    <div class="bubble-ai">
                        {full_response.replace(chr(10), "<br>")}
                    </div>
                </div>
                """,
                            unsafe_allow_html=True
                        )
                #
                # Setelah streaming selesai, baru buat audio dari teks lengkap
                with st.spinner("Membuat audio..."):
                    audio_file = text_to_audio(full_response)

                # Simpan ke chat history untuk ditampilkan ulang nanti
                st.session_state.chat.append(("user", clean_input))
                st.session_state.chat.append((
                    "ai",
                    full_response,
                    audio_file,
                    sources
                ))

                st.rerun()

            except Exception as e:
                st.toast("Gagal memproses permintaan", icon=":material/error:")
                st.error(f"ERROR: {e}")

    if st.session_state.chat:
        if st.button("Reset Percakapan", icon=":material/refresh:"):
            st.session_state.chat = []
            st.session_state.chat_history.clear()
            st.rerun()


# =========================================================
# INSIGHT
# =========================================================
elif st.session_state.page == "Insight":

    st.markdown(f"""
    <p class="section-title">{icon('monitoring', 28)} Insight Kesehatan</p>
    <p class="section-sub">Ringkasan progres dan riwayat konsultasi kamu.</p>
    """, unsafe_allow_html=True)

    total_consult = len([1 for e in st.session_state.chat if e[0] == "user"])
    # Skor sederhana berdasarkan kelengkapan profil + jumlah sesi konsultasi
    # (representasi kasar, bukan skor medis - murni indikator keterlibatan).
    profile_complete = profile_is_complete(st.session_state.profile)
    health_score = min(100, (40 if profile_complete else 0) + min(total_consult * 10, 60))

    col_score, col_priority = st.columns([1, 1.3], gap="large")

    with col_score:
        st.markdown(f"""
        <div class="glass-card-flat" style="text-align:center; height:100%;">
            <p style="font-size:12px; font-weight:800; letter-spacing:0.08em; text-transform:uppercase; color:{SUBTEXT}; opacity:0.7;">Skor Keterlibatan</p>
            <div style="
                width:170px; height:170px; margin:18px auto;
                border-radius:50%;
                background: conic-gradient({PRIMARY} {health_score * 3.6}deg, rgba(7,100,78,0.12) 0deg);
                display:flex; align-items:center; justify-content:center;
            ">
                <div style="
                    width:135px; height:135px; border-radius:50%;
                    background: {BG_FROM};
                    display:flex; flex-direction:column; align-items:center; justify-content:center;
                ">
                    <span style="font-size:34px; font-weight:800; color:{PRIMARY};">{health_score}%</span>
                </div>
            </div>
            <p style="font-size:13px; color:{SUBTEXT};">
                {'Profil lengkap & aktif berkonsultasi.' if health_score >= 70 else 'Lengkapi profil dan mulai konsultasi untuk skor lebih tinggi.'}
            </p>
        </div>
        """, unsafe_allow_html=True)

    with col_priority:
        st.markdown(f"""
        <div class="glass-card-flat" style="height:100%;">
            <p style="font-weight:700; font-size:16px; color:{TEXT}; margin:0 0 16px 0; display:flex; align-items:center; gap:8px;">
                {icon('auto_awesome', 18)} Prioritas Hari Ini
            </p>
        """, unsafe_allow_html=True)

        priorities = [
            ("bedtime", "Tidur lebih teratur", "Target: 7-8 jam per malam"),
            ("water_drop", "Perbanyak minum air", "Target: 2 liter per hari"),
            ("directions_walk", "Aktivitas fisik 30 menit", "Berjalan santai atau peregangan"),
        ]

        for icon_name, title, sub in priorities:
            st.markdown(f"""
            <div style="display:flex; align-items:center; gap:14px; padding:12px 0; border-bottom:1px solid rgba(190,201,195,0.25);">
                <div style="width:38px; height:38px; border-radius:12px; background:rgba(7,100,78,0.10); display:flex; align-items:center; justify-content:center; color:{PRIMARY}; flex-shrink:0;">
                    {icon(icon_name, 20)}
                </div>
                <div>
                    <p style="font-weight:600; font-size:14px; color:{TEXT}; margin:0;">{title}</p>
                    <p style="font-size:12px; color:{SUBTEXT}; opacity:0.8; margin:0;">{sub}</p>
                </div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)

    st.write("")
    st.write("")

    st.markdown(f"""
    <p style="font-weight:700; font-size:17px; color:{TEXT}; margin:0 0 14px 0; display:flex; align-items:center; gap:8px;">
        {icon('history', 20)} Riwayat Konsultasi
    </p>
    """, unsafe_allow_html=True)

    if not st.session_state.chat:
        st.markdown(f"""
        <div class="chat-empty">
            {icon('inbox', 36)}
            Belum ada riwayat konsultasi.
        </div>
        """, unsafe_allow_html=True)
    else:
        user_messages = [e[1] for e in st.session_state.chat if e[0] == "user"]
        for i, msg in enumerate(reversed(user_messages[-6:]), start=1):
            preview = msg if len(msg) <= 100 else msg[:100] + "..."
            st.markdown(f"""
            <div class="glass-card-flat" style="margin-bottom:10px; padding:16px 20px; display:flex; align-items:center; gap:14px;">
                <div class="chat-avatar" style="background:{PRIMARY};">{icon('person', 16)}</div>
                <p style="margin:0; font-size:14px; color:{TEXT};">{html.escape(preview)}</p>
            </div>
            """, unsafe_allow_html=True)


# =========================================================
# FOOTER
# =========================================================
st.markdown(f"""
<div class="app-footer">
    <div class="footer-title">AI Healthy Assistant</div>
    <div class="footer-sub">Membantu kamu menjaga pola hidup sehat dengan bantuan AI</div>
    <div class="footer-disclaimer">Aplikasi ini hanya memberikan edukasi dan tidak menggantikan tenaga medis profesional.</div>
</div>
""", unsafe_allow_html=True)
