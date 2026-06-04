from .audio_control import volume_up, volume_down, volume_mute, volume_set
from .display_control import brightness_up, brightness_down, dark_mode
from .network_control import toggle_wifi
from .power_control import restart_computer, shutdown_computer, sleep_display, lock_screen
from .window_control import (
    close_app, close_window, full_screen, minimize_window, maximize_window,
    snap_left, snap_right, switch_window, show_desktop, open_task_manager
)
from .keyboard_control import (
    focus_search, pause_video, refresh_page, close_tab, new_tab, next_tab, prev_tab,
    go_back, go_forward, zoom_in, zoom_out, zoom_reset, find_on_page, scroll_up,
    scroll_down, scroll_top, scroll_bottom, page_up, page_down, copy, paste, cut,
    undo, redo, select_all, save_file, press_enter, press_escape, press_key,
    type_text, take_screenshot, open_system_settings, open_file_explorer, open_run
)

__all__ = [
    "volume_up", "volume_down", "volume_mute", "volume_set",
    "brightness_up", "brightness_down", "dark_mode",
    "toggle_wifi",
    "restart_computer", "shutdown_computer", "sleep_display", "lock_screen",
    "close_app", "close_window", "full_screen", "minimize_window", "maximize_window",
    "snap_left", "snap_right", "switch_window", "show_desktop", "open_task_manager",
    "focus_search", "pause_video", "refresh_page", "close_tab", "new_tab", "next_tab", "prev_tab",
    "go_back", "go_forward", "zoom_in", "zoom_out", "zoom_reset", "find_on_page", "scroll_up",
    "scroll_down", "scroll_top", "scroll_bottom", "page_up", "page_down", "copy", "paste", "cut",
    "undo", "redo", "select_all", "save_file", "press_enter", "press_escape", "press_key",
    "type_text", "take_screenshot", "open_system_settings", "open_file_explorer", "open_run"
]
