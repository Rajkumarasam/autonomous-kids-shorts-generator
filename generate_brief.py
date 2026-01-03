import json, re, os
from llama_cpp import Llama

# Load offline LLM
llm = Llama(
    model_path="/opt/models/phi-3.5-mini-instruct.Q5_K_M.gguf",
    n_gpu_layers=40,
    n_ctx=4096,
    verbose=False
)

prompt = """<|system|>You are a creative director for kids' YouTube Shorts (ages 3-8). Invent a NEW original 45-second story.
Output ONLY valid JSON with:
{
  "title": "Catchy title <50 chars",
  "shots": [
    {
      "prompt": "SDXL prompt: cute animal + watercolor forest + action, 9:16, bright warm colors",
      "voice_line": "5-8 word line",
      "sfx": "butterfly"
    }
  ]
}
Rules: no humans, no text in scene, joyful, safe, watercolor picture book style.</s>
<|user|>Create today's story.</s>
<|assistant|>"""

output = llm(prompt, max_tokens=800, temperature=0.85)
text = output["choices"][0]["text"]

# Robust JSON extraction
try:
    # Attempt to find JSON blob
    json_str = re.search(r'\{.*\}', text, re.DOTALL).group()
    brief = json.loads(json_str)
except Exception as e:
    print(f"LLM JSON failed: {e}. Using fallback.")
    brief = {
        "title": "Little Fox's Sunny Adventure",
        "shots": [
            {"prompt": "adorable little fox with orange fur, white chest, blue scarf, in sunny watercolor forest with butterflies, rounded trees, mushrooms, 9:16 vertical", "voice_line": "One sunny morning, little fox explored!", "sfx": "butterfly"},
            {"prompt": "same little fox jumping joyfully on forest path, scarf flying, butterflies swirling, watercolor style", "voice_line": "Wheee! So many wonders to see!", "sfx": "paws"},
            {"prompt": "same little fox curled up in cozy tree root den at sunset, eyes closing, scarf wrapped, fireflies glowing", "voice_line": "Time to sleep, sweet dreams ahead.", "sfx": "cricket"}
        ]
    }

with open("/tmp/brief.json", "w") as f:
    json.dump(brief, f, indent=2)
print("✅ Brief generated.")
