import os
from gtts import gTTS
import time
print()

from transformers import AutoTokenizer
from transformers import AutoModelForCausalLM

MODEL_NAME = "Qwen/Qwen2.5-3B-Instruct"

print("Loading Qwen2.5-3B-Instruct...")
print("First run may take several minutes because the model will be downloaded.")

tokenizer = AutoTokenizer.from_pretrained(
    MODEL_NAME
)

model = AutoModelForCausalLM.from_pretrained(
    MODEL_NAME
)

print("Model loaded!")

def generate_health_advice(user_input):

    prompt = f"""
Kamu adalah asisten kesehatan yang memberikan saran sederhana, aman, dan tidak mendiagnosis penyakit.

Berikan saran kesehatan berdasarkan kondisi pengguna berikut.

Fokuskan saran pada perbaikan pola hidup sehat pengguna dan sesuaikan dengan kondisi yang dialami.

Gunakan bahasa Indonesia.

Kamu hanya boleh menjawab pertanyaan yang berkaitan dengan:
- kesehatan
- pola hidup sehat
- nutrisi
- olahraga
- kebugaran
- tidur
- hidrasi
- kesehatan mental ringan

Jika pertanyaan pengguna berada di luar topik tersebut, jawab HANYA dengan:

"Maaf, saya hanya dapat membantu pertanyaan yang berkaitan dengan kesehatan dan pola hidup sehat."

Untuk pertanyaan kesehatan:

- Awali dengan kalimat yang menunjukkan kamu memahami kondisi pengguna.
- Jelaskan secara singkat penyebab atau dampaknya.
- Berikan saran menggunakan penomoran (1, 2, 3, dst).
- Akhiri dengan anjuran umum dan saran berkonsultasi ke tenaga medis jika kondisi berlanjut.

PENTING:
- Jangan gunakan tanda bintang (*).
- Jangan gunakan bullet (-).
- Jangan gunakan markdown.
- Gunakan angka (1, 2, 3, dst).
- Gunakan kata ganti "kamu".
- Gunakan bahasa sederhana dan mudah dipahami.
- Hindari memberikan diagnosis penyakit.
- Hindari menyebutkan obat atau tindakan medis spesifik.
- Berikan maksimal 4 saran.
- Jangan memberikan lebih dari 4 poin.
- Setiap poin maksimal 1-2 kalimat.

Input Pengguna:
{user_input}

Jawaban:
"""

    try:

        messages = [
            {
                "role": "system",
                "content": """Kamu adalah asisten kesehatan yang memberikan saran sederhana, aman, dan tidak mendiagnosis penyakit."""
            },
            {
                "role": "user",
                "content": prompt
            }
        ]

        text = tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=True
        )

        inputs = tokenizer(
            text,
            return_tensors="pt"
        )

        outputs = model.generate(
            **inputs,
            max_new_tokens=250,
            temperature=0.7,
            do_sample=True,
            repetition_penalty=1.2,
            pad_token_id=tokenizer.eos_token_id
        )

        response = tokenizer.decode(
            outputs[0][inputs["input_ids"].shape[1]:],
            skip_special_tokens=True
        )

        print("\n=== DEBUG RAW OUTPUT ===\n")
        print(response)

        return response

    except Exception as e:

        print("\nERROR MODEL:")
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
    print("=== AI Healthy Assistant (Qwen Local + Audio) ===\n")

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