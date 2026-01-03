import subprocess, json, os

with open("/tmp/brief.json") as f:
    brief = json.load(f)

SFX_MAP = {
    "butterfly": "/opt/sfx/butterfly.wav",
    "paws": "/opt/sfx/paws.wav",
    "cricket": "/opt/sfx/cricket.wav",
    "sparkle": "/opt/sfx/sparkle.wav"
}

os.makedirs("/tmp/audio", exist_ok=True)

print("🎙️ Processing Audio...")
for i, shot in enumerate(brief["shots"]):
    # 1. Generate Voice
    voice_wav = f"/tmp/audio/voice_{i+1:02d}.wav"
    # Pipe text into Piper binary
    cmd = f'echo "{shot["voice_line"]}" | /opt/models/piper/piper --model /opt/models/piper/en_US-amy-medium.onnx --output {voice_wav}'
    subprocess.run(cmd, shell=True, check=True)
    
    # 2. Mix with SFX
    sfx_path = SFX_MAP.get(shot.get("sfx"), "/opt/sfx/sparkle.wav")
    if not os.path.exists(sfx_path): sfx_path = "/opt/sfx/sparkle.wav" # Fallback
    
    mixed_wav = f"/tmp/audio/mixed_{i+1:02d}.wav"
    subprocess.run([
        "ffmpeg", "-y", "-i", voice_wav, "-i", sfx_path,
        "-filter_complex", "amix=inputs=2:duration=first",
        "-c:a", "aac", mixed_wav
    ], check=True, stderr=subprocess.DEVNULL)

# Concatenate audio files
with open("/tmp/audio_list.txt", "w") as f:
    for i in range(len(brief["shots"])):
        f.write(f"file 'mixed_{i+1:02d}.wav'\n")

subprocess.run([
    "ffmpeg", "-y", "-f", "concat", "-safe", "0",
    "-i", "/tmp/audio_list.txt",
    "-c", "copy", "/tmp/final_audio.aac"
], check=True, stderr=subprocess.DEVNULL)
print("✅ Audio complete.")
