#!/bin/bash
# Installs the Микрофон и мишка global theme and its colour scheme.
set -e
here="$(cd "$(dirname "$0")" && pwd)"

# The launcher icon is looked up in the icon theme, so the logo goes to hicolor.
for size in 16 22 24 32 48 64 128 256 512; do
    dir="$HOME/.local/share/icons/hicolor/${size}x${size}/apps"
    mkdir -p "$dir"
    cp "$here/package/contents/icons/micmouse-${size}.png" "$dir/micmouse.png"
done
command -v xdg-icon-resource >/dev/null && xdg-icon-resource forceupdate --mode user || true

# Breeze Dark repainted in the brand orange; only accented icons are copied,
# the rest fall through by inheritance.
python3 "$here/build_icons.py"
python3 "$here/build_cursors.py"

# Aurorae decoration: Breeze cannot colour its window outline, so the orange
# contour needs an own decoration.
mkdir -p "$HOME/.local/share/aurorae/themes"
rm -rf "$HOME/.local/share/aurorae/themes/MicMouse"
cp -r "$here/aurorae/MicMouse" "$HOME/.local/share/aurorae/themes/MicMouse"

mkdir -p "$HOME/.local/share/color-schemes"
cp "$here/MicMouseDark.colors" "$HOME/.local/share/color-schemes/MicMouseDark.colors"

if kpackagetool6 -t Plasma/LookAndFeel --list 2>/dev/null | grep -q us.obla.micmouse.dark; then
    kpackagetool6 -t Plasma/LookAndFeel --upgrade "$here/package"
else
    kpackagetool6 -t Plasma/LookAndFeel --install "$here/package"
fi

echo "To use the logo as the launcher icon: right click the launcher -> Configure"
echo "and pick the icon named micmouse."
echo "Installed. Apply it in System Settings → Colors & Themes → Global Theme."
