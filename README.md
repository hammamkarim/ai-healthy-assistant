# 🩺 AI Healthy Assistant

AI Healthy Assistant adalah aplikasi berbasis web yang memberikan rekomendasi pola hidup sehat secara personal menggunakan teknologi Generative AI dengan output teks dan audio.

---

## 🚀 Fitur Utama

- 💬 Konsultasi kesehatan berbasis AI  
- 🧠 Rekomendasi pola hidup sehat secara personal  
- 🔊 Output dalam bentuk audio (Text-to-Speech)  
- 🌐 Tampilan web interaktif menggunakan Streamlit  

---

## 🌍 Akses Aplikasi

### ✅ Online (Deploy)
Aplikasi dapat diakses melalui:  
https://ai-healthy-assistant.streamlit.app/

---

### 💻 Menjalankan Secara Lokal

#### 1. Clone Repository
```bash
git clone https://github.com/username/ai-healthy-assistant.git
cd ai-healthy-assistant
```

#### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

#### 3. Setup API Key
```bash
GROQ_API_KEY = "API_KEY_KAMU"
```
Catatan:
- File .env.example hanya sebagai contoh
- Gunakan .env untuk menyimpan API key asli

#### 4. Jalankan Aplikasi
```bash
streamlit run app.py
```
---

## 🧠 Teknologi yang Digunakan
- Streamlit (Frontend)
- Groq - LLaMA (LLM / Text-to-Text)
- gTTS (Text-to-Speech)
---

## ⚠️ Disclaimer
Aplikasi ini hanya bertujuan untuk edukasi dan tidak menggantikan tenaga medis profesional.
