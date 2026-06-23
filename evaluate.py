import pandas as pd
import time

from main import (
    generate_health_advice,
    calculate_similarity,
    text_to_audio
)

test_questions = [
    "Apa manfaat tidur cukup?",
    "Berapa kebutuhan air putih harian?",
    "Apa dampak kurang tidur?",
    "Bagaimana cara menjaga hidrasi tubuh?",
    "Apakah minum kopi berlebihan berbahaya?",
    "Siapa presiden pertama indonesia?",
    #"Bagaimana pola hidup sehat untuk mahasiswa?",
    #"Apa manfaat olahraga rutin?",
    #"Bagaimana cara mengurangi konsumsi kafein?",
    #"Apa dampak dehidrasi?",
    #"Bagaimana menjaga kualitas tidur?"
]

results = []

test_profile = {

    "gender": "Laki-laki",
    "age": "21",
    "weight": "71",
    "height": "165",
    "activity": "sedang",
    "goal": "Menjaga kesehatan dan meningkatkan kebugaran"

}

for question in test_questions:

    history = []

    # -------------------------
    # Evaluasi LLM
    # -------------------------

    start_time = time.time()

    answer, sources = generate_health_advice(
        question,
        history,
        test_profile
    )

    latency = round(
        time.time() - start_time,
        2
    )

    # -------------------------
    # Similarity
    # -------------------------

    similarity = calculate_similarity(
        question,
        answer
    )

    # -------------------------
    # Evaluasi Audio
    # -------------------------

    audio_start = time.time()

    audio_file = text_to_audio(
        answer
    )

    audio_time = round(
        time.time() - audio_start,
        2
    )

    # -------------------------
    # Simpan hasil
    # -------------------------

    results.append({

        "Question": question,
        
        "User Profile": (
            f"{test_profile['gender']}, "
            f"{test_profile['age']} tahun, "
            f"{test_profile['weight']} kg, "
            f"{test_profile['height']} cm, "
            f"{test_profile['activity']}, "
            f"Tujuan: {test_profile['goal']}"
        ),

        "Generated Answer": answer,
        
        "Audio File": audio_file,

        "RAG Source": ", ".join(
            set(sources)
        ),

        "Similarity": similarity,

        "Latency (s)": latency,

        "Relevance (1-5)": "",

        "Coherence (1-5)": "",

        "Fluency (1-5)": "",
        
        "Diversity (1-5)": "",

        "Hallucination Analysis": "",

        "Naturalness Audio (1-5)": "",

        "Intelligibility Audio (1-5)": "",

        "Audio Generation Time (s)": audio_time,

        "Error Analysis": ""

    })

# -------------------------
# Export CSV
# -------------------------

df = pd.DataFrame(
    results
)

df.to_csv(
    "outputs/evaluation.csv",
    index=False,
    encoding="utf-8-sig"
)

print(
    "\nEvaluasi berhasil disimpan ke outputs/evaluation.csv"
)