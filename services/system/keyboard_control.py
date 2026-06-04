import platform
import subprocess
import time
import logging

try:
    import pyautogui
    pyautogui.FAILSAFE = True
    pyautogui.PAUSE    = 0.05
except ImportError:
    pyautogui = None

try:
    import pyperclip
    _PYPERCLIP = True
except ImportError:
    _PYPERCLIP = False

logger = logging.getLogger(__name__)
_OS = platform.system()

def focus_search():
    if not pyautogui: return
    if _OS == "Darwin": pyautogui.hotkey("command", "l")
    else:               pyautogui.hotkey("ctrl", "l")

def pause_video():
    if pyautogui: pyautogui.press("space")

def refresh_page():
    if not pyautogui: return
    if _OS == "Darwin": pyautogui.hotkey("command", "r")
    else:               pyautogui.press("f5")

def close_tab():
    if not pyautogui: return
    if _OS == "Darwin": pyautogui.hotkey("command", "w")
    else:               pyautogui.hotkey("ctrl", "w")

def new_tab():
    if not pyautogui: return
    if _OS == "Darwin": pyautogui.hotkey("command", "t")
    else:               pyautogui.hotkey("ctrl", "t")

def next_tab():
    if not pyautogui: return
    if _OS == "Darwin": pyautogui.hotkey("command", "shift", "bracketright")
    else:               pyautogui.hotkey("ctrl", "tab")

def prev_tab():
    if not pyautogui: return
    if _OS == "Darwin": pyautogui.hotkey("command", "shift", "bracketleft")
    else:               pyautogui.hotkey("ctrl", "shift", "tab")

def go_back():
    if not pyautogui: return
    if _OS == "Darwin": pyautogui.hotkey("command", "left")
    else:               pyautogui.hotkey("alt", "left")

def go_forward():
    if not pyautogui: return
    if _OS == "Darwin": pyautogui.hotkey("command", "right")
    else:               pyautogui.hotkey("alt", "right")

def zoom_in():
    if not pyautogui: return
    if _OS == "Darwin": pyautogui.hotkey("command", "equal")
    else:               pyautogui.hotkey("ctrl", "equal")

def zoom_out():
    if not pyautogui: return
    if _OS == "Darwin": pyautogui.hotkey("command", "minus")
    else:               pyautogui.hotkey("ctrl", "minus")

def zoom_reset():
    if not pyautogui: return
    if _OS == "Darwin": pyautogui.hotkey("command", "0")
    else:               pyautogui.hotkey("ctrl", "0")

def find_on_page():
    if not pyautogui: return
    if _OS == "Darwin": pyautogui.hotkey("command", "f")
    else:               pyautogui.hotkey("ctrl", "f")

def scroll_up(amount: int = 500):
    if pyautogui: pyautogui.scroll(amount)

def scroll_down(amount: int = 500):
    if pyautogui: pyautogui.scroll(-amount)

def scroll_top():
    if not pyautogui: return
    if _OS == "Darwin": pyautogui.hotkey("command", "up")
    else:               pyautogui.hotkey("ctrl", "home")

def scroll_bottom():
    if not pyautogui: return
    if _OS == "Darwin": pyautogui.hotkey("command", "down")
    else:               pyautogui.hotkey("ctrl", "end")

def page_up():
    if pyautogui: pyautogui.press("pageup")

def page_down():
    if pyautogui: pyautogui.press("pagedown")

def copy():
    if not pyautogui: return
    if _OS == "Darwin": pyautogui.hotkey("command", "c")
    else:               pyautogui.hotkey("ctrl", "c")

def paste():
    if not pyautogui: return
    if _OS == "Darwin": pyautogui.hotkey("command", "v")
    else:               pyautogui.hotkey("ctrl", "v")

def cut():
    if not pyautogui: return
    if _OS == "Darwin": pyautogui.hotkey("command", "x")
    else:               pyautogui.hotkey("ctrl", "x")

def undo():
    if not pyautogui: return
    if _OS == "Darwin": pyautogui.hotkey("command", "z")
    else:               pyautogui.hotkey("ctrl", "z")

def redo():
    if not pyautogui: return
    if _OS == "Darwin": pyautogui.hotkey("command", "shift", "z")
    else:               pyautogui.hotkey("ctrl", "y")

def select_all():
    if not pyautogui: return
    if _OS == "Darwin": pyautogui.hotkey("command", "a")
    else:               pyautogui.hotkey("ctrl", "a")

def save_file():
    if not pyautogui: return
    if _OS == "Darwin": pyautogui.hotkey("command", "s")
    else:               pyautogui.hotkey("ctrl", "s")

def press_enter():
    if pyautogui: pyautogui.press("enter")

def press_escape():
    if pyautogui: pyautogui.press("escape")

def press_key(key: str):
    if pyautogui: pyautogui.press(key)

def type_text(text: str, press_enter_after: bool = False):
    if not text or not pyautogui:
        return
    if _PYPERCLIP:
        pyperclip.copy(str(text))
        time.sleep(0.15)
        paste()
    else:
        pyautogui.write(str(text), interval=0.03)
    if press_enter_after:
        time.sleep(0.1)
        pyautogui.press("enter")
    logger.info("Typed text (length: %s)", len(text))

def take_screenshot():
    if _OS == "Windows":
        if pyautogui: pyautogui.hotkey("win", "shift", "s")
    elif _OS == "Darwin":
        if pyautogui: pyautogui.hotkey("command", "shift", "3")
    else:
        for cmd in [["scrot"], ["gnome-screenshot"], ["import", "-window", "root", "screenshot.png"]]:
            if subprocess.run(["which", cmd[0]], capture_output=True).returncode == 0:
                subprocess.Popen(cmd)
                return
        if pyautogui: pyautogui.hotkey("ctrl", "print_screen")
    logger.info("Took screenshot")

def open_system_settings():
    if _OS == "Windows":
        if pyautogui: pyautogui.hotkey("win", "i")
    elif _OS == "Darwin":
        subprocess.Popen(["open", "-a", "System Preferences"])
    else:
        for cmd in [["gnome-control-center"], ["xfce4-settings-manager"], ["kcmshell5"]]:
            if subprocess.run(["which", cmd[0]], capture_output=True).returncode == 0:
                subprocess.Popen(cmd)
                return
    logger.info("Opened system settings")

def open_file_explorer():
    if _OS == "Windows":
        if pyautogui: pyautogui.hotkey("win", "e")
    elif _OS == "Darwin":
        from pathlib import Path
        subprocess.Popen(["open", str(Path.home())])
    else:
        for cmd in [["nautilus"], ["thunar"], ["dolphin"], ["nemo"]]:
            if subprocess.run(["which", cmd[0]], capture_output=True).returncode == 0:
                subprocess.Popen(cmd)
                return
        from pathlib import Path
        subprocess.Popen(["xdg-open", str(Path.home())])
    logger.info("Opened file explorer")

def open_run():
    if _OS == "Windows":
        if pyautogui: pyautogui.hotkey("win", "r")
    logger.info("Opened run dialog")
