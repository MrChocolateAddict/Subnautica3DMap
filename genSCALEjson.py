from PIL import Image
import json
import numpy as np

def generate_lookup(scale_img_path, depth_min=-500, depth_max=160, output_path='color_to_depth.json'):
    img = Image.open(scale_img_path).convert("RGB")
    pixels = np.array(img)

    H, W, _ = pixels.shape
    if H < 1 or W != 662:
        raise ValueError("Expected SCALE.png to be 662 pixels wide (any height ≥ 1)")

    # Take the top row as representative colors
    colors = pixels[0]  # Shape: (662, 3)

    depths = np.linspace(depth_min, depth_max, len(colors))
    lookup = {f"{r},{g},{b}": float(round(depth, 2)) for (r, g, b), depth in zip(colors, depths)}

    with open(output_path, 'w') as f:
        json.dump(lookup, f, indent=2)

    print(f"Lookup table saved to {output_path} with {len(lookup)} entries.")

# Run it:
generate_lookup("SCALE.png")
