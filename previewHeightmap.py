import json
import numpy as np
from PIL import Image

def lerp(a, b, t):
    return a + t * (b - a)

def interpolate_color(value, stops):
    # stops: list of (depth, (r,g,b))
    # Find two stops between which 'value' fits
    for i in range(len(stops)-1):
        d0, c0 = stops[i]
        d1, c1 = stops[i+1]
        if d0 <= value <= d1:
            t = (value - d0) / (d1 - d0)
            r = lerp(c0[0], c1[0], t)
            g = lerp(c0[1], c1[1], t)
            b = lerp(c0[2], c1[2], t)
            return (int(r), int(g), int(b))
    # If out of range, clamp to nearest stop
    if value < stops[0][0]:
        return stops[0][1]
    else:
        return stops[-1][1]

def main():
    # Load heightmap
    with open("heightmap.json", "r") as f:
        heightmap = json.load(f)

    heightmap = np.array(heightmap, dtype=np.float32)

    # Gradient stops (depth, RGB)
    stops = [
        (-500, (0, 0, 0)),       # black
        (-300, (0, 0, 255)),     # blue
        (0, (255, 255, 255)),    # white
        (160, (255, 0, 0)),      # red
    ]

    H, W = heightmap.shape
    img_array = np.zeros((H, W, 3), dtype=np.uint8)

    for i in range(H):
        for j in range(W):
            val = heightmap[i, j]
            if val is None or np.isnan(val):
                # transparent or set to a specific background color, e.g. gray
                img_array[i, j] = (128, 128, 128)
            else:
                img_array[i, j] = interpolate_color(val, stops)

    img = Image.fromarray(img_array)
    img.save("heightmap_preview.png")
    print("Saved preview image as 'heightmap_preview.png'")

if __name__ == "__main__":
    main()
