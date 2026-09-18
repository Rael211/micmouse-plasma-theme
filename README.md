# Микрофон и мишка — Plasma 6 theme

Black and orange desktop in the colours of the [Микрофон и мишка](https://micmouse.net)
podcast: `#14110d` surfaces, `#ff6600` accents. Breeze Dark underneath.

| Part | Where it goes |
|---|---|
| Global theme (colours, splash, wallpaper) | `package/` → `~/.local/share/plasma/look-and-feel/us.obla.micmouse.dark` |
| Window decoration | `aurorae/MicMouse` → `~/.local/share/aurorae/themes/` |
| Pointers | built by `build_cursors.py` → `~/.local/share/icons/MicMouse-Cursors` |
| Icon theme | built by `build_icons.py` → `~/.local/share/icons/MicMouse-Dark` |
| Boot splash (Plymouth) | `plymouth/micmouse` → `/usr/share/plymouth/themes/` (root) |

## Install
```bash
./install.sh          # everything but the boot splash
```
Then System Settings → Colors & Themes → Global Theme.

Boot splash, separately, because it needs root and a new initramfs:
```bash
sudo cp -r plymouth/micmouse /usr/share/plymouth/themes/
sudo sed -i 's/^Theme=.*/Theme=micmouse/' /etc/plymouth/plymouthd.conf
sudo mkinitcpio -P
```

## Notes worth keeping
- Breeze cannot colour its window outline; that is why the orange contour needs
  an own Aurorae decoration rather than a Breeze setting.
- Aurorae scales each button state to the button size, so every state needs the
  same bounding box, otherwise a bare glyph is drawn twice the size of a state
  that carries a full-box circle.
- The icon and cursor themes are generated from Breeze, not copied by hand, so
  they can be rebuilt after a Breeze update.
- The splash asks for the Cormac typeface for its Bulgarian wordmark and falls
  back to the system font when it is absent. Cormac is not redistributed here.

## Credits
- Pointers derive from the **Breeze cursor theme** by the KDE community,
  LGPL-3.0-or-later. Hotspots and animation timings are unchanged; only colour.
- The icon theme (not published) derives from **Breeze icons** by the KDE
  community, LGPL-3.0-or-later.
- The logo is the registered trademark of Микрофон и мишка, used by its owner.
- Everything else: Orlin Chotev, GPL-3.0-or-later.
