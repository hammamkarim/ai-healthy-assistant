# 🩺 AI Healthy Assistant

![Python](https://img.shields.io/badge/Python-3.11+-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-Web_App-red)
![Transformers](https://img.shields.io/badge/HuggingFace-Transformers-yellow)
![FAISS](https://img.shields.io/badge/FAISS-Vector_Search-green)
![Piper](https://img.shields.io/badge/Piper-TTS-purple)
![License](https://img.shields.io/badge/License-Educational-lightgrey)

AI Healthy Assistant adalah aplikasi berbasis web yang memanfaatkan teknologi **Generative AI** untuk memberikan rekomendasi pola hidup sehat secara personal berdasarkan profil pengguna, riwayat percakapan, dan informasi kesehatan yang diperoleh melalui **Retrieval Augmented Generation (RAG)**.

Sistem menghasilkan rekomendasi dalam bentuk **teks** maupun **audio**, sehingga informasi kesehatan menjadi lebih mudah dipahami oleh pengguna.

---

# 🚀 Fitur Utama

- 💬 Konsultasi kesehatan berbasis Generative AI
- 🧠 Rekomendasi pola hidup sehat yang dipersonalisasi
- 👤 Healthy Profile (profil pengguna)
- 📚 Retrieval Augmented Generation (RAG)
- 🔎 Semantic Search menggunakan FAISS
- 🧩 Embedding Model untuk pencarian konteks
- 💭 Conversation Memory (AI mengingat percakapan sebelumnya)
- ⚡ Streaming Response (jawaban muncul secara real-time)
- 🔊 Text-to-Speech menggunakan Piper
- 🌐 Antarmuka web interaktif menggunakan Streamlit

---

# 🏗️ Arsitektur Sistem

Sistem terdiri dari beberapa komponen utama:

- Local Large Language Model (Qwen2.5-3B-Instruct)
- Sentence Transformer Embedding Model
- FAISS Vector Database
- Retrieval Augmented Generation (RAG)
- Conversation Memory
- Healthy User Profile
- Piper Text-to-Speech
- Streamlit Web Interface

---

# 🤖 Model yang Digunakan

## Large Language Model (LLM)

- Qwen/Qwen2.5-3B-Instruct

## Embedding Model

- sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2

## Text-to-Speech

- Piper TTS
- id_ID-news_tts-medium

---

# 📂 Struktur Project

```
AI-Healthy-Assistant
│
├── app.py
├── main.py
├── requirements.txt
│
├── dataset/
│   └── health_dataset.json
│
├── assets/
│
├── models/
│   └── piper/
│
├── outputs/
│   └── audio/
│
└── README.md
```

---

# 💻 Menjalankan Secara Lokal

## 1. Clone Repository

```bash
git clone https://github.com/hammamkarim/ai-healthy-assistant.git

cd ai-healthy-assistant
```

---

## 2. Install Dependencies

```bash
pip install -r requirements.txt
```

---

## 3. Jalankan Aplikasi

```bash
streamlit run app.py
```

Aplikasi akan berjalan pada:

```
http://localhost:8501
```

---

# ⚙️ Teknologi yang Digunakan

- Python
- Streamlit
- Hugging Face Transformers
- PyTorch
- Qwen2.5-3B-Instruct
- Sentence Transformers
- FAISS
- Piper TTS
- NumPy

---

# 📋 Cara Kerja Sistem

1. Pengguna mengisi Healthy Profile.
2. Pengguna mengirimkan pertanyaan atau keluhan kesehatan.
3. Sistem melakukan preprocessing input.
4. Embedding pertanyaan dibuat menggunakan Sentence Transformer.
5. FAISS melakukan semantic similarity search.
6. Dokumen yang paling relevan diambil melalui mekanisme RAG.
7. Profil pengguna, riwayat percakapan, dan hasil RAG digabungkan menjadi prompt.
8. Qwen2.5-3B-Instruct menghasilkan rekomendasi kesehatan.
9. Jawaban ditampilkan secara streaming.
10. Jawaban dikonversi menjadi audio menggunakan Piper TTS.
11. Riwayat percakapan disimpan sebagai Conversation Memory.

---

# ✨ Fitur AI

- Local Open Source LLM
- Retrieval Augmented Generation (RAG)
- Semantic Search
- Embedding Model
- Personalized Recommendation
- Conversation Memory
- Streaming Response
- Text-to-Speech

---

# 📌 Disclaimer

AI Healthy Assistant hanya digunakan sebagai media edukasi mengenai pola hidup sehat.

Aplikasi ini **tidak menggantikan tenaga medis profesional**, tidak memberikan diagnosis penyakit, dan tidak digunakan sebagai dasar pengambilan keputusan medis. Apabila keluhan berlanjut atau memburuk, pengguna disarankan untuk berkonsultasi dengan tenaga kesehatan.
