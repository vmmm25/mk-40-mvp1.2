import platform
import subprocess
import logging

try:
    import pyautogui
except ImportError:
    pyautogui = None

logger = logging.getLogger(__name__)
_OS = platform.system()

def close_app():
    if not pyautogui: return
    if _OS == "Darwin": pyautogui.hotkey("command", "q")
    else:               pyautogui.hotkey("alt", "f4")
    logger.info("Closed app")

def close_window():
    if not pyautogui: return
    if _OS == "Darwin": pyautogui.hotkey("command", "w")
    else:               pyautogui.hotkey("ctrl", "w")
    logger.info("Closed window")

def full_screen():
    if not pyautogui: return
    if _OS == "Darwin": pyautogui.hotkey("ctrl", "command", "f")
    else:               pyautogui.press("f11")
    logger.info("Toggled full screen")

def minimize_window():
    if not pyautogui: return
    if _OS == "Darwin": pyautogui.hotkey("command", "m")
    else:               pyautogui.hotkey("win", "down")
    logger.info("Minimized window")

def maximize_window():
    if _OS == "Darwin":
        subprocess.run(["osascript", "-e",
            'tell application "System Events" to keystroke "f" '
            'using {control down, command down}'],
            capture_output=True)
    elif _OS == "Windows":
        if pyautogui: pyautogui.hotkey("win", "up")
    else:
        try:
            subprocess.run(["wmctrl", "-r", ":ACTIVE:", "-b", "add,maximized_vert,maximized_horz"],
                capture_output=True)
        except Exception:
            if pyautogui: pyautogui.hotkey("super", "up")
    logger.info("Maximized window")

def snap_left():
    if _OS == "Windows":
        if pyautogui: pyautogui.hotkey("win", "left")
    elif _OS == "Linux":
        try:
            subprocess.run(["wmctrl", "-r", ":ACTIVE:", "-e", "0,0,0,960,1080"],
                capture_output=True)
        except Exception:
            pass
    logger.info("Snapped window left")

def snap_right():
    if _OS == "Windows":
        if pyautogui: pyautogui.hotkey("win", "right")
    elif _OS == "Linux":
        try:
            subprocess.run(["wmctrl", "-r", ":ACTIVE:", "-e", "0,960,0,960,1080"],
                capture_output=True)
        except Exception:
            pass
    logger.info("Snapped window right")

def switch_window():
    if not pyautogui: return
    if _OS == "Darwin": pyautogui.hotkey("command", "tab")
    else:               pyautogui.hotkey("alt", "tab")
    logger.info("Switched window")

def show_desktop():
    if not pyautogui: return
    if _OS == "Darwin":   pyautogui.hotkey("fn", "f11")
    elif _OS == "Windows": pyautogui.hotkey("win", "d")
    else:                  pyautogui.hotkey("super", "d")
    logger.info("Showed desktop")

def open_task_manager():
    if _OS == "Windows":
        if pyautogui: pyautogui.hotkey("ctrl", "shift", "esc")
    elif _OS == "Darwin":
        subprocess.Popen(["open", "-a", "Activity Monitor"])
    else:
        for cmd in [["gnome-system-monitor"], ["xfce4-taskmanager"], ["htop"]]:
            if subprocess.run(["which", cmd[0]], capture_output=True).returncode == 0:
                subprocess.Popen(cmd)
                break
    logger.info("Opened task manager")
