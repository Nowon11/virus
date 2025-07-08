import sys
import subprocess
import time
import threading
import random
import os
import ctypes
import win32api
import win32con
import win32gui
import win32process
import shutil
import tempfile

CREATE_NEW_CONSOLE = 0x00000010
POPUP_TITLE = "Error"

def launch_donut_random_position(DONUT_PATH):
    screen_width = win32api.GetSystemMetrics(0)
    screen_height = win32api.GetSystemMetrics(1)
    x = random.randint(0, screen_width - 200)
    y = random.randint(0, screen_height - 200)

    try:
        proc = subprocess.Popen(
            DONUT_PATH,
            creationflags=CREATE_NEW_CONSOLE
        )
    except Exception as e:
        print("❌ Failed to launch donut.exe:", e)
        return None

    def enum_handler(hwnd, pid):
        if win32process.GetWindowThreadProcessId(hwnd)[1] == pid:
            win32gui.SetWindowPos(hwnd, win32con.HWND_TOPMOST, x, y, 0, 0,
                                  win32con.SWP_NOSIZE | win32con.SWP_SHOWWINDOW)
            return False
        return True

    time.sleep(0.3)
    win32gui.EnumWindows(lambda hwnd, _: enum_handler(hwnd, proc.pid), None)
    return proc

def show_error(message, title=POPUP_TITLE):
    ctypes.windll.user32.MessageBoxW(0, message, title, 0x10 | 0x00040000)

def is_popup_open(title=POPUP_TITLE):
    found = []
    def enum_handler(hwnd, _):
        if win32gui.IsWindowVisible(hwnd) and win32gui.GetWindowText(hwnd) == title:
            found.append(hwnd)
    win32gui.EnumWindows(enum_handler, None)
    return len(found) > 0

def main_program():
    if hasattr(sys, "_MEIPASS"):
        bundled_path = os.path.join(sys._MEIPASS, "donut.exe")
    else:
        bundled_path = os.path.join(os.path.dirname(__file__), "donut.exe")

    temp_dir = tempfile.gettempdir()
    DONUT_PATH = os.path.join(temp_dir, "donut.exe")

    if not os.path.exists(DONUT_PATH):
        try:
            shutil.copyfile(bundled_path, DONUT_PATH)
        except Exception as e:
            ctypes.windll.user32.MessageBoxW(0, f"Failed to extract donut.exe:\n{e}", "Error", 0x10)
            sys.exit(1)

    active_donuts = []
    running = True

    def donut_watcher():
        nonlocal active_donuts, running
        while running:
            for proc in active_donuts[:]:
                if proc.poll() is not None:
                    active_donuts.remove(proc)
                    for _ in range(2):
                        if running:
                            new_proc = launch_donut_random_position(DONUT_PATH)
                            if new_proc:
                                active_donuts.append(new_proc)
            time.sleep(1)

    def monitor_delete_key():
        nonlocal running
        while running:
            if win32api.GetAsyncKeyState(win32con.VK_DELETE) & 0x8000:
                running = False
                for proc in active_donuts:
                    try:
                        proc.terminate()
                    except:
                        pass
                sys.exit(0)
            time.sleep(0.1)

    threading.Thread(target=donut_watcher, daemon=True).start()
    threading.Thread(target=monitor_delete_key, daemon=True).start()

    while running:
        try:
            raise ValueError("LOL")
        except ValueError as e:
            show_error(f"Ur dumb.\n\n{e}")
            if running:
                new_proc = launch_donut_random_position(DONUT_PATH)
                if new_proc:
                    active_donuts.append(new_proc)

def write_watcher_script():
    script_path = os.path.abspath(sys.argv[0])
    exe_path = os.path.splitext(script_path)[0] + ".exe"

    watcher_code = f'''
import time
import subprocess
import os
import win32gui

POPUP_TITLE = "{POPUP_TITLE}"
EXE_PATH = r"{exe_path}"

def is_popup_open(title=POPUP_TITLE):
    found = []
    def enum_handler(hwnd, _):
        if win32gui.IsWindowVisible(hwnd) and win32gui.GetWindowText(hwnd) == title:
            found.append(hwnd)
    win32gui.EnumWindows(enum_handler, None)
    return len(found) > 0

def main():
    main_proc = None
    while True:
        if not is_popup_open():
            if main_proc is None or main_proc.poll() is not None:
                try:
                    main_proc = subprocess.Popen([EXE_PATH], creationflags=0x00000010)
                except Exception as e:
                    pass
        time.sleep(2)

if __name__ == "__main__":
    main()
'''
    script_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
    watcher_path = os.path.join(script_dir, "donut_watcher.py")
    with open(watcher_path, "w", encoding="utf-8") as f:
        f.write(watcher_code)
    return watcher_path

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "run":
        main_program()
    else:
        watcher_path = write_watcher_script()
        subprocess.Popen([sys.executable, watcher_path], creationflags=CREATE_NEW_CONSOLE)
        sys.exit(0)
