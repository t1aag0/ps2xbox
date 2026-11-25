"""
ps2xbox - minimal PS4/PS5 -> Xbox controller bridge that lives in the system tray.

Requirements (Windows 10/11):
    1. ViGEmBus driver: https://github.com/nefarius/ViGEmBus/releases
    2. pip install pygame vgamepad pystray pillow
Run without a console window:
    pythonw ps2xbox.py
Or double-click build.bat to turn it into a single PS2Xbox.exe.
"""
import ctypes
import os
import sys
import threading
import time
import webbrowser

os.environ["SDL_JOYSTICK_ALLOW_BACKGROUND_EVENTS"] = "1"  # keep reading when unfocused
os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "1"

VIGEM_URL = "https://github.com/nefarius/ViGEmBus/releases/latest"


def message(text, buttons=0x40):  # 0x40 = info icon, OK button
    return ctypes.windll.user32.MessageBoxW(None, text, "PS → Xbox", buttons)


# Only one copy at a time (avoids two tray icons / two virtual pads).
ctypes.windll.kernel32.CreateMutexW(None, False, "ps2xbox_single_instance")
if ctypes.windll.kernel32.GetLastError() == 183:  # ERROR_ALREADY_EXISTS
    message("PS → Xbox is already running.\nLook for its icon in the system tray.")
    sys.exit(0)

try:
    import vgamepad as vg
except Exception:
    # 0x34 = warning icon + Yes/No buttons, 6 = Yes
    if message("A required driver (ViGEmBus) is missing.\n\n"
               "Open the download page now? Install the file ending in .exe, "
               "then start PS → Xbox again.", 0x34) == 6:
        webbrowser.open(VIGEM_URL)
    sys.exit(1)

import pygame
from pygame._sdl2 import controller
import pystray
from PIL import Image, ImageDraw

XB = vg.XUSB_BUTTON

# PlayStation button -> Xbox button. SDL names buttons by position:
# A = Cross, B = Circle, X = Square, Y = Triangle, BACK = Share/Create,
# START = Options, GUIDE = PS button. The touchpad is ignored.
MAPPING = {
    pygame.CONTROLLER_BUTTON_A: XB.XUSB_GAMEPAD_A,              # Cross    -> A
    pygame.CONTROLLER_BUTTON_B: XB.XUSB_GAMEPAD_B,              # Circle   -> B
    pygame.CONTROLLER_BUTTON_X: XB.XUSB_GAMEPAD_X,              # Square   -> X
    pygame.CONTROLLER_BUTTON_Y: XB.XUSB_GAMEPAD_Y,              # Triangle -> Y
    pygame.CONTROLLER_BUTTON_BACK: XB.XUSB_GAMEPAD_BACK,        # Share    -> Select/View
    pygame.CONTROLLER_BUTTON_START: XB.XUSB_GAMEPAD_START,      # Options  -> Start/Menu
    pygame.CONTROLLER_BUTTON_GUIDE: XB.XUSB_GAMEPAD_GUIDE,      # PS       -> Xbox
    pygame.CONTROLLER_BUTTON_LEFTSHOULDER: XB.XUSB_GAMEPAD_LEFT_SHOULDER,    # L1 -> LB
    pygame.CONTROLLER_BUTTON_RIGHTSHOULDER: XB.XUSB_GAMEPAD_RIGHT_SHOULDER,  # R1 -> RB
    pygame.CONTROLLER_BUTTON_LEFTSTICK: XB.XUSB_GAMEPAD_LEFT_THUMB,          # L3 -> LS
    pygame.CONTROLLER_BUTTON_RIGHTSTICK: XB.XUSB_GAMEPAD_RIGHT_THUMB,        # R3 -> RS
    pygame.CONTROLLER_BUTTON_DPAD_UP: XB.XUSB_GAMEPAD_DPAD_UP,
    pygame.CONTROLLER_BUTTON_DPAD_DOWN: XB.XUSB_GAMEPAD_DPAD_DOWN,
    pygame.CONTROLLER_BUTTON_DPAD_LEFT: XB.XUSB_GAMEPAD_DPAD_LEFT,
    pygame.CONTROLLER_BUTTON_DPAD_RIGHT: XB.XUSB_GAMEPAD_DPAD_RIGHT,
}

running = threading.Event()
running.set()
status = "Waiting for controller..."


def stick(v):
    return max(-32768, min(32767, v))


def trigger(v):
    return max(0, min(255, v * 255 // 32767))


def make_icon(color):
    img = Image.new("RGBA", (64, 64), (0, 0, 0, 0))
    ImageDraw.Draw(img).ellipse((8, 8, 56, 56), fill=color)
    return img


ICON_IDLE = make_icon((140, 140, 140))
ICON_ON = make_icon((16, 124, 16))  # Xbox green


def bridge(icon):
    global status
    icon.visible = True
    pygame.init()
    controller.init()
    ps, pad = None, None

    while running.is_set():
        pygame.event.pump()

        if ps is None or not ps.attached():
            if pad is not None:
                pad = None  # unplugs the virtual Xbox pad
                status = "Waiting for controller..."
                icon.icon = ICON_IDLE
                icon.update_menu()
            ps = None
            for i in range(controller.get_count()):
                if controller.is_controller(i):
                    ps = controller.Controller(i)
                    pad = vg.VX360Gamepad()
                    status = f"Connected: {ps.name}"
                    icon.icon = ICON_ON
                    icon.update_menu()
                    break
            if ps is None:
                time.sleep(1)
                continue

        for src, dst in MAPPING.items():
            if ps.get_button(src):
                pad.press_button(dst)
            else:
                pad.release_button(dst)

        a = ps.get_axis
        # SDL Y axes point down; XInput Y axes point up, hence the minus.
        pad.left_joystick(stick(a(pygame.CONTROLLER_AXIS_LEFTX)),
                          stick(-a(pygame.CONTROLLER_AXIS_LEFTY)))
        pad.right_joystick(stick(a(pygame.CONTROLLER_AXIS_RIGHTX)),
                           stick(-a(pygame.CONTROLLER_AXIS_RIGHTY)))
        pad.left_trigger(trigger(a(pygame.CONTROLLER_AXIS_TRIGGERLEFT)))
        pad.right_trigger(trigger(a(pygame.CONTROLLER_AXIS_TRIGGERRIGHT)))
        pad.update()

        time.sleep(0.004)  # ~250 Hz

    pad = None
    pygame.quit()


def quit_app(icon, _item):
    running.clear()
    icon.stop()


icon = pystray.Icon(
    "ps2xbox",
    ICON_IDLE,
    "PS → Xbox",
    menu=pystray.Menu(
        pystray.MenuItem(lambda _: status, None, enabled=False),
        pystray.MenuItem("Quit", quit_app),
    ),
)

if __name__ == "__main__":
    icon.run(setup=bridge)
