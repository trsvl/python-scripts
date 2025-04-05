import os
import subprocess
import tkinter as tk
from tkinter import filedialog, messagebox

def convert_file(png_path, svg_path):
    """
    Convert a single PNG file to SVG using Inkscape's command-line conversion.
    Inkscape 1.x uses the --export-filename option.
    """
    try:
        # Inkscape command for version 1.x:
        command = ["inkscape", png_path, "--export-filename", svg_path]
        subprocess.run(command, check=True)
        print(f"Converted: {png_path} -> {svg_path}")
    except subprocess.CalledProcessError as e:
        print(f"Error converting {png_path}: {e}")

def select_files_or_folder():
    """
    Ask the user whether to select a folder (all PNGs inside)
    or to select individual PNG files.
    Returns a list of PNG file paths.
    """
    # Create a hidden Tk window
    root = tk.Tk()
    root.withdraw()

    # Ask the user which mode they want
    mode = messagebox.askquestion(
        "Select Mode", 
        "Do you want to select a folder containing PNG files?\n\n"
        "Click 'Yes' for folder mode, or 'No' to select individual files."
    )
    
    png_files = []
    if mode == "yes":
        folder = filedialog.askdirectory(title="Select folder with PNG files")
        if not folder:
            messagebox.showinfo("Info", "No folder selected. Exiting.")
            return []
        # List all PNG files in the folder (non-recursive)
        for file in os.listdir(folder):
            if file.lower().endswith(".png"):
                png_files.append(os.path.join(folder, file))
    else:
        files = filedialog.askopenfilenames(
            title="Select PNG files", 
            filetypes=[("PNG Files", "*.png")]
        )
        png_files = list(files)
    
    if not png_files:
        messagebox.showinfo("Info", "No PNG files selected.")
    return png_files

def main():
    png_files = select_files_or_folder()
    if not png_files:
        return

    # Use the folder of the first selected file for output
    base_dir = os.path.dirname(png_files[0])
    output_folder = os.path.join(base_dir, "svg_output")
    os.makedirs(output_folder, exist_ok=True)

    for png_file in png_files:
        # Create the output filename by replacing .png with .svg
        filename = os.path.splitext(os.path.basename(png_file))[0] + ".svg"
        svg_path = os.path.join(output_folder, filename)
        convert_file(png_file, svg_path)

    messagebox.showinfo("Done", f"Conversion complete!\nSVG files are saved in:\n{output_folder}")

if __name__ == "__main__":
    main()
