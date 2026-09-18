#!/usr/bin/env python3
"""Builds the Plymouth boot splash: black screen, orange spinner, the mark as
watermark. Uses the two-step module, the same one CachyOS ships, so the
password prompt keeps working without any scripting."""
import math
import os
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "plymouth", "micmouse")
BLACK = (20, 17, 13, 255)
ORANGE = (255, 102, 0, 255)
DIM = (58, 47, 36, 255)
CREAM = (244, 239, 230, 255)

os.makedirs(OUT, exist_ok=True)

# --- spinner: an orange arc chasing round a dim ring ----------------------
FRAMES, SIZE = 30, 96
for i in range(FRAMES):
    img = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    box = [10, 10, SIZE - 10, SIZE - 10]
    d.arc(box, 0, 360, fill=DIM, width=6)
    start = (360 / FRAMES) * i
    d.arc(box, start, start + 90, fill=ORANGE, width=6)
    img.save(os.path.join(OUT, "throbber-%04d.png" % (i + 1)))

# --- watermark: the podcast mark ------------------------------------------
logo = Image.open(os.path.join(HERE, "brand-logo.png")).convert("RGBA")
logo = logo.crop(logo.getchannel("A").getbbox())
side = 220
w = int(side * logo.width / max(logo.width, logo.height))
h = int(side * logo.height / max(logo.width, logo.height))
logo.resize((w, h), Image.LANCZOS).save(os.path.join(OUT, "watermark.png"))

# --- password dialog pieces ----------------------------------------------
entry = Image.new("RGBA", (420, 52), (0, 0, 0, 0))
d = ImageDraw.Draw(entry)
d.rounded_rectangle([0, 0, 419, 51], radius=6, fill=(26, 22, 16, 255), outline=ORANGE, width=2)
entry.save(os.path.join(OUT, "entry.png"))

bullet = Image.new("RGBA", (16, 16), (0, 0, 0, 0))
ImageDraw.Draw(bullet).ellipse([2, 2, 13, 13], fill=ORANGE)
bullet.save(os.path.join(OUT, "bullet.png"))

lock = Image.new("RGBA", (48, 48), (0, 0, 0, 0))
d = ImageDraw.Draw(lock)
d.rounded_rectangle([10, 21, 38, 42], radius=4, fill=ORANGE)
d.arc([15, 8, 33, 30], 180, 360, fill=ORANGE, width=4)
lock.save(os.path.join(OUT, "lock.png"))

caps = Image.new("RGBA", (48, 48), (0, 0, 0, 0))
d = ImageDraw.Draw(caps)
d.polygon([(24, 10), (40, 28), (31, 28), (31, 38), (17, 38), (17, 28), (8, 28)], fill=CREAM)
caps.save(os.path.join(OUT, "capslock.png"))

kbd = Image.new("RGBA", (48, 32), (0, 0, 0, 0))
d = ImageDraw.Draw(kbd)
d.rounded_rectangle([1, 1, 46, 30], radius=4, fill=(26, 22, 16, 255), outline=CREAM, width=2)
for row in range(2):
    for col in range(5):
        x, y = 6 + col * 8, 8 + row * 9
        d.rectangle([x, y, x + 4, y + 4], fill=CREAM)
kbd.save(os.path.join(OUT, "keyboard.png"))
kbd.save(os.path.join(OUT, "keymap-render.png"))

open(os.path.join(OUT, "micmouse.plymouth"), "w", encoding="utf-8").write("""[Plymouth Theme]
Name=Микрофон и мишка
Description=Black boot splash with an orange spinner
ModuleName=two-step

[two-step]
Font=Cantarell 12
TitleFont=Cantarell Light 30
ImageDir=/usr/share/plymouth/themes/micmouse
DialogHorizontalAlignment=.5
DialogVerticalAlignment=.5
TitleHorizontalAlignment=.5
TitleVerticalAlignment=.382
HorizontalAlignment=.5
VerticalAlignment=.62
WatermarkHorizontalAlignment=.5
WatermarkVerticalAlignment=.36
Transition=none
TransitionDuration=0.0
BackgroundStartColor=0x14110d
BackgroundEndColor=0x14110d
ProgressBarBackgroundColor=0x3a2f24
ProgressBarForegroundColor=0xff6600
DialogClearsFirmwareBackground=true
MessageBelowAnimation=true

[boot-up]
UseEndAnimation=false
UseFirmwareBackground=false

[shutdown]
UseEndAnimation=false
UseFirmwareBackground=false

[reboot]
UseEndAnimation=false
UseFirmwareBackground=false

[updates]
SuppressMessages=true
ProgressBarShowPercentComplete=true
UseProgressBar=true
Title=Updating...
SubTitle=Do not turn off your computer
""")
print("plymouth theme written to", OUT)
