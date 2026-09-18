#!/usr/bin/env python3
"""Builds the MicMouse cursor theme: Breeze cursors repainted orange.

Xcursor files are parsed and rewritten in place of converting to PNG and back,
so hotspots, nominal sizes and animation delays survive untouched."""
import os
import shutil
import struct
import sys

SRC = "/usr/share/icons/breeze_cursors"
DST = os.path.expanduser("~/.local/share/icons/MicMouse-Cursors")
MAGIC = b"Xcur"
IMAGE_TYPE = 0xFFFD0002

# Black pointer with an orange contour: the body keeps Breeze's near-black and
# the white halo becomes the brand orange.
BODY = (20, 17, 13)
HALO = (255, 102, 0)


def recolour(argb):
    a = (argb >> 24) & 0xFF
    if a == 0:
        return argb
    r, g, b = (argb >> 16) & 0xFF, (argb >> 8) & 0xFF, argb & 0xFF
    # Xcursor stores premultiplied alpha; un-premultiply before judging colour.
    if a != 255:
        r, g, b = min(255, r * 255 // a), min(255, g * 255 // a), min(255, b * 255 // a)
    v = (r + g + b) / 765.0
    if b > r + 20 and b > g + 20:
        # Breeze's blue accents (busy spinner, link cursor) become orange
        v = 1.0
    nr = int(BODY[0] + (HALO[0] - BODY[0]) * v)
    ng = int(BODY[1] + (HALO[1] - BODY[1]) * v)
    nb = int(BODY[2] + (HALO[2] - BODY[2]) * v)
    if a != 255:
        nr, ng, nb = nr * a // 255, ng * a // 255, nb * a // 255
    return (a << 24) | (nr << 16) | (ng << 8) | nb


def convert(path, out):
    data = open(path, "rb").read()
    if data[:4] != MAGIC:
        shutil.copy(path, out)
        return False
    header, version, ntoc = struct.unpack_from("<III", data, 4)
    buf = bytearray(data)
    for i in range(ntoc):
        ctype, _subtype, pos = struct.unpack_from("<III", data, 16 + i * 12)
        if ctype != IMAGE_TYPE:
            continue
        chdr = struct.unpack_from("<I", data, pos)[0]
        width, height = struct.unpack_from("<II", data, pos + 16)
        start = pos + chdr
        count = width * height
        pixels = struct.unpack_from("<%dI" % count, data, start)
        struct.pack_into("<%dI" % count, buf, start, *[recolour(p) for p in pixels])
    open(out, "wb").write(bytes(buf))
    return True


if not os.path.isdir(SRC):
    sys.exit("breeze_cursors not found at %s" % SRC)

shutil.rmtree(DST, ignore_errors=True)
os.makedirs(os.path.join(DST, "cursors"))

done = links = 0
src_cursors = os.path.join(SRC, "cursors")
for name in sorted(os.listdir(src_cursors)):
    src = os.path.join(src_cursors, name)
    dst = os.path.join(DST, "cursors", name)
    if os.path.islink(src):
        os.symlink(os.readlink(src), dst)
        links += 1
    elif convert(src, dst):
        done += 1

open(os.path.join(DST, "index.theme"), "w", encoding="utf-8").write(
    "[Icon Theme]\nName=Микрофон и мишка\nComment=Orange pointers\nInherits=breeze_cursors\n")
open(os.path.join(DST, "cursor.theme"), "w", encoding="utf-8").write(
    "[Icon Theme]\nName=Микрофон и мишка\nInherits=breeze_cursors\n")
print("repainted %d cursors, %d aliases -> %s" % (done, links, DST))
