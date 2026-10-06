#!/usr/bin/env python3
"""Make the small copies of each photo that phones download instead of the full file.

Run this after dropping a new photo into images/, then run build.py.
Originals are never touched; it writes name-640w.jpg and name-1280w.jpg beside them.
"""
from PIL import Image
import glob, os

WIDTHS = [640, 1280]
SKIP = ("og-default.jpg", "placeholder.jpg")

made = kept = 0
for f in sorted(glob.glob("images/*.jpg")):
    base = os.path.basename(f)
    if base in SKIP or base[:-4].endswith(("640w", "1280w")):
        continue
    with Image.open(f) as im:
        im = im.convert("RGB")
        for w in WIDTHS:
            if im.width <= w:
                continue
            out = "images/%s-%dw.jpg" % (base[:-4], w)
            if os.path.exists(out) and os.path.getmtime(out) >= os.path.getmtime(f):
                kept += 1
                continue
            h = round(im.height * w / im.width)
            im.resize((w, h), Image.LANCZOS).save(
                out, quality=86, optimize=True, progressive=True, subsampling=1)
            print("wrote %s  %dKB" % (out, os.path.getsize(out) // 1024))
            made += 1
print("%d written, %d already up to date" % (made, kept))
