import torch, json, os
from diffusers import StableDiffusionXLPipeline, AnimateDiffPipeline, MotionAdapter
from diffusers.utils import export_to_video
from ip_adapter import IPAdapterPlusXL

os.makedirs("/tmp/shots", exist_ok=True)

with open("/tmp/brief.json") as f:
    brief = json.load(f)

# === Step 1: Reference Image (SDXL) ===
print("🦊 Generating Reference Image...")
pipe = StableDiffusionXLPipeline.from_single_file(
    "/opt/models/sd_xl_base_1.0.safetensors",
    torch_dtype=torch.float16
).to("cuda")

ref_prompt = brief["shots"][0]["prompt"] + " sharp focus, solo character, centered"
ref_image = pipe(ref_prompt, num_inference_steps=30).images[0]
ref_image.save("/tmp/ref.png")
del pipe
torch.cuda.empty_cache()

# === Step 2: Animation (AnimateDiff + IP-Adapter) ===
print("🎬 Generating Animation...")
pipe = StableDiffusionXLPipeline.from_single_file(
    "/opt/models/sd_xl_base_1.0.safetensors",
    torch_dtype=torch.float16
).to("cuda")

motion_adapter = MotionAdapter.from_single_file("/opt/models/animatediff_lightning_2step_sdxl.safetensors")
anim_pipe = AnimateDiffPipeline(**pipe.components, motion_adapter=motion_adapter)
anim_pipe.to("cuda")

# Load IP-Adapter to lock character consistency
ip_model = IPAdapterPlusXL(anim_pipe, "/opt/models/ip-adapter_sdxl.safetensors", device="cuda")

for i, shot in enumerate(brief["shots"]):
    print(f"Generating Shot {i+1}...")
    prompt = shot["prompt"] + " watercolor picture book style, bright warm colors, rounded shapes, for children"
    frames = ip_model.generate(
        pil_image="/tmp/ref.png",
        prompt=prompt,
        num_samples=1,
        num_inference_steps=2, # Fast lightning steps
        height=512,
        width=512,
        seed=42+i
    )
    export_to_video(frames[0], f"/tmp/shots/shot_{i+1:02d}.mp4", fps=24)

del pipe, anim_pipe, ip_model
torch.cuda.empty_cache()
print("✅ Visuals complete.")
