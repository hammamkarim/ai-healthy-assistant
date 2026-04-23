from groq import Groq
import os
from dotenv import load_dotenv
from gtts import gTTS
import time
print()

# Load .env
load_dotenv()

api_key = os.getenv("GROQ_API_KEY")

# Debug
print("API KEY loaded:", "YES" if api_key else "NO")

if not api_key:
    raise ValueError("API KEY tidak ditemukan!")

# Setup client
client = Groq(api_key=api_key)


def generate_health_advice(user_input):
    prompt = f"""
    Berikan saran kesehatan berdasarkan kondisi pengguna berikut.

    Fokuskan saran pada perbaikan pola hidup sehat pengguna dan sesuaikan dengan kondisi yang dialami.

    Tuliskan jawaban dalam bentuk yang natural dan mengalir, seperti berbicara langsung kepada pengguna.

    Struktur jawaban:
    - Awali dengan kalimat yang menunjukkan kamu memahami kondisi pengguna
    - Jelaskan secara singkat penyebab atau dampaknya
    - Berikan saran menggunakan penomoran (1, 2, 3, dst)
    - Akhiri dengan penutup berupa anjuran umum, termasuk saran untuk berkonsultasi ke tenaga medis jika kondisi berlanjut

    PENTING:
    - Jangan gunakan tanda bintang (*), bullet (-), atau format markdown
    - Gunakan angka (1, 2, 3, dst)
    - Gunakan kata ganti "kamu"
    - Gunakan bahasa sederhana dan mudah dipahami
    - Hindari memberikan diagnosis penyakit
    - Hindari menyebutkan obat atau tindakan medis spesifik

    Input:
    {user_input}
    """

    try:
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {
                    "role": "system",
                    "content": "Kamu adalah asisten kesehatan yang memberikan saran sederhana, aman, dan tidak mendiagnosis penyakit."
                },
                {"role": "user", "content": prompt}
            ],
            max_tokens=500,
            temperature=0.8
        )

        return response.choices[0].message.content.strip()

    except Exception as e:
        print("\nERROR API:")
        print(e)
        return "Maaf, terjadi kesalahan saat memproses permintaan."


# Clean text (agar suara lebih natural)
def clean_text_for_audio(text):
    return text.replace("\n", " ").strip()


# Convert text ke audio
def text_to_audio(text):
    try:
        clean_text = clean_text_for_audio(text)

        filename = f"output_{int(time.time())}.mp3"
        tts = gTTS(text=clean_text, lang='id')
        tts.save(filename)

        return filename

    except Exception as e:
        print("Gagal membuat audio:", e)
        return None


# TEST
if __name__ == "__main__":
    print("=== AI Healthy Assistant (Groq + Audio) ===\n")

    user_input = input("Masukkan keluhan atau kondisi kesehatan kamu: ")

    if not user_input.strip():
        print("Input tidak boleh kosong!")
    else:
        hasil = generate_health_advice(user_input)

        print("\n=== HASIL AI ===\n")
        print(hasil)

        # Convert ke audio
        audio_file = text_to_audio(hasil)

        if audio_file:
            print(f"\n🔊 Audio berhasil dibuat: {audio_file}")

            # Auto play (Windows)
            os.system(f"start {audio_file}")
        else:
            print("Audio gagal dibuat")