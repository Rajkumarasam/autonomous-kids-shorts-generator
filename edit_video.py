import subprocess, json, os

with open("/tmp/brief.json") as f:
    brief = json.load(f)

# List video shots
with open("/tmp/shot_list.txt", "w") as f:
    for i in range(len(brief["shots"])):
        f.write(f"file 'shots/shot_{i+1:02d}.mp4'\n")

print("✂️ Stitching Video...")
# 1. Concatenate video
subprocess.run([
    "ffmpeg", "-y", "-f", "concat", "-safe", "0",
    "-i", "/tmp/shot_list.txt",
    "-c", "copy", "/tmp/concat_video.mp4"
], check=True, stderr=subprocess.DEVNULL)

# 2. Final Edit (Resize to 9:16 + Zoom Effect + Audio)
print("✨ Rendering Final Output...")
cmd = [
    "ffmpeg", "-y",
    "-i", "/tmp/concat_video.mp4",
    "-i", "/tmp/final_audio.aac",
    "-vf", (
        "scale=1080:1920:force_original_aspect_ratio=decrease,"
        "pad=1080:1920:(ow-iw)/2:(oh-ih)/2,"
        "zoompan=z='if(lte(zoom,1.0),1.0,zoom-0.001)':x='(iw-iw*zoom)/2':y='(ih-ih*zoom)/2':d=125"
    ),
    "-c:v", "libx264", "-crf", "18", "-preset", "fast",
    "-c:a", "aac", "-b:a", "192k",
    "-shortest",
    "/tmp/final_shorts.mp4"
]
subprocess.run(cmd, check=True, stderr=subprocess.DEVNULL)
print("✅ Final Video Ready: /tmp/final_shorts.mp4")
