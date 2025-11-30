import tkinter as tk
from tkinter import filedialog, messagebox

MAX_DIM = 512      # maximum for the larger side
MIN_DIM = 1        # minimum for width or height
MAX_RATIO = 4      # maximum ratio between width and height

def load_pxp(file_path):
    """Load a PXP file and return pixel data and dimensions."""
    pixels = []
    with open(file_path, 'r') as f:
        lines = [line.strip() for line in f if line.strip()]

    if not lines[0].startswith("size"):
        raise ValueError("Invalid PXP file: missing size definition")
    
    try:
        _, w, h = lines[0].split()
        w, h = int(w), int(h)
    except:
        raise ValueError("Invalid size syntax in PXP file")
    
    if not (MIN_DIM <= w <= MAX_DIM and MIN_DIM <= h <= MAX_DIM):
        raise ValueError(f"Invalid size: width and height must be between {MIN_DIM} and {MAX_DIM}")
    
    if w/h > MAX_RATIO or h/w > MAX_RATIO:
        raise ValueError(f"Invalid aspect ratio: max allowed ratio is {MAX_RATIO}:1")
    
    pixel_lines = lines[1:1+h]
    if len(pixel_lines) != h:
        raise ValueError("Number of pixel rows does not match height")
    
    for line in pixel_lines:
        row = line.split()
        if len(row) != w:
            raise ValueError("Number of pixels in row does not match width")
        pixels.append(row)
    
    return pixels, w, h

def draw_image(canvas, pixels, w, h):
    """Draw image using PhotoImage, dynamically scaling pixels."""
    canvas.delete("all")
    
    # determine scale factor for the largest side
    pixel_size = max(1, min(MAX_DIM // w, MAX_DIM // h))
    canvas_width = w * pixel_size
    canvas_height = h * pixel_size
    
    img = tk.PhotoImage(width=w, height=h)
    for y in range(h):
        for x in range(w):
            color_code = pixels[y][x]
            color = "#FFFFFF" if color_code == "......" else "#" + color_code
            img.put(color, (x, y))
    
    zoomed_img = img.zoom(pixel_size, pixel_size)
    offset_x = (MAX_DIM - canvas_width)//2
    offset_y = (MAX_DIM - canvas_height)//2
    canvas.config(width=MAX_DIM, height=MAX_DIM)
    canvas.create_image(offset_x, offset_y, anchor="nw", image=zoomed_img)
    canvas.image = zoomed_img  # keep reference

def open_file():
    file_path = filedialog.askopenfilename(
        title="Open Pixel Perfect Image",
        filetypes=[("Pixel Perfect Image", "*.pxp")]
    )
    if file_path:
        try:
            pixels, w, h = load_pxp(file_path)
            draw_image(canvas, pixels, w, h)
        except Exception as e:
            messagebox.showerror("Error", str(e))

# --- GUI ---
root = tk.Tk()
root.title(f"PXP Opener (1x1 to {MAX_DIM}x{MAX_DIM}, max 4:1 ratio)")
root.geometry(f"{MAX_DIM}x{MAX_DIM+60}")  # +60 for button

canvas = tk.Canvas(root, width=MAX_DIM, height=MAX_DIM, bg="white")
canvas.pack()

open_btn = tk.Button(root, text="Open", font=("Arial", 16), command=open_file)
open_btn.pack(pady=10)

root.mainloop()
