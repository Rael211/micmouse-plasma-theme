#!/usr/bin/env python3
"""Builds the MicMouse icon theme: Breeze Dark with its blue accent repainted
in the brand orange. Only the files that actually carry the accent are copied;
everything else falls through to breeze-dark by inheritance."""
import os
import re
import shutil
import sys

SRC = "/usr/share/icons/breeze-dark"
DST = os.path.expanduser("~/.local/share/icons/MicMouse-Dark")
BRAND = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                     "package", "contents", "icons")

# Breeze accent blues -> the Микрофон и мишка orange family.
COLORS = {
    "3daee9": "ff6600",
    "1d99f3": "ff7a18",
    "2980b9": "d2600b",
    "93cee9": "ff9a4d",
    "0057ae": "b34700",
    "1b668f": "a34a08",
}
PATTERN = re.compile("|".join(COLORS), re.IGNORECASE)

if not os.path.isdir(SRC):
    sys.exit("breeze-dark not installed at %s" % SRC)

shutil.rmtree(DST, ignore_errors=True)
os.makedirs(DST)

copied = 0
for root, _dirs, files in os.walk(SRC):
    for name in files:
        if not name.endswith(".svg"):
            continue
        path = os.path.join(root, name)
        if os.path.islink(path):
            continue
        try:
            text = open(path, encoding="utf-8").read()
        except (UnicodeDecodeError, OSError):
            continue
        if not PATTERN.search(text):
            continue
        out = PATTERN.sub(lambda m: COLORS[m.group(0).lower()], text)
        target = os.path.join(DST, os.path.relpath(path, SRC))
        os.makedirs(os.path.dirname(target), exist_ok=True)
        open(target, "w", encoding="utf-8").write(out)
        copied += 1

# the podcast mark as a real app icon inside the theme
for size in (16, 22, 24, 32, 48, 64, 128, 256):
    d = os.path.join(DST, "apps", str(size))
    os.makedirs(d, exist_ok=True)
    shutil.copy(os.path.join(BRAND, "micmouse-%d.png" % size),
                os.path.join(d, "micmouse.png"))

index = open(os.path.join(SRC, "index.theme"), encoding="utf-8").read()
index = re.sub(r"^Name=.*$", "Name=Микрофон и мишка", index, count=1, flags=re.M)
index = re.sub(r"^Name\[.*$", "", index, flags=re.M)
index = re.sub(r"^Comment=.*$", "Comment=Breeze Dark repainted in the МиМ orange",
               index, count=1, flags=re.M)
index = re.sub(r"^Comment\[.*$", "", index, flags=re.M)
if re.search(r"^Inherits=", index, flags=re.M):
    index = re.sub(r"^Inherits=.*$", "Inherits=breeze-dark,breeze,hicolor", index,
                   count=1, flags=re.M)
else:
    index = index.replace("[Icon Theme]", "[Icon Theme]\nInherits=breeze-dark,breeze,hicolor", 1)
open(os.path.join(DST, "index.theme"), "w", encoding="utf-8").write(index)

print("recoloured %d icons into %s" % (copied, DST))
