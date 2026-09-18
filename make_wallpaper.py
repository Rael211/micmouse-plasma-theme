#!/usr/bin/env python3
"""Renders the branded wallpaper shipped with the theme."""
from PIL import Image, ImageDraw, ImageFont, ImageFilter

BLACK, TEXT, ORANGE = (20, 17, 13), (244, 239, 230), (255, 102, 0)
CORMAC = "/usr/local/share/fonts/t/Typedepot__CormacBlack.otf"
logo = Image.open("brand-logo.png").convert("RGBA")
logo = logo.crop(logo.getchannel("A").getbbox())


def wallpaper(w, h):
    img = Image.new("RGB", (w, h), BLACK)
    # A low warm glow off the lower left, so the mark sits in light rather than
    # floating on flat black. Kept faint: icons have to stay readable on top.
    glow = Image.new("RGB", (w, h), BLACK)
    gd = ImageDraw.Draw(glow)
    cx, cy, r = int(w * 0.22), int(h * 0.28), int(max(w, h) * 0.55)
    for i in range(40):
        t = i / 40.0
        gd.ellipse([cx - r * (1 - t), cy - r * (1 - t), cx + r * (1 - t), cy + r * (1 - t)],
                   fill=(int(20 + 30 * t), int(17 + 15 * t), int(13 + 9 * t)))
    glow = glow.filter(ImageFilter.GaussianBlur(radius=max(w, h) // 40))
    img = Image.blend(img, glow, 0.85)

    mark_h = int(h * 0.11)
    mark = logo.resize((mark_h, mark_h), Image.LANCZOS)
    mx, my = int(w * 0.07), int(h * 0.09)
    img.paste(mark, (mx, my), mark)

    d = ImageDraw.Draw(img)
    size = int(mark_h * 0.42)
    d.text((mx + int(mark_h * 1.25), my + int(mark_h * 0.18)), "Микрофон",
           font=ImageFont.truetype(CORMAC, size), fill=TEXT)
    d.text((mx + int(mark_h * 1.25), my + int(mark_h * 0.18) + int(size * 1.15)), "и мишка",
           font=ImageFont.truetype(CORMAC, size), fill=ORANGE)
    return img


for w, h in [(3840, 2400), (2560, 1440), (1920, 1080)]:
    wallpaper(w, h).save("package/contents/wallpapers/micmouse/contents/images/%dx%d.png" % (w, h))
print("wallpapers written")
