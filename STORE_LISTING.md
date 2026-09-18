# store.kde.org listings — Микрофон и мишка

Three products; the KDE Store keeps global themes, decorations and cursors in
separate categories, and a look-and-feel package cannot carry the other two.
The categories below are the ones Plasma's own "Get New..." dialogs query
(`/usr/share/knsrcfiles/*.knsrc`); picking any other category hides the product
from those dialogs. "Plasma Theme" is NOT it: that category is Plasma Styles,
a different package type.
Upload with your openDesktop account: store.kde.org → Add Product.

Shared fields
- Version: 1.0 · Licence: GPLv3 · Homepage: https://micmouse.net
- Source: https://github.com/Rael211/micmouse-plasma-theme
- Tags: dark, black, orange, plasma6, micmouse, podcast, breeze

---

## 1. Global theme  (category: Global Themes (Plasma 6))
File: `micmouse-globaltheme-1.0.tar.gz`
Title: **Микрофон и мишка**

Black and orange desktop in the colours of the Микрофон и мишка podcast:
`#14110d` surfaces, `#ff6600` selection and accents. Breeze Dark underneath, so
every application keeps working the way it does now.

Includes the colour scheme, a branded wallpaper, and an orange splash screen.
For the full look install the matching window decoration and cursors, listed
separately.

## 2. Window decoration  (category: Window Decoration Aurorae)
File: `micmouse-aurorae-1.0.tar.gz`
Title: **Микрофон и мишка (decoration)**

Aurorae decoration: black titlebar, a one pixel orange contour around the whole
window, rounded top corners, and Breeze style chevron buttons that fill with
orange on hover (red on close). Breeze itself cannot colour its outline, which
is why this exists.

## 3. Cursors  (category: X11 Mouse Theme, shown as "Cursors")
File: `micmouse-cursors-1.0.tar.gz`
Title: **Микрофон и мишка (pointers)**

Breeze pointers with a black body and an orange halo: readable on a light
wallpaper and on a black one. All 47 cursors and their 68 aliases, hotspots and
animation timings unchanged.

Credit line for the description: "Derived from the Breeze cursor theme by the
KDE community, LGPL-3.0-or-later."

---

## Not published
- **Icon theme.** It is 1350 recoloured Breeze icons; as a derivative it has to
  ship LGPL-3.0-or-later with KDE credited, and it breaks whenever Breeze
  changes its blues. `build_icons.py` rebuilds it locally in a few seconds.
- **Sound theme.** Dropped.

## One thing to decide at upload
The wallpaper and the splash carry the podcast's logo. The KDE Store only takes
libre licences, so publishing them puts that artwork under GPL-3.0 and anyone
may reuse or modify it. To avoid that, delete `contents/wallpapers` and
`contents/splash/images/logo.png` from the tarball before uploading; the theme
still reads as МиМ through the colours.
