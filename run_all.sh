#!/bin/bash
set -e

# Activate conda env (pre-installed in AMI)
source /opt/miniconda3/bin/activate shorts

cd /opt/autonomous-kids-shorts

echo "🚀 Starting Pipeline..."

# 1. Generate autonomous creative brief
echo "📝 Generating Brief..."
python3 generate_brief.py

# 2. Generate visuals
echo "🎨 Generating Images & Animation..."
python3 generate_images.py

# 3. Generate audio
echo "🎙️ Generating Voice & SFX..."
python3 generate_voice.py

# 4. Edit video
echo "✂️ Editing Shorts..."
python3 edit_video.py

# 5. Upload
echo "📤 Uploading to YouTube..."
TITLE=$(python3 -c "import json; print(json.load(open('/tmp/brief.json'))['title'])")
python3 upload_youtube.py --title "$TITLE | Kids Short 🌟"

# 6. Backup & Shutdown
echo "💾 Backing up & Shutting down..."
aws s3 cp /tmp/final_shorts.mp4 s3://your-shorts-bucket/$(date -Iseconds).mp4
sudo shutdown -h now
