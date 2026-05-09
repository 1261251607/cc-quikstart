"""Process the cat image: crop white borders and make background transparent."""
from PIL import Image
import numpy as np

SRC = r"C:\Users\Scholar\Desktop\images.jpg"
DST = r"C:\Users\Scholar\Desktop\cat_icon.png"

img = Image.open(SRC).convert("RGBA")
arr = np.array(img)

# --- Step 1: Find bounding box of non-white content ---
# "White" = R,G,B all > 240
mask = ~((arr[:, :, 0] > 240) & (arr[:, :, 1] > 240) & (arr[:, :, 2] > 240))
rows = np.any(mask, axis=1)
cols = np.any(mask, axis=0)
if not rows.any():
    print("No non-white pixels found!"); exit(1)

rmin, rmax = np.where(rows)[0][[0, -1]]
cmin, cmax = np.where(cols)[0][[0, -1]]

# Add a tiny 3px margin so the cat isn't cut off at the edge
rmin = max(rmin - 3, 0)
rmax = min(rmax + 3, arr.shape[0] - 1)
cmin = max(cmin - 3, 0)
cmax = min(cmax + 3, arr.shape[1] - 1)

cropped = arr[rmin:rmax+1, cmin:cmax+1]

# --- Step 2: Flood-fill white background → transparent ---
# Start from all 4 edges, flood-fill white-ish pixels
h, w = cropped.shape[:2]
visited = np.zeros((h, w), dtype=bool)
stack = []

# Seed: all edge pixels that are white-ish
def is_white(pixel):
    return int(pixel[0]) > 235 and int(pixel[1]) > 235 and int(pixel[2]) > 235

for y in range(h):
    for x in [0, w-1]:
        if is_white(cropped[y, x]) and not visited[y, x]:
            visited[y, x] = True
            stack.append((y, x))
for x in range(w):
    for y in [0, h-1]:
        if is_white(cropped[y, x]) and not visited[y, x]:
            visited[y, x] = True
            stack.append((y, x))

while stack:
    y, x = stack.pop()
    cropped[y, x, 3] = 0  # make transparent
    for ny, nx in [(y-1,x), (y+1,x), (y,x-1), (y,x+1)]:
        if 0 <= ny < h and 0 <= nx < w:
            if not visited[ny, nx] and is_white(cropped[ny, nx]):
                visited[ny, nx] = True
                stack.append((ny, nx))

result = Image.fromarray(cropped, "RGBA")
result.save(DST)
print(f"Done: {SRC} → {DST}")
print(f"  Original: {img.size[0]}x{img.size[1]}")
print(f"  Cropped:  {result.size[0]}x{result.size[1]}")
