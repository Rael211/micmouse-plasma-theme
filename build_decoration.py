#!/usr/bin/env python3
"""Generates the Aurorae window decoration: black frame with a 1px brand-orange
contour. Aurorae reads each piece by element id, so the SVG is laid out as
separate tiles on one canvas."""
import os

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "aurorae", "MicMouse")
BLACK, ORANGE, TITLE = "#14110d", "#ff6600", "#1a1610"
MUTED, TEXT, HOVER, CLOSE = "#6b5f52", "#f4efe6", "#ff9a4d", "#ff3d2e"
DIM_ORANGE = "#8a5326"

TITLE_H, CORNER, EDGE, TILE = 32, 8, 4, 8


def tile(x, y, w, h, eid, parts):
    """parts: list of (x, y, w, h, colour) in tile-local coordinates."""
    body = "".join(
        '<rect x="%g" y="%g" width="%g" height="%g" fill="%s"/>' % (x + px, y + py, pw, ph, c)
        for px, py, pw, ph, c in parts)
    return '<g id="%s">%s</g>' % (eid, body)


def frame_set(prefix, oy, contour, title_bg, maximized=False):
    """One complete 9-piece set at vertical canvas offset oy.

    maximized: no contour at all — a maximised window meets the screen edge,
    and a line there is a stripe, not an outline (Breeze drops its outline
    too). Square corners."""
    r = 0 if maximized else 6
    g = []
    if maximized:
        g.append(tile(0, oy, CORNER, TITLE_H, prefix + "-topleft", [
            (0, 0, CORNER, TITLE_H, title_bg)]))
        g.append(tile(32, oy, CORNER, TITLE_H, prefix + "-topright", [
            (0, 0, CORNER, TITLE_H, title_bg)]))
    else:
        # Aurorae squeezes the 8px corner tiles into the 3px frame (x0.375) and the
        # 4px edge tiles into 3px (x0.75); contour widths are pre-compensated so
        # the line stays 1px and continuous from titlebar to side.
        g.append(tile(0, oy, CORNER, TITLE_H, prefix + "-topleft", [
            (0, 0, CORNER, TITLE_H, title_bg), (0, 0, CORNER, 1, contour), (0, 0, 2.67, TITLE_H, contour)]))
        g.append(tile(32, oy, CORNER, TITLE_H, prefix + "-topright", [
            (0, 0, CORNER, TITLE_H, title_bg), (0, 0, CORNER, 1, contour), (CORNER - 2.67, 0, 2.67, TITLE_H, contour)]))
    g.append(tile(16, oy, TILE, TITLE_H, prefix + "-top",
                  [(0, 0, TILE, TITLE_H, title_bg)] + ([] if maximized else [(0, 0, TILE, 1, contour)])))
    side = [] if maximized else [(0, 0, 1.33, TILE, contour)]
    g.append(tile(0, oy + 40, EDGE, TILE, prefix + "-left", [(0, 0, EDGE, TILE, BLACK)] + side))
    if maximized:
        # Maximised windows: Aurorae disables every border and paints the whole
        # titlebar from the centre element stretched, so here it must be the
        # opaque titlebar strip, contour line on top.
        g.append(tile(24, oy, TILE, TITLE_H, prefix + "-center", [
            (0, 0, TILE, TITLE_H, title_bg)]))
    else:
        g.append('<g id="%s-center"><rect x="16" y="%d" width="%d" height="%d" '
                 'fill="none" fill-opacity="0"/></g>' % (prefix, oy + 40, TILE, TILE))
    side = [] if maximized else [(EDGE - 1.33, 0, 1.33, TILE, contour)]
    g.append(tile(32, oy + 40, EDGE, TILE, prefix + "-right", [(0, 0, EDGE, TILE, BLACK)] + side))
    bottom = [] if maximized else [(0, EDGE - 1, CORNER, 1, contour)]
    g.append(tile(0, oy + 56, CORNER, EDGE, prefix + "-bottomleft",
                  [(0, 0, CORNER, EDGE, BLACK)] + bottom + ([] if maximized else [(0, 0, 2.67, EDGE, contour)])))
    g.append(tile(16, oy + 56, TILE, EDGE, prefix + "-bottom",
                  [(0, 0, TILE, EDGE, BLACK)] + ([] if maximized else [(0, EDGE - 1, TILE, 1, contour)])))
    g.append(tile(32, oy + 56, CORNER, EDGE, prefix + "-bottomright",
                  [(0, 0, CORNER, EDGE, BLACK)] + bottom + ([] if maximized else [(CORNER - 2.67, 0, 2.67, EDGE, contour)])))
    return "".join(g)


def decoration():
    sets = [
        ("decoration", 0, ORANGE, TITLE, False),
        ("decoration-inactive", 80, DIM_ORANGE, BLACK, False),
        ("decoration-maximized", 160, ORANGE, TITLE, True),
        ("decoration-maximized-inactive", 240, DIM_ORANGE, BLACK, True),
    ]
    body = "".join(frame_set(*args) for args in sets)
    w, h = 48, 320
    return ('<?xml version="1.0" encoding="UTF-8"?>\n'
            '<svg xmlns="http://www.w3.org/2000/svg" width="%d" height="%d" '
            'viewBox="0 0 %d %d">%s</svg>\n' % (w, h, w, h, body))


def button(glyph, hover_fill=None):
    """glyph(colour) -> svg fragment drawn in a 16x16 box at the origin.

    Breeze puts the symbol in the titlebar colour and fills a circle behind it
    on hover; the symbol then flips to the dark background colour.

    All states sit on top of each other in ONE 16x16 document. Plasma's Svg
    renders a state by element id, so stacking costs nothing, while a wide
    document with the states side by side made KWin 6.7 size the buttons from
    the document and overlap them."""
    states = [("active-center", ORANGE, None), ("inactive-center", DIM_ORANGE, None),
              ("hover-center", BLACK, hover_fill or ORANGE),
              ("pressed-center", BLACK, HOVER),
              ("deactivated-center", MUTED, None)]
    g = []
    for eid, colour, fill in states:
        disc = ('<circle cx="8" cy="8" r="8" fill="%s"/>' % fill) if fill else ""
        box = '<rect x="0" y="0" width="16" height="16" fill="#000000" fill-opacity="0"/>'
        g.append('<g id="%s">%s%s%s</g>' % (eid, box, disc, glyph(colour)))
    return ('<?xml version="1.0" encoding="UTF-8"?>\n'
            '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" '
            'viewBox="0 0 16 16">%s</svg>\n' % "".join(g))


def stroke(d, colour, width=2):
    return ('<path d="%s" fill="none" stroke="%s" stroke-width="%g" '
            'stroke-linecap="round"/>' % (d, colour, width))


W = 1.6

GLYPHS = {
    "close": lambda c: stroke("M4.5,4.5 L11.5,11.5 M11.5,4.5 L4.5,11.5", c, W),
    "minimize": lambda c: stroke("M4,6.5 L8,10.5 L12,6.5", c, W),
    "maximize": lambda c: stroke("M4,9.5 L8,5.5 L12,9.5", c, W),
    "restore": lambda c: stroke("M4,7 L8,3.5 L12,7 M4,12.5 L8,9 L12,12.5", c, W),
    "alldesktops": lambda c: stroke("M8,3.5 L8,12.5 M3.5,8 L12.5,8", c, W),
    "keepabove": lambda c: stroke("M4,9 L8,5 L12,9 M4,12 L12,12", c, W),
    "keepbelow": lambda c: stroke("M4,7 L8,11 L12,7 M4,4 L12,4", c, W),
    "shade": lambda c: stroke("M4,4 L12,4 M4,9 L8,13 L12,9", c, W),
    "help": lambda c: stroke("M5.5,6 A2.5,2.5 0 0 1 8,8.5 L8,10 M8,12.2 L8,12.3", c, W),
}

os.makedirs(OUT, exist_ok=True)
open(os.path.join(OUT, "decoration.svg"), "w").write(decoration())
for name, glyph in GLYPHS.items():
    # the close button goes red on hover, everything else brand orange
    svg = button(glyph, hover_fill=CLOSE if name == "close" else None)
    open(os.path.join(OUT, "%s.svg" % name), "w").write(svg)

# Aurorae buttons are fixed pixel boxes; at 6 px spacing they overlapped on an
# openSUSE box at a different display scale (2026-09-25), 12 px holds there
# and on the 200% ProArt screen.
open(os.path.join(OUT, "MicMouserc"), "w").write("""[General]
ActiveTextColor=244,239,230
InactiveTextColor=156,146,135
Animation=100
LeftButtons=M
RightButtons=IAX
TitleAlignment=Left
TitleVerticalAlignment=Center
UseTextShadow=false
Shadow=true

[Layout]
BorderBottom=3
BorderLeft=3
BorderRight=3
ButtonHeight=16
ButtonMarginTop=8
ButtonSpacing=12
ButtonWidth=16
ExplicitButtonSpacer=12
PaddingBottom=0
PaddingLeft=0
PaddingRight=0
PaddingTop=0
TitleBorderLeft=8
TitleBorderRight=8
TitleEdgeBottom=0
TitleEdgeBottomMaximized=0
TitleEdgeLeft=3
TitleEdgeLeftMaximized=3
TitleEdgeRight=3
TitleEdgeRightMaximized=3
TitleEdgeTop=0
TitleEdgeTopMaximized=0
TitleHeight=32
""")

open(os.path.join(OUT, "metadata.desktop"), "w").write("""[Desktop Entry]
Name=Микрофон и мишка
Comment=Black frame with a thin orange contour
X-KDE-PluginInfo-Author=Orlin Chotev
X-KDE-PluginInfo-Email=meteoclock@obla.us
X-KDE-PluginInfo-Name=MicMouse
X-KDE-PluginInfo-Version=1.0
X-KDE-PluginInfo-Website=https://micmouse.net
X-KDE-PluginInfo-License=GPL-3.0-or-later
X-KDE-ServiceTypes=KWin/Decoration
Type=Service
""")
print("decoration written to", OUT)
