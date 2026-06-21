# ============================================
# FILE INI: main.py  (BUKAN app.py)
# ============================================
"""
AI Healthy Assistant - Core Engine
-----------------------------------
Modul ini berisi semua logika inti aplikasi:
- Load model LLM (Qwen2.5-3B-Instruct) lokal
- RAG (Retrieval Augmented Generation) dengan FAISS
- Embedding model untuk pencarian semantik
- Text-to-Speech (Piper)
- Conversation memory
- Streaming response (jawaban muncul kata per kata)

File ini bisa dijalankan langsung (CLI mode) atau diimport
oleh app.py (Streamlit UI).
"""

import os
import time
import json
import logging
import threading
from typing import Optional

import torch
import numpy as np
import faiss

from transformers import AutoTokenizer, AutoModelForCausalLM, TextIteratorStreamer
from sentence_transformers import SentenceTransformer, util
from piper.voice import PiperVoice
import wave


# =========================================================
# LOGGING
# =========================================================
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("ai_healthy_assistant")


# =========================================================
# KONSTANTA
# =========================================================
MODEL_NAME = "Qwen/Qwen2.5-3B-Instruct"
EMBEDDING_MODEL_NAME = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"

DATASET_PATH = "dataset/health_dataset.json"
VOICE_MODEL_PATH = "models/piper/id_ID-news_tts-medium.onnx"
AUDIO_OUTPUT_DIR = "outputs/audio"

MAX_HISTORY = 10          # jumlah pesan (user+assistant) yang disimpan di memory
RAG_TOP_K = 3              # jumlah dokumen relevan yang diambil dari FAISS
MAX_NEW_TOKENS = 300       # batas panjang jawaban AI
TEMPERATURE = 0.7
REPETITION_PENALTY = 1.2

TOPIK_DIPERBOLEHKAN = [
    "kesehatan",
    "pola hidup sehat",
    "nutrisi",
    "olahraga",
    "kebugaran",
    "tidur",
    "hidrasi",
    "kesehatan mental ringan",
]

PESAN_DI_LUAR_TOPIK = (
    "Maaf, saya hanya dapat membantu pertanyaan yang berkaitan "
    "dengan kesehatan dan pola hidup sehat."
)

SYSTEM_PROMPT = (
    "Kamu adalah asisten kesehatan yang memberikan saran sederhana, "
    "aman, dan tidak mendiagnosis penyakit."
)


# =========================================================
# DETEKSI DEVICE OTOMATIS
# Kalau device ini punya GPU NVIDIA yang kebaca PyTorch (CUDA),
# model akan dijalankan di GPU (jauh lebih cepat).
# Kalau tidak ada (device lain yang cuma CPU), otomatis
# fallback ke CPU tanpa perlu diubah manual.
# =========================================================
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

if DEVICE == "cuda":
    logger.info(f"GPU terdeteksi: {torch.cuda.get_device_name(0)}")
    logger.info("Model akan dijalankan di GPU (CUDA).")
else:
    logger.info("GPU tidak terdeteksi. Model akan dijalankan di CPU (lebih lambat).")


# =========================================================
# LOAD MODEL LLM
# =========================================================
logger.info(f"Loading {MODEL_NAME} ...")
logger.info("Saat pertama kali dijalankan, model akan diunduh. Proses ini mungkin memerlukan beberapa menit.")

tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)

model = AutoModelForCausalLM.from_pretrained(
    MODEL_NAME,
    torch_dtype=torch.float16 if DEVICE == "cuda" else torch.float32,
)
model = model.to(DEVICE)
model.eval()

logger.info("Model LLM berhasil dimuat!")


# =========================================================
# LOAD EMBEDDING MODEL
# =========================================================
logger.info("Memuat model embedding...")

embedding_model = SentenceTransformer(EMBEDDING_MODEL_NAME, device=DEVICE)

logger.info("Model embedding berhasil dimuat!")


# =========================================================
# LOAD DATASET + BANGUN FAISS INDEX
# =========================================================
def _load_dataset(path: str) -> list:
    """Load dataset kesehatan dari file JSON. Raise error yang jelas kalau file tidak ada/rusak."""
    if not os.path.exists(path):
        raise FileNotFoundError(
            f"Dataset tidak ditemukan di '{path}'. "
            "Pastikan file dataset/health_dataset.json ada di folder project."
        )

    with open(path, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError as e:
            raise ValueError(f"Dataset '{path}' bukan JSON yang valid: {e}")


dataset = _load_dataset(DATASET_PATH)
logger.info(f"Dataset berhasil dimuat: {len(dataset)} data")

documents = [
    f"""
Kategori: {item['category']}

Pertanyaan:
{item['question']}

Jawaban:
{item['answer']}
"""
    for item in dataset
]

logger.info("Membuat embedding dataset...")
document_embeddings = embedding_model.encode(documents, convert_to_numpy=True)
logger.info("Embedding selesai dibuat!")

_dimension = document_embeddings.shape[1]
index = faiss.IndexFlatL2(_dimension)
index.add(document_embeddings.astype("float32"))

logger.info(f"FAISS index siap dengan {index.ntotal} data")


# =========================================================
# LOAD VOICE MODEL (PIPER TTS)
# =========================================================
logger.info("Memuat model suara Piper...")

if not os.path.exists(VOICE_MODEL_PATH):
    logger.warning(
        f"File voice model tidak ditemukan di '{VOICE_MODEL_PATH}'. "
        "Fitur text-to-audio tidak akan berfungsi."
    )
    voice = None
else:
    voice = PiperVoice.load(VOICE_MODEL_PATH)
    logger.info("Model suara berhasil dimuat!")


# =========================================================
# STATE (dipakai CLI mode; app.py punya state sendiri lewat
# st.session_state, fungsi-fungsi di bawah tetap menerima
# history/profile sebagai parameter sehingga reusable)
# =========================================================
conversation_history = []
user_profile = {}


# =========================================================
# PROFIL PENGGUNA (CLI helper)
# =========================================================
def create_user_profile() -> dict:
    """Tanya data profil kesehatan pengguna lewat terminal (CLI mode)."""
    print("\n=== HEALTHY PROFILE ===")

    return {
        "gender": input("Jenis Kelamin (Laki-laki/Perempuan): "),
        "age": input("Umur: "),
        "weight": input("Berat Badan (kg): "),
        "height": input("Tinggi Badan (cm): "),
        "activity": input("Aktivitas Harian (rendah/sedang/tinggi): "),
        "goal": input("Tujuan Kesehatan: "),
    }


# =========================================================
# RAG: PENCARIAN KONTEKS
# =========================================================
def search_context(query: str, top_k: int = RAG_TOP_K):
    """
    Cari dokumen paling relevan di dataset menggunakan FAISS.
    Mengembalikan (context_gabungan: str, sources: list[str]).
    """
    top_k = min(top_k, index.ntotal)  # jaga-jaga kalau dataset lebih kecil dari top_k

    query_embedding = embedding_model.encode([query], convert_to_numpy=True)
    distances, indices = index.search(query_embedding.astype("float32"), top_k)

    contexts = [documents[idx] for idx in indices[0]]
    sources = [dataset[idx]["source"] for idx in indices[0]]

    return "\n\n".join(contexts), sources


def calculate_similarity(question: str, answer: str) -> float:
    """Hitung cosine similarity antara pertanyaan dan jawaban (untuk evaluasi kualitas RAG)."""
    emb1 = embedding_model.encode(question, convert_to_tensor=True)
    emb2 = embedding_model.encode(answer, convert_to_tensor=True)
    score = util.cos_sim(emb1, emb2)
    return round(score.item(), 4)


# =========================================================
# PROMPT BUILDER
# =========================================================
def _build_profile_context(profile: dict) -> str:
    return f"""
PROFIL PENGGUNA

Jenis Kelamin:
{profile['gender']}

Umur:
{profile['age']} tahun

Berat Badan:
{profile['weight']} kg

Tinggi Badan:
{profile['height']} cm

Aktivitas Harian:
{profile['activity']}

Tujuan Kesehatan:
{profile['goal']}
"""


def _build_prompt(user_input: str, profile: dict, context: str) -> str:
    profile_context = _build_profile_context(profile)
    topik_list = "\n".join(f"- {t}" for t in TOPIK_DIPERBOLEHKAN)

    return f"""
Gunakan informasi berikut sebagai referensi utama.

PROFIL PENGGUNA:

{profile_context}

INFORMASI DATASET:

{context}

Berikan saran kesehatan berdasarkan kondisi pengguna berikut.

Fokuskan saran pada perbaikan pola hidup sehat pengguna dan sesuaikan dengan kondisi yang dialami.

Gunakan bahasa Indonesia.

Kamu hanya boleh menjawab pertanyaan yang berkaitan dengan:
{topik_list}

Jika pertanyaan pengguna berada di luar topik tersebut, jawab HANYA dengan:

"{PESAN_DI_LUAR_TOPIK}"

Untuk pertanyaan kesehatan:

- Awali dengan kalimat yang menunjukkan kamu memahami kondisi pengguna.
- Jelaskan secara singkat penyebab atau dampaknya.
- Berikan saran menggunakan penomoran (1, 2, 3, 4, dst).
- Akhiri dengan anjuran umum dan saran berkonsultasi ke tenaga medis jika kondisi berlanjut.

PENTING:
- Gunakan bahasa Indonesia yang sederhana dan mudah dipahami.
- WAJIB menggunakan kata ganti "kamu" dan jangan menggunakan kata "Anda".
- Gunakan penomoran (1, 2, 3, 4, dst).
- Maksimal 4 poin saran.
- Setiap poin maksimal 1-2 kalimat.
- Jangan menggunakan markdown, bullet (-), atau tanda bintang (*).
- Jangan memberikan diagnosis penyakit.
- Jangan menyebutkan obat atau tindakan medis spesifik.
- Jika informasi pengguna kurang jelas, berikan saran umum yang aman.

Input Pengguna:
{user_input}

Jawaban:
"""


def _build_messages(prompt: str, history: list) -> list:
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    messages.extend(history)
    messages.append({"role": "user", "content": prompt})
    return messages


def _prepare_model_inputs(messages: list):
    text = tokenizer.apply_chat_template(
        messages,
        tokenize=False,
        add_generation_prompt=True,
    )
    inputs = tokenizer(text, return_tensors="pt")
    inputs = {key: value.to(DEVICE) for key, value in inputs.items()}
    return inputs


def _update_history(history: list, user_input: str, response: str):
    history.append({"role": "user", "content": user_input})
    history.append({"role": "assistant", "content": response})

    if len(history) > MAX_HISTORY:
        del history[:-MAX_HISTORY]


# =========================================================
# GENERATE HEALTH ADVICE (mode normal / non-streaming)
# =========================================================
def generate_health_advice(user_input: str, history: list, profile: dict):
    """
    Hasilkan saran kesehatan secara penuh (tunggu sampai selesai).
    Mengembalikan (response: str, sources: list[str]).
    Dipakai oleh app.py (Streamlit) dan CLI mode klasik.
    """
    context, sources = search_context(user_input)
    prompt = _build_prompt(user_input, profile, context)
    messages = _build_messages(prompt, history)

    try:
        inputs = _prepare_model_inputs(messages)

        with torch.inference_mode():
            outputs = model.generate(
                **inputs,
                max_new_tokens=MAX_NEW_TOKENS,
                temperature=TEMPERATURE,
                do_sample=True,
                repetition_penalty=REPETITION_PENALTY,
                pad_token_id=tokenizer.eos_token_id,
            )

        response = tokenizer.decode(
            outputs[0][inputs["input_ids"].shape[1]:],
            skip_special_tokens=True,
        )

        _update_history(history, user_input, response)

        return response, sources

    except Exception as e:
        logger.error(f"Gagal generate jawaban: {e}")
        return "Maaf, terjadi kesalahan saat memproses permintaan.", []


# =========================================================
# GENERATE HEALTH ADVICE (mode streaming)
# Jawaban di-yield kata per kata / potongan per potongan,
# bukan ditunggu sampai selesai semua.
#
# Cara pakai:
#   for chunk in generate_health_advice_stream(user_input, history, profile):
#       print(chunk, end="", flush=True)
#
# Catatan untuk integrasi ke Streamlit (app.py):
#   st.write_stream() bisa langsung menerima generator ini.
#   Sources & history-update terjadi SETELAH stream selesai,
#   diakses lewat nilai return generator (lihat StopIteration.value)
#   atau lebih simpel: panggil search_context() dulu di app.py
#   kalau sumbernya mau ditampilkan sebelum streaming selesai.
# =========================================================
def generate_health_advice_stream(user_input: str, history: list, profile: dict):
    """
    Versi streaming dari generate_health_advice().
    Yield potongan teks jawaban secara real-time.
    Setelah selesai, history otomatis ter-update dan
    generator mengembalikan (full_response, sources) lewat
    atribut `.sources` dan `.full_response` pada objek ini
    tidak tersedia langsung di generator biasa, sehingga
    sources dikembalikan di akhir lewat yield khusus jika
    diperlukan -- lihat contoh pemakaian di __main__ di bawah.
    """
    context, sources = search_context(user_input)
    prompt = _build_prompt(user_input, profile, context)
    messages = _build_messages(prompt, history)

    try:
        inputs = _prepare_model_inputs(messages)

        streamer = TextIteratorStreamer(
            tokenizer,
            skip_prompt=True,
            skip_special_tokens=True,
        )

        generation_kwargs = dict(
            **inputs,
            max_new_tokens=MAX_NEW_TOKENS,
            temperature=TEMPERATURE,
            do_sample=True,
            repetition_penalty=REPETITION_PENALTY,
            pad_token_id=tokenizer.eos_token_id,
            streamer=streamer,
        )

        # generate() bersifat blocking, jadi dijalankan di thread
        # terpisah supaya kita bisa membaca streamer secara realtime
        thread = threading.Thread(target=model.generate, kwargs=generation_kwargs)
        thread.start()

        full_response = ""
        for chunk in streamer:
            full_response += chunk
            yield chunk

        thread.join()

        _update_history(history, user_input, full_response)

    except Exception as e:
        logger.error(f"Gagal generate jawaban (streaming): {e}")
        yield "Maaf, terjadi kesalahan saat memproses permintaan."


def get_last_sources(user_input: str, top_k: int = RAG_TOP_K):
    """
    Helper terpisah untuk ambil sumber RAG saja, dipakai bersamaan
    dengan generate_health_advice_stream() di app.py kalau sumber
    ingin ditampilkan sebelum/selama streaming berlangsung.
    """
    _, sources = search_context(user_input, top_k=top_k)
    return sources


# =========================================================
# TEXT TO AUDIO
# =========================================================
def text_to_audio(text: str) -> Optional[str]:
    """Ubah teks jadi file audio .wav menggunakan Piper TTS. Return path file, atau None kalau gagal."""
    if voice is None:
        logger.warning("Voice model belum dimuat, audio tidak dibuat.")
        return None

    try:
        text = text.replace("\n", " ").strip()

        os.makedirs(AUDIO_OUTPUT_DIR, exist_ok=True)
        filename = os.path.join(AUDIO_OUTPUT_DIR, f"output_{int(time.time())}.wav")

        with wave.open(filename, "wb") as wav_file:
            voice.synthesize_wav(text, wav_file)

        return filename

    except Exception as e:
        logger.error(f"Gagal membuat audio: {e}")
        return None


# =========================================================
# CLI ENTRY POINT
# =========================================================
if __name__ == "__main__":

    print("\n=== AI Healthy Assistant ===")
    print("Kamu dapat bertanya beberapa kali secara berurutan.")
    print("AI akan mengingat percakapan sebelumnya.")
    print("Ketik 'reset' untuk memulai percakapan baru.")
    print("Ketik 'keluar' untuk menutup aplikasi.")

    user_profile = create_user_profile()

    print("\n=====================================")
    print("Profil berhasil disimpan.")
    print("=====================================")

    print("\n=== RINGKASAN PROFIL ===")
    print(f"Jenis Kelamin : {user_profile['gender']}")
    print(f"Umur          : {user_profile['age']} tahun")
    print(f"Berat Badan   : {user_profile['weight']} kg")
    print(f"Tinggi Badan  : {user_profile['height']} cm")
    print(f"Aktivitas     : {user_profile['activity']}")
    print(f"Tujuan        : {user_profile['goal']}")

    print("\n=====================================")
    print("=== KONSULTASI KESEHATAN ===")
    print("=====================================")

    while True:

        user_input = input("\nMasukkan keluhan atau kondisi kesehatan kamu: ")

        if user_input.lower() == "keluar":
            print("Sampai jumpa!")
            break

        if user_input.lower() == "reset":
            conversation_history.clear()
            print("Riwayat percakapan berhasil dihapus.")
            continue

        if not user_input.strip():
            print("Input tidak boleh kosong!")
            continue

        # Tampilkan sumber RAG dulu sebelum streaming jawaban
        sources = get_last_sources(user_input)

        print("\n=== REFERENSI DATASET (RAG) ===\n")
        for i, source in enumerate(set(sources), start=1):
            print(f"[{i}] {source}")

        print("\n=== HASIL AI (streaming) ===\n")

        full_response = ""
        for chunk in generate_health_advice_stream(user_input, conversation_history, user_profile):
            print(chunk, end="", flush=True)
            full_response += chunk
        print()  # newline setelah streaming selesai

        audio_file = text_to_audio(full_response)

        if audio_file:
            print(f"\n🔊 Audio berhasil dibuat: {audio_file}")
            os.system(f'start "" "{audio_file}"')  # Auto play (Windows)
        else:
            print("Audio gagal dibuat")