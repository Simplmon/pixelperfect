import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk

ZOOM_LEVELS = [0.25, 0.5, 1, 2, 3, 4, 5, 6, 7, 8]

class PXPViewer:
    def __init__(self, root):
        self.root = root
        self.root.title("PXP Opener")
        self.root.geometry("800x600")

        # Canvas + scrollbars
        self.frame = tk.Frame(root)
        self.frame.pack(fill="both", expand=True)

        self.canvas = tk.Canvas(self.frame, bg="white")
        self.h_scroll = tk.Scrollbar(self.frame, orient="horizontal", command=self.canvas.xview)
        self.v_scroll = tk.Scrollbar(self.frame, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(xscrollcommand=self.h_scroll.set, yscrollcommand=self.v_scroll.set)

        self.canvas.grid(row=0, column=0, sticky="nsew")
        self.v_scroll.grid(row=0, column=1, sticky="ns")
        self.h_scroll.grid(row=1, column=0, sticky="ew")
        self.frame.rowconfigure(0, weight=1)
        self.frame.columnconfigure(0, weight=1)

        # Buttons + slider
        self.btn_frame = tk.Frame(root)
        self.btn_frame.pack(fill="x", pady=5)

        # Open button (rozšírené)
        self.open_btn = tk.Button(self.btn_frame, text="OPEN", font=("Arial", 12, "bold"), width=15, command=self.open_file)
        self.open_btn.pack(side="left", padx=5)

        # Zoom out button
        self.zoom_out_btn = tk.Button(self.btn_frame, text="-", font=("Arial", 12, "bold"), width=3, command=self.zoom_out)
        self.zoom_out_btn.pack(side="left", padx=2)

        # Zoom slider
        self.zoom_slider = tk.Scale(self.btn_frame, from_=0, to=len(ZOOM_LEVELS)-1,
                                    orient="horizontal", showvalue=False, command=self.slider_zoom, length=300)
        self.zoom_slider.set(2)  # default = 1x
        self.zoom_slider.pack(side="left", padx=5)

        # Zoom in button
        self.zoom_in_btn = tk.Button(self.btn_frame, text="+", font=("Arial", 12, "bold"), width=3, command=self.zoom_in)
        self.zoom_in_btn.pack(side="left", padx=2)

        # Zoom label
        self.zoom_label = tk.Label(self.btn_frame, text="Zoom: 1×", font=("Arial", 12))
        self.zoom_label.pack(side="left", padx=5)

        # Image data
        self.pil_img = None
        self.tk_img = None
        self.pixel_size = 1

        # Bind resize event to redraw centered image
        self.canvas.bind("<Configure>", lambda event: self.draw_image())

        # Inicialna kontrola tlačidiel
        self.update_zoom_buttons()

    # Open PXP file
    def open_file(self):
        file_path = filedialog.askopenfilename(
            title="Open Pixel Perfect Image",
            filetypes=[("Pixel Perfect Image", "*.pxp")]
        )
        if file_path:
            try:
                self.load_pxp(file_path)
                self.pixel_size = ZOOM_LEVELS[self.zoom_slider.get()]
                self.draw_image()
            except Exception as e:
                messagebox.showerror("Error", str(e))

    def load_pxp(self, file_path):
        with open(file_path, "r") as f:
            lines = [line.strip() for line in f if line.strip()]
        if not lines[0].startswith("size"):
            raise ValueError("Invalid PXP file")
        _, w, h = lines[0].split()
        width, height = int(w), int(h)
        if len(lines[1:]) != height:
            raise ValueError("Height mismatch")
        img = Image.new("RGB", (width, height), "white")
        for y, line in enumerate(lines[1:]):
            row = line.split()
            if len(row) != width:
                raise ValueError(f"Width mismatch at row {y}")
            for x, color_code in enumerate(row):
                if color_code == "......":
                    img.putpixel((x, y), (255, 255, 255))
                else:
                    r = int(color_code[0:2], 16)
                    g = int(color_code[2:4], 16)
                    b = int(color_code[4:6], 16)
                    img.putpixel((x, y), (r, g, b))
        self.pil_img = img
        self.pixel_size = 1

    # Draw image centered
    def draw_image(self):
        if self.pil_img:
            w, h = self.pil_img.size
            scaled_w = max(1, int(w * self.pixel_size))
            scaled_h = max(1, int(h * self.pixel_size))
            img_scaled = self.pil_img.resize((scaled_w, scaled_h), Image.NEAREST)
            self.tk_img = ImageTk.PhotoImage(img_scaled)
            self.canvas.delete("all")

            # get canvas size
            canvas_w = self.canvas.winfo_width()
            canvas_h = self.canvas.winfo_height()

            # calculate offsets for centering
            x_offset = max((canvas_w - scaled_w) // 2, 0)
            y_offset = max((canvas_h - scaled_h) // 2, 0)

            self.canvas.create_image(x_offset, y_offset, anchor="nw", image=self.tk_img)

            # scroll region covers full image or canvas
            self.canvas.config(scrollregion=(0, 0, max(scaled_w, canvas_w), max(scaled_h, canvas_h)))

            # update zoom label
            self.zoom_label.config(text=f"Zoom: {self.pixel_size}×")

            # update + / - button states
            self.update_zoom_buttons()

    # Slider callback
    def slider_zoom(self, val):
        idx = int(val)
        self.pixel_size = ZOOM_LEVELS[idx]
        self.draw_image()

    # Zoom via buttons
    def zoom_in(self):
        current_idx = self.zoom_slider.get()
        if current_idx < len(ZOOM_LEVELS) - 1:
            self.zoom_slider.set(current_idx + 1)

    def zoom_out(self):
        current_idx = self.zoom_slider.get()
        if current_idx > 0:
            self.zoom_slider.set(current_idx - 1)

    # Enable/disable zoom buttons
    def update_zoom_buttons(self):
        if self.zoom_slider.get() <= 0:
            self.zoom_out_btn.config(state="disabled")
        else:
            self.zoom_out_btn.config(state="normal")
        if self.zoom_slider.get() >= len(ZOOM_LEVELS) - 1:
            self.zoom_in_btn.config(state="disabled")
        else:
            self.zoom_in_btn.config(state="normal")

# --- main ---
root = tk.Tk()
viewer = PXPViewer(root)
root.mainloop()

