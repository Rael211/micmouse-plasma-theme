#!/usr/bin/env python3
"""Builds the Windows edition: a .theme file (dark mode, #ff6600 accent, accent
on title bars, wallpaper) plus the orange pointers converted from the Xcursor
set to .cur/.ani with hotspots and timings intact, and an apply.ps1 that
writes the registry so nothing has to be clicked through."""
import io
import os
import struct
import zipfile
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
XCUR = os.environ.get("MM_XCUR_DIR", "/tmp/mm-xcur/cursors")
OUT = os.path.join(HERE, "windows", "MicMouse")
SIZES = (32, 48, 64, 96)

# Windows cursor slot -> Xcursor names to try, in order
SLOTS = {
    "Arrow": ["left_ptr", "default"],
    "Help": ["help", "question_arrow", "whats_this"],
    "AppStarting": ["left_ptr_watch", "half-busy", "progress"],
    "Wait": ["wait", "watch"],
    "Crosshair": ["crosshair", "cross"],
    "IBeam": ["xterm", "text", "ibeam"],
    "NWPen": ["pencil", "draft"],
    "No": ["not-allowed", "crossed_circle", "circle"],
    "SizeNS": ["sb_v_double_arrow", "size_ver", "ns-resize"],
    "SizeWE": ["sb_h_double_arrow", "size_hor", "ew-resize"],
    "SizeNWSE": ["bd_double_arrow", "size_fdiag", "nwse-resize"],
    "SizeNESW": ["fd_double_arrow", "size_bdiag", "nesw-resize"],
    "SizeAll": ["fleur", "size_all", "all-scroll"],
    "UpArrow": ["sb_up_arrow", "up_arrow", "center_ptr"],
    "Hand": ["hand2", "pointer", "hand1", "pointing_hand"],
}
ORDER = ["Arrow", "Help", "AppStarting", "Wait", "Crosshair", "IBeam", "NWPen", "No",
         "SizeNS", "SizeWE", "SizeNWSE", "SizeNESW", "SizeAll", "UpArrow", "Hand", "Pin", "Person"]


def read_xcursor(path):
    """-> {pixel_size: [(image, xhot, yhot, delay_ms), ...]} in frame order"""
    d = open(path, "rb").read()
    if d[:4] != b"Xcur":
        return {}
    _h, _v, ntoc = struct.unpack_from("<III", d, 4)
    out = {}
    for i in range(ntoc):
        t, nominal, pos = struct.unpack_from("<III", d, 16 + i * 12)
        if t != 0xFFFD0002:
            continue
        chdr = struct.unpack_from("<I", d, pos)[0]
        w, h, xhot, yhot, delay = struct.unpack_from("<IIIII", d, pos + 16)
        px = struct.unpack_from("<%dI" % (w * h), d, pos + chdr)
        img = Image.new("RGBA", (w, h))
        # Xcursor is premultiplied ARGB; Windows wants straight alpha
        data = []
        for p in px:
            a = (p >> 24) & 255
            r, g, b = (p >> 16) & 255, (p >> 8) & 255, p & 255
            if 0 < a < 255:
                r, g, b = min(255, r * 255 // a), min(255, g * 255 // a), min(255, b * 255 // a)
            data.append((r, g, b, a))
        img.putdata(data)
        # keyed by pixel size: Xcursor's nominal size is a scale hint
        # (nominal 24 is a 32 px image), and Windows chooses by pixels.
        out.setdefault(w, []).append((img, xhot, yhot, delay))
    return out


def cur_bytes(frames):
    """frames: [(image, xhot, yhot)] one per size -> bytes of a .cur file"""
    entries, blobs = [], []
    offset = 6 + 16 * len(frames)
    for img, xhot, yhot in frames:
        w, h = img.size
        rows = []
        mask = bytearray()
        for y in range(h - 1, -1, -1):          # BMP is bottom-up
            row = bytearray()
            maskrow = 0
            for x in range(w):
                r, g, b, a = img.getpixel((x, y))
                row += bytes((b, g, r, a))
                maskrow = (maskrow << 1) | (1 if a == 0 else 0)
            rows.append(bytes(row))
            pad = (-w) % 32
            maskrow <<= pad
            mask += (maskrow).to_bytes((w + pad) // 8, "big")
        xor = b"".join(rows)
        bih = struct.pack("<IiiHHIIiiII", 40, w, h * 2, 1, 32, 0, len(xor) + len(mask), 0, 0, 0, 0)
        blob = bih + xor + bytes(mask)
        entries.append(struct.pack("<BBBBHHII", w if w < 256 else 0, h if h < 256 else 0,
                                   0, 0, xhot, yhot, len(blob), offset))
        blobs.append(blob)
        offset += len(blob)
    return struct.pack("<HHH", 0, 2, len(frames)) + b"".join(entries) + b"".join(blobs)


def ani_bytes(per_frame_curs, delays_ms):
    """per_frame_curs: [.cur bytes per animation frame]; delays in ms"""
    n = len(per_frame_curs)
    jiffies = [max(1, round(d / (1000 / 60))) for d in delays_ms]
    anih = struct.pack("<IIIIIIIII", 36, n, n, 0, 0, 0, 0, jiffies[0], 1)
    rate = struct.pack("<%dI" % n, *jiffies)
    seq = struct.pack("<%dI" % n, *range(n))

    def chunk(tag, payload):
        return tag + struct.pack("<I", len(payload)) + payload + (b"\0" if len(payload) % 2 else b"")

    frames = b"".join(chunk(b"icon", c) for c in per_frame_curs)
    body = (b"ACON" + chunk(b"anih", anih) + chunk(b"rate", rate) + chunk(b"seq ", seq)
            + b"LIST" + struct.pack("<I", 4 + len(frames)) + b"fram" + frames)
    return b"RIFF" + struct.pack("<I", len(body)) + body


def pick(names):
    for n in names:
        p = os.path.join(XCUR, n)
        if os.path.exists(p):
            return p
    return None


os.makedirs(os.path.join(OUT, "cursors"), exist_ok=True)
files = {}
for slot, names in SLOTS.items():
    src = pick(names)
    if not src:
        continue
    by_size = read_xcursor(src)
    sizes = [s for s in SIZES if s in by_size] or sorted(by_size)[-2:]
    nframes = min(len(by_size[s]) for s in sizes)
    if nframes > 1:
        curs, delays = [], []
        for i in range(nframes):
            curs.append(cur_bytes([(by_size[s][i][0], by_size[s][i][1], by_size[s][i][2]) for s in sizes]))
            delays.append(by_size[sizes[0]][i][3])
        name = slot.lower() + ".ani"
        open(os.path.join(OUT, "cursors", name), "wb").write(ani_bytes(curs, delays))
    else:
        name = slot.lower() + ".cur"
        open(os.path.join(OUT, "cursors", name), "wb").write(
            cur_bytes([(by_size[s][0][0], by_size[s][0][1], by_size[s][0][2]) for s in sizes]))
    files[slot] = name

# wallpaper: the 3840x2400 render, as JPEG for the Windows side
wp = Image.open(os.path.join(HERE, "package", "contents", "wallpapers", "micmouse",
                             "contents", "images", "3840x2400.png")).convert("RGB")
wp.save(os.path.join(OUT, "wallpaper.jpg"), quality=92)

base = r"%LocalAppData%\MicMouse"
cursor_lines = "\n".join("%s=%s\\cursors\\%s" % (k, base, v) for k, v in files.items())
# .theme files are read as ANSI, so the display name stays Latin here; the
# Cyrillic name is applied by the script, which Windows reads as UTF-8.
open(os.path.join(OUT, "MicMouse.theme"), "w", encoding="ascii").write(f"""[Theme]
DisplayName=MicMouse (Microphone and Mouse)
ThemeId={{7a3c2f0e-6f1b-4c1a-9c0d-micmouse00001}}

[Control Panel\\Desktop]
Wallpaper={base}\\wallpaper.jpg
TileWallpaper=0
WallpaperStyle=10

[VisualStyles]
Path=%SystemRoot%\\resources\\Themes\\Aero\\Aero.msstyles
ColorStyle=NormalColor
Size=NormalSize
AutoColorization=0
ColorizationColor=0XC4FF6600
SystemMode=Dark
AppMode=Dark

[Control Panel\\Cursors]
{cursor_lines}
DefaultValue=MicMouse

[MasterThemeSelector]
MTSM=RJSPBS
""")

scheme = ",".join(("%s\\cursors\\%s" % (base, files[k])) if k in files else "" for k in ORDER)
ps = r'''# Applies the Микрофон и мишка look on Windows 10/11 for the current user.
$ErrorActionPreference = "Stop"
$here = Split-Path -Parent $MyInvocation.MyCommand.Path
$dest = Join-Path $env:LocalAppData "MicMouse"
New-Item -ItemType Directory -Force -Path $dest | Out-Null
Copy-Item -Recurse -Force (Join-Path $here "*") $dest

# dark mode, accent #ff6600, accent on title bars and window borders
$p = "HKCU:\Software\Microsoft\Windows\CurrentVersion\Themes\Personalize"
New-Item -Force -Path $p | Out-Null
Set-ItemProperty $p AppsUseLightTheme 0 -Type DWord
Set-ItemProperty $p SystemUsesLightTheme 0 -Type DWord
Set-ItemProperty $p ColorPrevalence 1 -Type DWord
$dwm = "HKCU:\Software\Microsoft\Windows\DWM"
Set-ItemProperty $dwm ColorPrevalence 1 -Type DWord
Set-ItemProperty $dwm AccentColor 0xFF0066FF -Type DWord        # ABGR of #ff6600
Set-ItemProperty $dwm ColorizationColor 0xC4FF6600 -Type DWord
Set-ItemProperty $dwm ColorizationAfterglow 0xC4FF6600 -Type DWord
$acc = "HKCU:\Software\Microsoft\Windows\CurrentVersion\Explorer\Accent"
New-Item -Force -Path $acc | Out-Null
Set-ItemProperty $acc AccentColorMenu 0xFF0066FF -Type DWord

# pointers
$c = "HKCU:\Control Panel\Cursors"
''' + "\n".join('Set-ItemProperty $c "%s" "%s"' % (k, ("%s\\cursors\\%s" % (base, v)).replace("%LocalAppData%", "$env:LocalAppData")) for k, v in files.items()) + r'''
Set-ItemProperty $c "(Default)" "Микрофон и мишка"
Set-ItemProperty $c "Scheme Source" 1 -Type DWord
$schemes = "HKCU:\Control Panel\Cursors\Schemes"
New-Item -Force -Path $schemes | Out-Null
Set-ItemProperty $schemes "Микрофон и мишка" "''' + scheme.replace("%LocalAppData%", "%LOCALAPPDATA%") + r'''"

# wallpaper, then tell the shell about cursors and wallpaper without a logout
Add-Type @"
using System.Runtime.InteropServices;
public class Native {
  [DllImport("user32.dll", SetLastError=true)]
  public static extern bool SystemParametersInfo(uint a, uint b, string c, uint d);
}
"@
Set-ItemProperty "HKCU:\Control Panel\Desktop" WallpaperStyle 10
Set-ItemProperty "HKCU:\Control Panel\Desktop" TileWallpaper 0
[Native]::SystemParametersInfo(0x0014, 0, (Join-Path $dest "wallpaper.jpg"), 0x03) | Out-Null
[Native]::SystemParametersInfo(0x0057, 0, $null, 0x03) | Out-Null   # SPI_SETCURSORS

Write-Host "Applied. Explorer restarts so the accent takes on the taskbar."
Stop-Process -Name explorer -Force
'''
open(os.path.join(OUT, "apply.ps1"), "w", encoding="utf-8-sig").write(ps)

open(os.path.join(OUT, "README.txt"), "w", encoding="utf-8").write(
    "Микрофон и мишка for Windows 10/11\n\n"
    "Right-click apply.ps1 -> Run with PowerShell (current user only, no admin).\n"
    "It sets dark mode, the #ff6600 accent on title bars and borders, the wallpaper\n"
    "and the orange pointers, then restarts Explorer.\n\n"
    "To go back: Settings -> Personalization -> Themes, pick Windows (dark), and\n"
    "Mouse settings -> Additional mouse settings -> Pointers -> Windows Default.\n")

zpath = os.path.join(HERE, "windows", "MicMouse-Windows.zip")
with zipfile.ZipFile(zpath, "w", zipfile.ZIP_DEFLATED) as z:
    for root, _d, fs in os.walk(OUT):
        for f in fs:
            full = os.path.join(root, f)
            z.write(full, os.path.relpath(full, os.path.dirname(OUT)))
print("cursors:", ", ".join(sorted(files.values())))
print("zip:", zpath, os.path.getsize(zpath) // 1024, "KB")
