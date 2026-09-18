#!/usr/bin/env python3
"""Renders the Global Themes preview images from the brand assets."""
from PIL import Image, ImageDraw, ImageFont

BLACK, PANEL, VIEW, BUTTON = (20, 17, 13), (26, 22, 16), (13, 11, 8), (32, 27, 21)
TEXT, MUTED, ORANGE, ORANGE2 = (244, 239, 230), (156, 146, 135), (255, 102, 0), (255, 154, 77)
CORMAC = "/usr/local/share/fonts/t/Typedepot__CormacBlack.otf"
SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
logo = Image.open("brand-logo.png").convert("RGBA")
logo = logo.crop(logo.getchannel("A").getbbox())

f = lambda p, s: ImageFont.truetype(p, s)


def render(w, h):
    img = Image.open("package/contents/wallpapers/micmouse/contents/images/1920x1080.png")
    img = img.convert("RGB").resize((w, h), Image.LANCZOS)
    s = w / 1920.0
    d = ImageDraw.Draw(img)

    wx, wy, ww, wh = int(520 * s), int(400 * s), int(1050 * s), int(520 * s)
    d.rounded_rectangle([wx, wy, wx + ww, wy + wh], radius=int(12 * s), fill=BLACK)
    d.rounded_rectangle([wx, wy, wx + ww, wy + int(58 * s)], radius=int(12 * s), fill=PANEL)
    d.rectangle([wx, wy + int(40 * s), wx + ww, wy + int(58 * s)], fill=PANEL)
    d.text((wx + int(24 * s), wy + int(16 * s)), "Episode 214 — cut list", font=f(SANS, int(24 * s)), fill=ORANGE)
    for i, c in enumerate((MUTED, MUTED, ORANGE)):
        d.ellipse([wx + ww - int((110 - i * 34) * s), wy + int(22 * s),
                   wx + ww - int((96 - i * 34) * s), wy + int(36 * s)], fill=c)

    d.rectangle([wx, wy + int(58 * s), wx + int(260 * s), wy + wh], fill=PANEL)
    d.rectangle([wx + int(260 * s), wy + int(58 * s), wx + ww, wy + wh], fill=VIEW)
    for i, name in enumerate(["Inbox", "Scripts", "Tape", "Music", "Guests", "Archive"]):
        ry = wy + int((92 + i * 62) * s)
        d.text((wx + int(32 * s), ry), name, font=f(SANS, int(22 * s)), fill=ORANGE if i == 2 else TEXT)
        if i == 2:
            d.rectangle([wx, ry - int(10 * s), wx + int(6 * s), ry + int(36 * s)], fill=ORANGE)

    rows = ["01  Студиен тон", "02  Интервю с гост — суров запис", "03  Реклама", "04  Финал"]
    for i, row in enumerate(rows):
        ry = wy + int((92 + i * 74) * s)
        if i == 1:
            d.rounded_rectangle([wx + int(286 * s), ry - int(12 * s), wx + ww - int(26 * s), ry + int(44 * s)],
                                radius=int(6 * s), fill=ORANGE)
            d.text((wx + int(306 * s), ry), row, font=f(SANS, int(24 * s)), fill=BLACK)
        else:
            d.text((wx + int(306 * s), ry), row, font=f(SANS, int(24 * s)), fill=MUTED if i == 3 else TEXT)

    bx, by = wx + ww - int(430 * s), wy + wh - int(86 * s)
    d.rounded_rectangle([bx, by, bx + int(190 * s), by + int(54 * s)], radius=int(6 * s), fill=ORANGE)
    d.text((bx + int(44 * s), by + int(14 * s)), "Render", font=f(SANS, int(24 * s)), fill=BLACK)
    d.rounded_rectangle([bx + int(214 * s), by, bx + int(404 * s), by + int(54 * s)],
                        radius=int(6 * s), fill=BUTTON, outline=ORANGE2, width=max(1, int(2 * s)))
    d.text((bx + int(262 * s), by + int(14 * s)), "Cancel", font=f(SANS, int(24 * s)), fill=TEXT)

    ph = int(72 * s)
    d.rectangle([0, h - ph, w, h], fill=PANEL)
    small = logo.resize((int(46 * s), int(46 * s)), Image.LANCZOS)
    img.paste(small, (int(24 * s), h - ph + int(13 * s)), small)
    d.rounded_rectangle([int(96 * s), h - ph + int(14 * s), int(300 * s), h - int(14 * s)], radius=int(6 * s), fill=BUTTON)
    d.rectangle([int(96 * s), h - int(16 * s), int(300 * s), h - int(12 * s)], fill=ORANGE)
    d.text((int(118 * s), h - ph + int(24 * s)), "Cutting room", font=f(SANS, int(22 * s)), fill=TEXT)
    d.text((w - int(190 * s), h - ph + int(24 * s)), "22:14", font=f(SANS, int(24 * s)), fill=ORANGE)
    return img


full = render(1920, 1080)
# Same shapes Breeze ships: the KCM falls back to the stock Breeze picture when
# it does not find previews in this exact form.
full.save("package/contents/previews/fullscreenpreview.jpg", quality=92)
full.save("package/contents/previews/fullscreenpreview.png")
full.resize((600, 337), Image.LANCZOS).save("package/contents/previews/preview.png")
print("previews written")
