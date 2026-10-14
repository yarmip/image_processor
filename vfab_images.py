import csv
import base64
import os
from PIL import Image
from rembg import remove  # Install via: pip install rembg

# 1. Define Blueprint SVG Template
SVG_TEMPLATE = """<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" viewBox="0 0 1200 800" width="1200" height="800">
  <defs>
    <linearGradient id="bgGrad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#0b1b2d" />
      <stop offset="100%" stop-color="#03080e" />
    </linearGradient>
    <pattern id="grid" width="40" height="40" patternUnits="userSpaceOnUse">
      <path d="M 40 0 L 0 0 0 40" fill="none" stroke="#00f0ff" stroke-width="1.0" opacity="0.15"/>
    </pattern>
    <filter id="glow">
      <feGaussianBlur stdDeviation="3" result="coloredBlur"/>
      <feMerge>
        <feMergeNode in="coloredBlur"/>
        <feMergeNode in="SourceGraphic"/>
      </feMerge>
    </filter>
  </defs>

  <!-- Background Layer -->
  <rect width="1200" height="800" fill="url(#bgGrad)"/>
  <rect width="1200" height="800" fill="url(#grid)"/>

  <!-- Logo (Top-Left) -->
  <image x="60" y="50" width="120" height="80" 
         href="data:image/png;base64,{logo_b64}" 
         xlink:href="data:image/png;base64,{logo_b64}" 
         preserveAspectRatio="xMidYMid meet"/>

  <!-- Van Cutout Image (Centered) -->
  <image x="200" y="100" width="800" height="500" 
         href="data:image/png;base64,{van_b64}" 
         xlink:href="data:image/png;base64,{van_b64}" 
         preserveAspectRatio="xMidYMid meet"/>

  <!-- Typography -->
  <text x="600" y="680" fill="#ffffff" font-family="Interstate Black" font-weight="900" font-size="52" text-anchor="middle" letter-spacing="2">{title}</text>
  <text x="600" y="730" fill="#00f0ff" font-family="Arial, sans-serif" font-weight="700" font-size="28" text-anchor="middle" letter-spacing="4" filter="url(#glow)">{subtitle}</text>
</svg>
"""

def image_to_b64(path):
    """Converts local image to base64 string."""
    if not os.path.exists(path):
        return ""
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")

def remove_bg_to_b64(input_path):
    """Removes image background automatically using rembg AI."""
    if not os.path.exists(input_path):
        return ""
    inp = Image.open(input_path)
    output = remove(inp)
    
    # Save transparent PNG to buffer
    from io import BytesIO
    buffer = BytesIO()
    output.save(buffer, format="PNG")
    return base64.b64encode(buffer.getvalue()).decode("utf-8")

def batch_process(csv_path, output_folder="dist_svgs"):
    os.makedirs(output_folder, exist_ok=True)

    with open(csv_path, mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            print(f"Processing: {row['title']}...")
            
            # Remove background from van image & convert to base64
            van_b64 = remove_bg_to_b64(row['van_image_path'])
            logo_b64 = image_to_b64(row['logo_path'])
            
            # Format SVG template
            svg_content = SVG_TEMPLATE.format(
                title=row['title'],
                subtitle=row['subtitle'],
                logo_b64=logo_b64,
                van_b64=van_b64
            )
            
            # Save final SVG
            output_path = os.path.join(output_folder, row['output_filename'])
            with open(output_path, "w", encoding="utf-8") as out:
                out.write(svg_content)
                
            print(f"Saved -> {output_path}")

if __name__ == "__main__":
    batch_process("products.csv")