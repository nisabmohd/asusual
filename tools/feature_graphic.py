"""Builds the Play Store feature graphic (1024 x 500) in the same look as Burrow's (both apps are by mid
apps, user 2026-11-08): the logo's green as the page, a pale rounded tile with the mark in green, the
name in white and two short lines under it.

usage: python3 tools/feature_graphic.py [out file]
Writes release/feature-graphic-1024x500.png and the fastlane copy. Needs Pillow; the mark is taken
from release/icon-512.png (tools/asusual_mark.py), so it is the store icon's drawing."""
import os
import sys

from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTS = [sys.argv[1]] if len(sys.argv) > 1 else [
    os.path.join(ROOT, "release", "feature-graphic-1024x500.png"),
    os.path.join(ROOT, "fastlane", "metadata", "android", "en-US", "images", "featureGraphic.png"),
]
FONT = os.path.join(ROOT, "app", "src", "main", "res", "font", "lexend.ttf")
W, H = 1024, 500
SS = 2                                  # drawn at twice the size, then scaled down

GREEN = (0x2B, 0x6F, 0x52)              # the logo's tile (asusual-logo.zip)
TILE = (0xD6, 0xEE, 0xE2)               # a pale tint of it, like Burrow's pale tile
NAME = (0xFF, 0xFF, 0xFF)
LINES = (0xD6, 0xEE, 0xE2)

TILE_X, TILE_Y, TILE_SIZE, TILE_R = 96, 150, 200, 48   # Burrow's tile
TEXT_X = 337


def font(size, weight):
    f = ImageFont.truetype(FONT, size * SS)
    f.set_variation_by_axes([weight])
    return f


def mark(px, color):
    """The mark from release/icon-512.png (white on the green tile), `px` wide, in [color]."""
    icon = Image.open(os.path.join(ROOT, "release", "icon-512.png")).convert("L")
    lo, hi = icon.getpixel((4, 4)), icon.getextrema()[1]
    m = icon.point(lambda v: max(0, min(255, round((v - lo) * 255 / (hi - lo)))))
    # The mark's own box (it is centred on the icon), so it can be sized on its own.
    # The wave is wider than tall: keep its shape, `px` wide, in the middle of a `px` square.
    m = m.crop(m.getbbox())
    h = round(px * m.height / m.width)
    alpha = Image.new("L", (px, px), 0)
    alpha.paste(m.resize((px, h), Image.LANCZOS), (0, (px - h) // 2))
    out = Image.new("RGBA", (px, px), color + (0,))
    out.putalpha(alpha)
    return out


img = Image.new("RGBA", (W * SS, H * SS), GREEN + (255,))
d = ImageDraw.Draw(img)
d.rounded_rectangle(
    (TILE_X * SS, TILE_Y * SS, (TILE_X + TILE_SIZE) * SS - 1, (TILE_Y + TILE_SIZE) * SS - 1),
    TILE_R * SS, fill=TILE + (255,),
)
# The wave takes the share of the tile it takes on the icon (404 of 512, about 0.7 of what shows), centred exactly.
size = round(TILE_SIZE * 0.7) * SS
m = mark(size, GREEN)
img.alpha_composite(m, (TILE_X * SS + (TILE_SIZE * SS - size) // 2, TILE_Y * SS + (TILE_SIZE * SS - size) // 2))
d = ImageDraw.Draw(img)
d.text((TEXT_X * SS, 235 * SS), "Asusual", font=font(96, 600), fill=NAME, anchor="ls")
d.text((TEXT_X * SS, 297 * SS), "Small habits, kept honestly.", font=font(32, 400), fill=LINES, anchor="ls")
d.text((TEXT_X * SS, 341 * SS), "Private. No ads. Open source.", font=font(32, 400), fill=LINES, anchor="ls")

final = img.convert("RGB").resize((W, H), Image.LANCZOS)
for out in OUTS:
    final.save(out, optimize=True)
    print(out)
