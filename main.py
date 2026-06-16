import os
import time
print()

from transformers import AutoTokenizer
from transformers import AutoModelForCausalLM

import json
import numpy as np
import faiss

from sentence_transformers import SentenceTransformer
from sentence_transformers import util

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

print("\nModel LLM berhasil dimuat!")

print("Memuat model embedding...")

embedding_model = SentenceTransformer(
    "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
)

print("Model embedding berhasil dimuat!")

with open(
    "dataset/health_dataset.json",
    "r",
    encoding="utf-8"
) as f:

    dataset = json.load(f)

print(
    f"Dataset berhasil dimuat: {len(dataset)} data"
)

documents = []

for item in dataset:

    text = f"""
Kategori: {item['category']}

Pertanyaan:
{item['question']}

Jawaban:
{item['answer']}
"""

    documents.append(text)
    
print("Membuat embedding dataset...")

document_embeddings = embedding_model.encode(
    documents,
    convert_to_numpy=True
)

print("Embedding selesai dibuat!")

dimension = document_embeddings.shape[1]

index = faiss.IndexFlatL2(
    dimension
)

index.add(
    document_embeddings.astype("float32")
)

print(
    f"FAISS index siap dengan {index.ntotal} data"
)

conversation_history = []
MAX_HISTORY = 10

print("Memuat model suara Piper...")
# print(os.path.exists("models/piper/id_ID-news_tts-medium.onnx"))
# print(os.path.exists("models/piper/id_ID-news_tts-medium.onnx.json"))

voice = PiperVoice.load(
    "models/piper/id_ID-news_tts-medium.onnx"
)

# print(type(voice))
# print(dir(voice))

print("Model suara berhasil dimuat!")

def search_context(query, top_k=3):

    query_embedding = embedding_model.encode(
        [query],
        convert_to_numpy=True
    )

    distances, indices = index.search(
        query_embedding.astype("float32"),
        top_k
    )

    contexts = []
    sources = []

    for idx in indices[0]:

        contexts.append(
            documents[idx]
        )

        sources.append(
            dataset[idx]["source"]
        )

    return "\n\n".join(contexts), sources

def calculate_similarity(question, answer):

    emb1 = embedding_model.encode(
        question,
        convert_to_tensor=True
    )

    emb2 = embedding_model.encode(
        answer,
        convert_to_tensor=True
    )

    score = util.cos_sim(
        emb1,
        emb2
    )

    return round(
        score.item(),
        4
    )

def generate_health_advice(user_input, history):
    
    context, sources = search_context(
        user_input
    )

    prompt = f"""
    
Gunakan informasi berikut sebagai referensi utama.

INFORMASI DATASET:

{context}
    
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
                "content": """
        Kamu adalah asisten kesehatan yang memberikan saran sederhana, aman, dan tidak mendiagnosis penyakit.
        """
            }
        ]

        messages.extend(history)

        messages.append(
            {
                "role": "user",
                "content": prompt
            }
        )

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

        history.append(
            {
                "role": "user",
                "content": user_input
            }
        )

        history.append(
            {
                "role": "assistant",
                "content": response
            }
        )

        # Simpan hanya 5 percakapan terakhir
        if len(history) > MAX_HISTORY:
            del history[:-MAX_HISTORY]

        return response, sources

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
    print("Kamu dapat bertanya beberapa kali secara berurutan.")
    print("AI akan mengingat percakapan sebelumnya.")
    print("Ketik 'reset' untuk memulai percakapan baru.")
    print("Ketik 'keluar' untuk menutup aplikasi.")

    while True:

        user_input = input(
            "\nMasukkan keluhan atau kondisi kesehatan kamu: "
        )

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

        hasil, sources = generate_health_advice(
            user_input,
            conversation_history
        )

        print("\n=== REFERENSI DATASET (RAG) ===\n")

        for i, source in enumerate(set(sources), start=1):
            print(f"[{i}] {source}")

        print("\n=== HASIL AI ===\n")
        print(hasil)

        audio_file = text_to_audio(hasil)

        if audio_file:
            print(f"\n🔊 Audio berhasil dibuat: {audio_file}")

            # Auto play (Windows)
            os.system(f'start "" "{audio_file}"')

        else:
            print("Audio gagal dibuat")