import subprocess

text = "Halo, saya adalah AI Healthy Assistant."

command = [
    "piper",
    "--model",
    "models/piper/id_ID-news_tts-medium.onnx",
    "--output_file",
    "hasil.wav"
]

process = subprocess.Popen(
    command,
    stdin=subprocess.PIPE,
    text=True
)

process.communicate(text)

print("Audio berhasil dibuat")