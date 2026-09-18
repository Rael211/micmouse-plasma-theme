# Applies the Микрофон и мишка look on Windows 10/11 for the current user.
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
Set-ItemProperty $c "Arrow" "$env:LocalAppData\MicMouse\cursors\arrow.cur"
Set-ItemProperty $c "Help" "$env:LocalAppData\MicMouse\cursors\help.cur"
Set-ItemProperty $c "AppStarting" "$env:LocalAppData\MicMouse\cursors\appstarting.ani"
Set-ItemProperty $c "Wait" "$env:LocalAppData\MicMouse\cursors\wait.ani"
Set-ItemProperty $c "Crosshair" "$env:LocalAppData\MicMouse\cursors\crosshair.cur"
Set-ItemProperty $c "IBeam" "$env:LocalAppData\MicMouse\cursors\ibeam.cur"
Set-ItemProperty $c "NWPen" "$env:LocalAppData\MicMouse\cursors\nwpen.cur"
Set-ItemProperty $c "No" "$env:LocalAppData\MicMouse\cursors\no.cur"
Set-ItemProperty $c "SizeNS" "$env:LocalAppData\MicMouse\cursors\sizens.cur"
Set-ItemProperty $c "SizeWE" "$env:LocalAppData\MicMouse\cursors\sizewe.cur"
Set-ItemProperty $c "SizeNWSE" "$env:LocalAppData\MicMouse\cursors\sizenwse.cur"
Set-ItemProperty $c "SizeNESW" "$env:LocalAppData\MicMouse\cursors\sizenesw.cur"
Set-ItemProperty $c "SizeAll" "$env:LocalAppData\MicMouse\cursors\sizeall.cur"
Set-ItemProperty $c "UpArrow" "$env:LocalAppData\MicMouse\cursors\uparrow.cur"
Set-ItemProperty $c "Hand" "$env:LocalAppData\MicMouse\cursors\hand.cur"
Set-ItemProperty $c "(Default)" "Микрофон и мишка"
Set-ItemProperty $c "Scheme Source" 1 -Type DWord
$schemes = "HKCU:\Control Panel\Cursors\Schemes"
New-Item -Force -Path $schemes | Out-Null
Set-ItemProperty $schemes "Микрофон и мишка" "%LOCALAPPDATA%\MicMouse\cursors\arrow.cur,%LOCALAPPDATA%\MicMouse\cursors\help.cur,%LOCALAPPDATA%\MicMouse\cursors\appstarting.ani,%LOCALAPPDATA%\MicMouse\cursors\wait.ani,%LOCALAPPDATA%\MicMouse\cursors\crosshair.cur,%LOCALAPPDATA%\MicMouse\cursors\ibeam.cur,%LOCALAPPDATA%\MicMouse\cursors\nwpen.cur,%LOCALAPPDATA%\MicMouse\cursors\no.cur,%LOCALAPPDATA%\MicMouse\cursors\sizens.cur,%LOCALAPPDATA%\MicMouse\cursors\sizewe.cur,%LOCALAPPDATA%\MicMouse\cursors\sizenwse.cur,%LOCALAPPDATA%\MicMouse\cursors\sizenesw.cur,%LOCALAPPDATA%\MicMouse\cursors\sizeall.cur,%LOCALAPPDATA%\MicMouse\cursors\uparrow.cur,%LOCALAPPDATA%\MicMouse\cursors\hand.cur,,"

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
