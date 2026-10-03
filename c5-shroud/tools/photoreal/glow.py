"""Post: a soft glow round the light line (what a camera's lens does with a bright source)."""
import sys, numpy as np
from PIL import Image
from scipy.ndimage import gaussian_filter
src, dst = sys.argv[1:3]
im = np.asarray(Image.open(src).convert('RGB')).astype(np.float32) / 255.0
lum = im.max(axis=2)
mask = np.clip((lum - 0.80) / 0.20, 0, 1)[..., None] * im
glow = sum(w * np.stack([gaussian_filter(mask[..., c], s) for c in range(3)], -1) for s, w in ((3, 0.55), (12, 0.45), (40, 0.30)))
out = 1 - (1 - im) * (1 - np.clip(glow, 0, 1))          # screen blend
Image.fromarray((np.clip(out, 0, 1) * 255).astype(np.uint8)).save(dst)
