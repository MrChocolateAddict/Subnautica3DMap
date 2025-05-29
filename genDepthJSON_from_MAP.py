import json
import numpy as np
from PIL import Image

def load_color_to_depth(path):
    with open(path) as f:
        return json.load(f)

def color_to_depth(color, color_lookup):
    key = f"{color[0]},{color[1]},{color[2]}"
    return color_lookup.get(key, None)

def downsample_average(heightmap, factor=2):
    h = len(heightmap)
    w = len(heightmap[0])
    h_ds = h // factor
    w_ds = w // factor
    result = []
    for i in range(h_ds):
        row = []
        for j in range(w_ds):
            block = []
            for di in range(factor):
                for dj in range(factor):
                    val = heightmap[i*factor + di][j*factor + dj]
                    if val is not None:
                        block.append(val)
            if block:
                row.append(sum(block) / len(block))
            else:
                row.append(None)
        result.append(row)
    return result

def main():
    # Load map image and crop off legend
    img = Image.open("MAP.png").convert("RGB")
    pixels = np.array(img)[:-50, :, :]  # Remove legend at bottom
    H, W, _ = pixels.shape

    # Load the precomputed color-to-depth table
    color_lookup = load_color_to_depth("color_to_depth.json")

    # Convert image to depth values
    pixels_flat = pixels.reshape(-1, 3)
    unknown_colors = {}
    depths_flat = []

    for color in pixels_flat:
        tup = tuple(color)
        # Check if all channels are light gray (192-255) and color missing from lookup
        if all(c >= 192 and c <= 255 for c in tup) and tup not in color_lookup:
            key = "255,255,255"  # Map missing grays to white
        else:
            key = ','.join(map(str, tup))
        depth = color_lookup.get(key)
        if depth is None:
            if tup in unknown_colors:
                unknown_colors[tup] += 1
            else:
                unknown_colors[tup] = 1
        depths_flat.append(depth)

    heightmap = np.array(depths_flat).reshape(H, W)

    # Convert to list with JSON-safe values
    heightmap_list = heightmap.tolist()
    heightmap_list = [[None if v is None else v for v in row] for row in heightmap_list]

    heightmap_downsampled = downsample_average(heightmap_list, factor=2)

    # Save to file
    with open("heightmap.json", "w") as f:
        json.dump(heightmap_downsampled, f)

    print("✅ Heightmap generated using exact SCALE.png values.")
    if unknown_colors:
        print(f"\n⚠️ Found {len(unknown_colors)} unknown colors not in the scale:")
        for color, count in sorted(unknown_colors.items(), key=lambda x: -x[1]):
            print(f"Color {color} — {count} occurrences")
    else:
        print("\n✅ No unknown colors found.")

if __name__ == "__main__":
    main()
