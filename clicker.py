from pynput import keyboard
import tkinter as tk
import threading
import time
import win32gui
import win32api
import win32con

# Initialize the main application window
root = tk.Tk()
root.title("Automated Right Clicker")

# Initialize variables
paused = True
interval_seconds = 0.7  # Default interval for right clicks
ctrl_pressed = False
zero_pressed = False

# Set the target window title
target_window_title = "Minecraft 1.7.10"  # Replace with the actual title of your target app

def toggle_pause():
    """Toggle the paused state."""
    global paused
    paused = not paused
    pause_label.config(text="Paused" if paused else "Running")

def update_interval():
    """Update the interval_seconds value from the input field."""
    global interval_seconds
    try:
        interval_seconds = float(interval_entry.get())
    except ValueError:
        interval_label.config(text="Invalid input!", fg="red")
        return
    interval_label.config(text=f"Interval: {interval_seconds:.2f} sec", fg="black")

def find_window(title):
    """Find the handle of the window by its title."""
    return win32gui.FindWindow(None, title)

def send_right_click(hwnd):
    """Send a right-click to the target window."""
    if hwnd:
        win32api.SendMessage(hwnd, win32con.WM_RBUTTONDOWN, 0, 0)
        win32api.SendMessage(hwnd, win32con.WM_RBUTTONUP, 0, 0)

def automated_click():
    """Perform right clicks at set intervals when not paused."""
    hwnd = find_window(target_window_title)
    while True:
        if not paused and hwnd:
            send_right_click(hwnd)
        time.sleep(interval_seconds)

##################################

def on_press(key):
    """Detect when Ctrl + 0 are pressed together."""
    global ctrl_pressed, zero_pressed
    try:
        # Track Ctrl key
        if key == keyboard.Key.ctrl_l or key == keyboard.Key.ctrl_r:
            ctrl_pressed = True

        # Track 0 key
        elif hasattr(key, 'char') and key.char == '0':
            zero_pressed = True

        # Only toggle if both Ctrl and 0 are pressed together
        if ctrl_pressed and zero_pressed:
            toggle_pause()

    except AttributeError:
        pass  # Handle special keys that don't have a 'char' attribute

def on_release(key):
    """Reset key states when keys are released."""
    global ctrl_pressed, zero_pressed

    try:
        # Reset Ctrl key state when released
        if key == keyboard.Key.ctrl_l or key == keyboard.Key.ctrl_r:
            ctrl_pressed = False

        # Reset 0 key state when released
        elif hasattr(key, 'char') and key.char == '0':
            zero_pressed = False

    except AttributeError:
        pass  # Handle any other unexpected errors


    #####################################

# Start a background thread for automated clicking
click_thread = threading.Thread(target=automated_click, daemon=True)
click_thread.start()

# Start a keyboard listener to monitor key presses and releases
keyboard_listener = keyboard.Listener(on_press=on_press, on_release=on_release)
keyboard_listener.start()

# Create widgets for the Tkinter UI
pause_label = tk.Label(root, text="Paused", font=("Arial", 12))
pause_button = tk.Button(root, text="Pause/Resume", font=("Arial", 12), command=toggle_pause)

interval_label = tk.Label(root, text=f"Interval: {interval_seconds:.2f} sec", font=("Arial", 12))
interval_entry = tk.Entry(root, font=("Arial", 12))
interval_entry.insert(0, str(interval_seconds))
update_button = tk.Button(root, text="Set Interval", font=("Arial", 12), command=update_interval)

# Place widgets on the window
pause_label.pack(pady=10)
pause_button.pack(pady=5)
interval_label.pack(pady=10)
interval_entry.pack(pady=5)
update_button.pack(pady=5)

# Start the Tkinter main loop
root.mainloop()

# Stop the keyboard listener when the program exits
keyboard_listener.stop()
