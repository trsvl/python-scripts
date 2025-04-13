import tkinter as tk
from tkinter import ttk, messagebox
import threading
import time
import win32gui
import win32api
import win32con
import json
import os
from pynput import keyboard

CONFIG_FILE = "clicker_config.json"

default_config = {
    "paused": True,
    "interval_seconds": 0.7,
    "target_window_title": "Minecraft 1.7.10",
    "click_type": "right",
    "hotkey": "ctrl+shift+p"
}

def load_config():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r') as f:
                return json.load(f)
        except:
            return default_config
    return default_config

def save_config():
    config = {
        "paused": paused,
        "interval_seconds": interval_seconds,
        "target_window_title": target_window_title,
        "click_type": click_type.get(),
        "hotkey": hotkey_string.get()
    }
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f)

config = load_config()
paused = config["paused"]
interval_seconds = config["interval_seconds"]
target_window_title = config["target_window_title"]

# GUI Initialization
root = tk.Tk()
root.title("Advanced Auto Clicker")

click_type = tk.StringVar(value=config.get("click_type", "right"))
hotkey_string = tk.StringVar(value=config.get("hotkey", "ctrl+shift+p"))
pressed_keys = set()

def parse_hotkey_string(hotkey_str):
    keys = hotkey_str.lower().split("+")
    key_set = set()
    for k in keys:
        k = k.strip()
        if k == "ctrl":
            key_set.add(keyboard.Key.ctrl)
        elif k == "shift":
            key_set.add(keyboard.Key.shift)
        elif k == "alt":
            key_set.add(keyboard.Key.alt)
        else:
            key_set.add(k)
    return key_set

user_hotkey = parse_hotkey_string(hotkey_string.get())

def toggle_pause():
    global paused
    paused = not paused
    pause_label.config(text="Paused" if paused else "Running")

def update_interval(event=None):
    global interval_seconds
    try:
        interval_seconds = float(interval_entry.get())
        interval_label.config(text=f"Interval: {interval_seconds:.2f} sec")
    except ValueError:
        interval_label.config(text="Invalid input!")

def update_window_title(event=None):
    global target_window_title
    target_window_title = window_title_entry.get()

def update_hotkey(event=None):
    global user_hotkey
    user_hotkey = parse_hotkey_string(hotkey_entry.get())

def send_click(hwnd):
    if not hwnd or not win32gui.IsWindow(hwnd):
        return
    if click_type.get() == "right":
        win32api.SendMessage(hwnd, win32con.WM_RBUTTONDOWN, 0, 0)
        win32api.SendMessage(hwnd, win32con.WM_RBUTTONUP, 0, 0)
    else:
        win32api.SendMessage(hwnd, win32con.WM_LBUTTONDOWN, 0, 0)
        win32api.SendMessage(hwnd, win32con.WM_LBUTTONUP, 0, 0)

selected_hwnds = []

def update_window_list():
    window_listbox.delete(0, tk.END)
    hwnds.clear()

    def enum_handler(hwnd, _):
        if win32gui.IsWindowVisible(hwnd):
            title = win32gui.GetWindowText(hwnd)
            if title and target_window_title.lower() in title.lower():
                hwnds.append(hwnd)
                window_listbox.insert(tk.END, f"{title} - HWND:{hwnd}")
    
    win32gui.EnumWindows(enum_handler, None)

def apply_selection():
    global selected_hwnds
    selection = window_listbox.curselection()
    selected_hwnds = [hwnds[i] for i in selection]
    messagebox.showinfo("Selection Updated", f"{len(selected_hwnds)} window(s) selected for clicking.")

def automated_click():
    while True:
        if not paused:
            for hwnd in selected_hwnds:
                send_click(hwnd)
        time.sleep(interval_seconds)

def on_press(key):
    try:
        pressed_keys.add(key.char if hasattr(key, 'char') else key)
    except AttributeError:
        pressed_keys.add(key)

    if user_hotkey.issubset(pressed_keys):
        toggle_pause()

def on_release(key):
    try:
        pressed_keys.discard(key.char if hasattr(key, 'char') else key)
    except AttributeError:
        pass

def on_closing():
    save_config()
    root.destroy()

hwnds = []

# Start background threads
threading.Thread(target=automated_click, daemon=True).start()
keyboard_listener = keyboard.Listener(on_press=on_press, on_release=on_release)
keyboard_listener.start()

# GUI Layout
main_frame = ttk.Frame(root, padding="20")
main_frame.pack(fill=tk.BOTH, expand=True)

pause_label = ttk.Label(main_frame, text="Paused" if paused else "Running", font=("Arial", 12))
pause_button = ttk.Button(main_frame, text="Pause/Resume", command=toggle_pause)

interval_label = ttk.Label(main_frame, text=f"Interval: {interval_seconds:.2f} sec", font=("Arial", 12))
interval_entry = ttk.Entry(main_frame, font=("Arial", 12))
interval_entry.insert(0, str(interval_seconds))
interval_entry.bind("<KeyRelease>", update_interval)

window_title_label = ttk.Label(main_frame, text="Window Title (partial match)", font=("Arial", 12))
window_title_entry = ttk.Entry(main_frame, font=("Arial", 12))
window_title_entry.insert(0, target_window_title)
window_title_entry.bind("<KeyRelease>", update_window_title)

refresh_button = ttk.Button(main_frame, text="Find Windows", command=update_window_list)
apply_button = ttk.Button(main_frame, text="Apply Selection", command=apply_selection)

hotkey_label = ttk.Label(main_frame, text="Pause/Resume Hotkey (e.g., ctrl+shift+p):", font=("Arial", 12))
hotkey_entry = ttk.Entry(main_frame, font=("Arial", 12), textvariable=hotkey_string)
hotkey_entry.bind("<KeyRelease>", update_hotkey)

click_type_frame = ttk.LabelFrame(main_frame, text="Click Type", padding=10)
ttk.Radiobutton(click_type_frame, text="Left Click", variable=click_type, value="left").pack(anchor=tk.W)
ttk.Radiobutton(click_type_frame, text="Right Click", variable=click_type, value="right").pack(anchor=tk.W)

window_listbox = tk.Listbox(main_frame, selectmode=tk.MULTIPLE, height=6, width=50)
window_listbox_label = ttk.Label(main_frame, text="Select Target Window(s):")

pause_label.pack(pady=10)
pause_button.pack(pady=5)
interval_label.pack(pady=10)
interval_entry.pack(pady=5)
window_title_label.pack(pady=10)
window_title_entry.pack(pady=5)
refresh_button.pack(pady=5)
window_listbox_label.pack()
window_listbox.pack(pady=5)
apply_button.pack(pady=5)
hotkey_label.pack(pady=10)
hotkey_entry.pack(pady=5)
click_type_frame.pack(pady=15, fill=tk.X)

root.protocol("WM_DELETE_WINDOW", on_closing)
root.mainloop()
keyboard_listener.stop()
