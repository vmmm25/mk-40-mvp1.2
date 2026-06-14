---
name: image-generation
version: 1.0.0
description: Generate, edit, and transform images using AI models including FLUX (via Replicate/fal.ai), DALL-E 3 (OpenAI), and Stable Diffusion (local). Supports img2img, inpainting, upscaling, and batch generation.
tags: [image-generation, flux, dalle, stable-diffusion, ai-art, replicate, fal, midjourney, editing]
author: garri333
license: MIT
source: https://clawdbotskills.org/
---

# Image Generation Skill

## Setup

```bash
pip install openai replicate pillow requests python-dotenv
# For local Stable Diffusion:
pip install diffusers transformers torch accelerate
```

`.env`:
```
OPENAI_API_KEY=sk-...
REPLICATE_API_TOKEN=r8_...
FAL_KEY=...
```

## DALL-E 3 (OpenAI) — Easiest, Highest Quality

```python
import openai
import os
import requests
from PIL import Image
from io import BytesIO
from dotenv import load_dotenv

load_dotenv()
client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def generate_dalle3(
    prompt: str,
    size: str = "1024x1024",   # "1024x1024" | "1792x1024" | "1024x1792"
    quality: str = "hd",       # "standard" | "hd"
    style: str = "vivid",      # "vivid" | "natural"
    n: int = 1,
    save_path: str = None
) -> dict:
    """Generate an image with DALL-E 3."""
    response = client.images.generate(
        model="dall-e-3",
        prompt=prompt,
        size=size,
        quality=quality,
        style=style,
        n=n
    )
    
    results = []
    for i, img_data in enumerate(response.data):
        url = img_data.url
        revised_prompt = img_data.revised_prompt
        
        if save_path:
            img_bytes = requests.get(url).content
            path = save_path if n == 1 else save_path.replace(".", f"_{i}.")
            with open(path, "wb") as f:
                f.write(img_bytes)
        
        results.append({"url": url, "revised_prompt": revised_prompt})
    
    return results[0] if n == 1 else results

def edit_image_dalle(
    image_path: str,
    mask_path: str,
    prompt: str,
    size: str = "1024x1024"
) -> dict:
    """Edit an image using DALL-E inpainting (transparent mask area gets replaced)."""
    with open(image_path, "rb") as img, open(mask_path, "rb") as mask:
        response = client.images.edit(
            model="dall-e-2",  # DALL-E 2 for edits
            image=img,
            mask=mask,
            prompt=prompt,
            size=size,
            n=1
        )
    return {"url": response.data[0].url}

def create_variation(image_path: str, n: int = 2) -> list[str]:
    """Create variations of an existing image."""
    with open(image_path, "rb") as img:
        response = client.images.create_variation(model="dall-e-2", image=img, n=n, size="1024x1024")
    return [d.url for d in response.data]
```

## FLUX (via Replicate) — Best Open-Source Quality

```python
import replicate

def generate_flux(
    prompt: str,
    model: str = "black-forest-labs/flux-schnell",  # or "flux-dev", "flux-pro"
    width: int = 1024,
    height: int = 1024,
    num_outputs: int = 1,
    num_inference_steps: int = 4,   # 4 for schnell, 28 for dev/pro
    guidance_scale: float = 3.5,
    save_path: str = None
) -> list[str]:
    """Generate image(s) using FLUX on Replicate."""
    output = replicate.run(
        model,
        input={
            "prompt": prompt,
            "width": width,
            "height": height,
            "num_outputs": num_outputs,
            "num_inference_steps": num_inference_steps,
            "guidance_scale": guidance_scale,
        }
    )
    
    urls = list(output)
    if save_path:
        for i, url in enumerate(urls):
            img_bytes = requests.get(url).content
            path = save_path if num_outputs == 1 else save_path.replace(".", f"_{i}.")
            with open(path, "wb") as f:
                f.write(img_bytes)
    
    return urls

def flux_img2img(
    prompt: str,
    image_path: str,
    prompt_strength: float = 0.8,  # 0=keep original, 1=full generation
    save_path: str = None
) -> str:
    """Transform an existing image with FLUX."""
    with open(image_path, "rb") as f:
        image_data = f.read()
    
    output = replicate.run(
        "black-forest-labs/flux-dev",
        input={
            "prompt": prompt,
            "image": image_data,
            "prompt_strength": prompt_strength,
            "num_inference_steps": 28,
        }
    )
    
    url = list(output)[0]
    if save_path:
        with open(save_path, "wb") as f:
            f.write(requests.get(url).content)
    return url
```

## FLUX via fal.ai (Faster, Cheaper)

```python
import fal_client
import os

os.environ["FAL_KEY"] = os.getenv("FAL_KEY")

def generate_flux_fal(
    prompt: str,
    image_size: str = "landscape_4_3",  # square, portrait_4_3, landscape_4_3, landscape_16_9
    num_images: int = 1,
    model: str = "fal-ai/flux/schnell"  # or "fal-ai/flux/dev", "fal-ai/flux-pro"
) -> list[str]:
    """Generate images with FLUX via fal.ai (fast and cheap)."""
    result = fal_client.subscribe(
        model,
        arguments={
            "prompt": prompt,
            "image_size": image_size,
            "num_images": num_images,
            "enable_safety_checker": True,
        }
    )
    return [img["url"] for img in result["images"]]
```

## Stable Diffusion (Local — No API Cost)

```python
from diffusers import StableDiffusionPipeline, DPMSolverMultistepScheduler
import torch

def load_sd_pipeline(model_id: str = "runwayml/stable-diffusion-v1-5"):
    """Load Stable Diffusion pipeline (requires GPU for reasonable speed)."""
    pipe = StableDiffusionPipeline.from_pretrained(
        model_id,
        torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32
    )
    pipe.scheduler = DPMSolverMultistepScheduler.from_config(pipe.scheduler.config)
    pipe = pipe.to("cuda" if torch.cuda.is_available() else "cpu")
    return pipe

def generate_local(
    pipe,
    prompt: str,
    negative_prompt: str = "ugly, blurry, low quality, distorted",
    num_steps: int = 20,
    guidance_scale: float = 7.5,
    width: int = 512,
    height: int = 512,
    save_path: str = "output.png"
) -> str:
    """Generate image locally with Stable Diffusion."""
    image = pipe(
        prompt=prompt,
        negative_prompt=negative_prompt,
        num_inference_steps=num_steps,
        guidance_scale=guidance_scale,
        width=width,
        height=height,
    ).images[0]
    image.save(save_path)
    return save_path
```

## Image Utilities

```python
def download_image(url: str, save_path: str) -> str:
    """Download image from URL."""
    response = requests.get(url, stream=True)
    response.raise_for_status()
    with open(save_path, "wb") as f:
        for chunk in response.iter_content(8192):
            f.write(chunk)
    return save_path

def resize_image(input_path: str, max_size: int = 1024, output_path: str = None) -> str:
    """Resize image maintaining aspect ratio."""
    img = Image.open(input_path)
    img.thumbnail((max_size, max_size), Image.LANCZOS)
    out = output_path or input_path
    img.save(out)
    return out

def create_image_grid(image_paths: list[str], cols: int = 2, output_path: str = "grid.png") -> str:
    """Arrange multiple images in a grid."""
    images = [Image.open(p) for p in image_paths]
    w, h = images[0].size
    rows = (len(images) + cols - 1) // cols
    grid = Image.new("RGB", (w * cols, h * rows))
    for i, img in enumerate(images):
        grid.paste(img, (w * (i % cols), h * (i // cols)))
    grid.save(output_path)
    return output_path

def upscale_image(input_path: str, scale: int = 2) -> str:
    """Simple upscale using Lanczos resampling."""
    img = Image.open(input_path)
    new_size = (img.width * scale, img.height * scale)
    upscaled = img.resize(new_size, Image.LANCZOS)
    output = input_path.replace(".", f"_x{scale}.")
    upscaled.save(output)
    return output
```

## Prompt Engineering for Images

```python
STYLE_MODIFIERS = {
    "photorealistic": "photorealistic, 8K, DSLR, sharp focus, professional photography",
    "cinematic":      "cinematic, film grain, dramatic lighting, movie still, anamorphic lens",
    "watercolor":     "watercolor painting, soft edges, flowing color, artistic, paper texture",
    "3d_render":      "3D render, octane render, dramatic lighting, 8K, detailed textures",
    "anime":          "anime style, studio ghibli, vibrant colors, detailed illustration",
    "icon":           "flat design, vector style, minimal, clean lines, icon, white background",
    "logo":           "professional logo, minimal, clean, vector, transparent background",
}

QUALITY_SUFFIXES = "highly detailed, masterpiece, best quality, sharp focus"
NEGATIVE_COMMON  = "ugly, blurry, low resolution, watermark, signature, deformed, distorted"

def build_prompt(subject: str, style: str = "photorealistic", extras: str = "") -> dict:
    """Build an optimized image prompt."""
    style_words = STYLE_MODIFIERS.get(style, style)
    positive = f"{subject}, {style_words}, {QUALITY_SUFFIXES}"
    if extras:
        positive = f"{positive}, {extras}"
    return {"prompt": positive, "negative_prompt": NEGATIVE_COMMON}

# Usage:
p = build_prompt("a futuristic city at sunset", style="cinematic")
result = generate_flux(p["prompt"], save_path="city.png")
```

## Batch Generation

```python
def batch_generate(prompts: list[str], provider: str = "dalle3", output_dir: str = ".") -> list[dict]:
    """Generate multiple images in batch."""
    os.makedirs(output_dir, exist_ok=True)
    results = []
    for i, prompt in enumerate(prompts):
        path = os.path.join(output_dir, f"image_{i+1:03d}.png")
        try:
            if provider == "dalle3":
                result = generate_dalle3(prompt, save_path=path)
                results.append({"prompt": prompt, "path": path, "status": "ok"})
            elif provider == "flux":
                urls = generate_flux(prompt, save_path=path)
                results.append({"prompt": prompt, "path": path, "url": urls[0], "status": "ok"})
        except Exception as e:
            results.append({"prompt": prompt, "status": "error", "error": str(e)})
    return results
```

## Cost Reference (approx. 2025 pricing)

| Model | Quality | Cost per image |
|-------|---------|----------------|
| DALL-E 3 HD | Excellent | ~$0.08 |
| DALL-E 3 Standard | Good | ~$0.04 |
| FLUX Pro (Replicate) | Excellent | ~$0.055 |
| FLUX Dev (Replicate) | Very Good | ~$0.025 |
| FLUX Schnell (Replicate) | Good | ~$0.003 |
| fal.ai FLUX Schnell | Good | ~$0.003 |
| SD Local | Cost of GPU | Free |

## References
- [OpenAI Images API](https://platform.openai.com/docs/guides/images) — DALL-E 3 docs
- [Replicate FLUX](https://replicate.com/black-forest-labs/flux-schnell) — FLUX models
- [fal.ai](https://fal.ai/models) — Fast FLUX inference
- [Diffusers](https://huggingface.co/docs/diffusers/) — Local SD generation
- [FLUX GitHub](https://github.com/black-forest-labs/flux) — Official FLUX repo
