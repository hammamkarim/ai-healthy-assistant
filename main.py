import os
import time
print()

from transformers import AutoTokenizer
from transformers import AutoModelForCausalLM

from piper.voice import PiperVoice
import wave

MODEL_NAME = "Qwen/Qwen2.5-3B-Instruct"

print("Loading Qwen2.5-3B-Instruct...")
print("Saat pertama kali dijalankan, model akan diunduh. Proses ini mungkin memerlukan beberapa menit.")

tokenizer = AutoTokenizer.from_pretrained(
    MODEL_NAME
)

model = AutoModelForCausalLM.from_pretrained(
    MODEL_NAME
)

print("\nModel berhasil dimuat!")

print("Memuat model suara Piper...")
# print(os.path.exists("models/piper/id_ID-news_tts-medium.onnx"))
# print(os.path.exists("models/piper/id_ID-news_tts-medium.onnx.json"))


voice = PiperVoice.load(
    "models/piper/id_ID-news_tts-medium.onnx"
)

# print(type(voice))
# print(dir(voice))

print("Model suara berhasil dimuat!")

def generate_health_advice(user_input):

    prompt = f"""
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
            max_new_tokens=350,
            temperature=0.7,
            do_sample=True,
            repetition_penalty=1.2,
            pad_token_id=tokenizer.eos_token_id
        )

        response = tokenizer.decode(
            outputs[0][inputs["input_ids"].shape[1]:],
            skip_special_tokens=True
        )

        return response

    except Exception as e:

        print("\nERROR MODEL:")
        print(e)

        return "Maaf, terjadi kesalahan saat memproses permintaan."



def text_to_audio(text):

    try:

        text = text.replace("\n", " ").strip()

        filename = f"outputs/audio/output_{int(time.time())}.wav"

        with wave.open(filename, "wb") as wav_file:

            voice.synthesize_wav(
                text,
                wav_file
            )

        return filename

    except Exception as e:

        print("Gagal membuat audio:")
        print(e)

        return None




# TEST
if __name__ == "__main__":
    print("\n=== AI Healthy Assistant ===")

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
            os.system(f'start "" "{audio_file}"')

        else:
            print("Audio gagal dibuat")