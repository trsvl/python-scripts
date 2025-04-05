import pyautogui
import time
import tkinter as tk
from tkinter import messagebox

# Function to start typing based on the selected mode
def start_typing():
    word = entry_word.get()  # Get the word from the input field
    delay = entry_delay.get()  # Get the delay from the input field
    mode = mode_var.get()  # Get the selected mode

    # Validate inputs
    if not word:
        messagebox.showwarning("Input Error", "Please enter a word!")
        return
    try:
        delay = float(delay)  # Convert delay to a float
        if delay < 0.5:  # Minimum delay to prevent spam
            messagebox.showwarning("Input Error", "Delay must be at least 0.5 seconds!")
            return
    except ValueError:
        messagebox.showwarning("Input Error", "Delay must be a number!")
        return

    # Add a small delay before starting (to give you time to focus on the typing area)
    time.sleep(5)

    # Mode 1: Type the word letter by letter
    if mode == mode_options[0]:
        max_lines = 3  # Number of lines in the pyramid (adjust as needed)

        for i in range(1, max_lines + 1):
            for _ in range(i):
                pyautogui.write(word)  # Type the word
                pyautogui.write(" ")  # Add a space after the word
            pyautogui.press('enter')  # Press "Enter" to move to the next line
            time.sleep(delay)  # Optional: Add a delay between lines

        for i in range(max_lines - 1, 0, -1):
            for _ in range(i):
                pyautogui.write(word)  # Type the word
                pyautogui.write(" ")  # Add a space after the word
            pyautogui.press('enter')  # Press "Enter" to move to the next line
            time.sleep(delay) 

    # Mode 2: Type the word letter by letter with "number " prefix
    elif mode == mode_options[1]:
        for letter in word:
            pyautogui.write(f"Sneak {letter}")  # Type "number <letter>"
            pyautogui.press('enter')  # Press "Enter"
            time.sleep(delay)  # Add the user-specified delay

    messagebox.showinfo("Done", "Typing completed!")

# Create the main window
root = tk.Tk()
root.title("Word Typer")

# Create a label for the word input
label_word = tk.Label(root, text="Enter the word to type:")
label_word.pack(pady=5)

# Create an input field for the word
entry_word = tk.Entry(root, width=30)
entry_word.pack(pady=5)

# Create a label for the delay input
label_delay = tk.Label(root, text="Enter the delay between letters (in seconds):")
label_delay.pack(pady=5)

# Create an input field for the delay
entry_delay = tk.Entry(root, width=30)
entry_delay.pack(pady=5)
entry_delay.insert(0, 1.5) 

# Create a label for the mode selection
label_mode = tk.Label(root, text="Select mode:")
label_mode.pack(pady=5)

# Create a dropdown menu for mode selection
mode_var = tk.StringVar(value="Mode 1")  # Default mode
mode_options = ["Pyramid", "Sneak"]
mode_menu = tk.OptionMenu(root, mode_var, *mode_options)
mode_menu.pack(pady=5)

# Create a start button
start_button = tk.Button(root, text="Start Typing", command=start_typing)
start_button.pack(pady=10)

# Run the GUI
root.mainloop()