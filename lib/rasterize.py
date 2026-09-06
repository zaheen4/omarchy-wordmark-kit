#!/usr/bin/env python3
"""Rasterize FIGlet text art into a seamless boot-logo PNG.

Usage: rasterize.py <art.txt> <out.png> <RRGGBB> [cell-px]
"""
import sys

from PIL import Image

SRC, DST = sys.argv[1], sys.argv[2]
HEX = sys.argv[3] if len(sys.argv) > 3 else "89b4fa"
COLOR = tuple(int(HEX[i : i + 2], 16) for i in (0, 2, 4)) + (255,)
CELL_W_ARG = float(sys.argv[4]) if len(sys.argv) > 4 else None
SS = 4
CANVAS_W, CANVAS_H = 800, 188
CELL_ASPECT = 0.5

lines = open(SRC, encoding="utf-8").read().splitlines()
while lines and not lines[0].strip():
    lines.pop(0)
while lines and not lines[-1].strip():
    lines.pop()
if not lines:
    print("rasterize.py: no drawable rows in input", file=sys.stderr)
    sys.exit(1)
cols = max(len(line) for line in lines)
rows = [line.ljust(cols) for line in lines]
nrows = len(rows)

cell_w = CELL_W_ARG or min(CANVAS_W / cols, CANVAS_H * CELL_ASPECT / nrows)
cell_h = cell_w / CELL_ASPECT
ink_w = int(round(cell_w * cols))
ink_h = int(round(cell_h * nrows))
if ink_w > CANVAS_W or ink_h > CANVAS_H:
    print(
        f"rasterize.py: word does not fit 800x188 at cell width {cell_w:.2f} "
        f"(needs {ink_w}x{ink_h}); use fewer characters",
        file=sys.stderr,
    )
    sys.exit(1)
cw, ch = cell_w * SS, cell_h * SS

img = Image.new("RGBA", (int(round(cols * cw)), int(round(nrows * ch))), (0, 0, 0, 0))
px = img.load()

for r, line in enumerate(rows):
    for c, glyph in enumerate(line):
        if glyph == " ":
            continue
        x0, y0 = int(round(c * cw)), int(round(r * ch))
        x1, y1 = int(round((c + 1) * cw)), int(round((r + 1) * ch))
        if glyph == "\u2584":
            y0 = (y0 + y1) // 2
        elif glyph == "\u2580":
            y1 = (y0 + y1) // 2
        for y in range(y0, y1):
            for x in range(x0, x1):
                px[x, y] = COLOR

img = img.resize((ink_w, ink_h), Image.LANCZOS)
canvas = Image.new("RGBA", (CANVAS_W, CANVAS_H), (0, 0, 0, 0))
canvas.alpha_composite(img, ((CANVAS_W - ink_w) // 2, (CANVAS_H - ink_h) // 2))
canvas.save(DST)
print(f"saved {DST} grid={cols}x{nrows} cell={cell_w:.2f}x{cell_h:.2f} ink={ink_w}x{ink_h}")
