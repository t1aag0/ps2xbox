# PS → Xbox

A tiny Windows tray app that makes a PS4 or PS5 controller show up as an Xbox controller. No window, just an icon in the system tray: grey while waiting for a controller, green when one is connected. Right-click it to see the status or quit.

## Button mapping

| PlayStation | Xbox |
|---|---|
| Cross / Circle / Square / Triangle | A / B / X / Y |
| Share (Create) | View (Select) |
| Options | Menu (Start) |
| PS button | Xbox button |
| L1 / R1, L2 / R2, L3 / R3 | LB / RB, LT / RT, LS / RS |
| D-pad, sticks | same |
| Touchpad | nothing |

## Using it

1. Install the **ViGEmBus** driver once: <https://github.com/nefarius/ViGEmBus/releases/latest> (the file ending in `.exe`). If you skip this, the app tells you and offers to open that page.
2. Double-click **PS2Xbox.exe**.

Windows may say "Windows protected your PC" because the app isn't signed. Click **More info → Run anyway**.

If a game reacts to every button twice, it's seeing both controllers. [HidHide](https://github.com/nefarius/HidHide/releases) hides the real one from games.

## Getting the .exe

- **Releases:** the latest PS2Xbox.exe is on the **Releases** page. To publish a new one, create a tag like `v1.1.0` (GitHub → Releases → *Draft a new release* → new tag → Publish); the exe is built and attached within a few minutes.
- **Automatic:** every push to `main` builds it on GitHub. Open the **Actions** tab, click the latest run, and download **PS2Xbox** under *Artifacts*.
- **On your own PC:** install Python (tick "Add python.exe to PATH"), then double-click `build.bat`. The result is `dist\PS2Xbox.exe`.

## Changing the mapping

Edit the `MAPPING` block at the top of `ps2xbox.py`.
