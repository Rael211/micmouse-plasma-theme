#!/usr/bin/env python3
"""Renders contents/previews/splash.png, the thumbnail the Splash Screen KCM
shows; without it the entry appears as an empty placeholder."""
from PIL import Image, ImageDraw, ImageFont

W, H = 1920, 1080
BLACK, TEXT, ORANGE, TRACK = (20, 17, 13), (244, 239, 230), (255, 102, 0), (44, 37, 29)
CORMAC = "/usr/local/share/fonts/t/Typedepot__CormacBlack.otf"

img = Image.new("RGB", (W, H), BLACK)
d = ImageDraw.Draw(img)

logo = Image.open("brand-logo.png").convert("RGBA")
logo = logo.crop(logo.getchannel("A").getbbox())
side = int(H * 0.22)
lw = int(side * logo.width / max(logo.width, logo.height))
lh = int(side * logo.height / max(logo.width, logo.height))
logo = logo.resize((lw, lh), Image.LANCZOS)
img.paste(logo, ((W - lw) // 2, int(H * 0.30)), logo)

font = ImageFont.truetype(CORMAC, int(side * 0.22))
text = "Микрофон и мишка"
tw = d.textbbox((0, 0), text, font=font)[2]
d.text(((W - tw) // 2, int(H * 0.30) + lh + int(side * 0.20)), text, font=font, fill=TEXT)

bar_w, bar_h = int(W * 0.22), 6
bx, by = (W - bar_w) // 2, int(H * 0.72)
d.rectangle([bx, by, bx + bar_w, by + bar_h], fill=TRACK)
d.rectangle([bx, by, bx + int(bar_w * 0.62), by + bar_h], fill=ORANGE)

img.save("package/contents/previews/splash.png")
print("splash preview written")
