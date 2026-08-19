import os
import sys
import tkinter as tk
from tkinter import filedialog, ttk, messagebox
from PIL import Image, ImageOps

class BatchPrinterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Batch Document Printer")
        self.root.geometry("450x420")
        
        self.folder_path = tk.StringVar()
        self.color_mode = tk.StringVar(value="Grayscale (B/W)")
        self.zoom_level = tk.IntVar(value=100)
        self.auto_fit = tk.BooleanVar(value=True)

        self._build_ui()

    def _build_ui(self):
        # Folder Selector
        ttk.Label(self.root, text="Select Target Folder:").pack(anchor="w", padx=15, pady=(15, 2))
        f_frame = ttk.Frame(self.root)
        f_frame.pack(fill="x", padx=15, pady=2)
        ttk.Entry(f_frame, textvariable=self.folder_path).pack(side="left", fill="x", expand=True, padx=(0, 5))
        ttk.Button(f_frame, text="Browse", command=self.browse_folder).pack(side="right")

        # Color Mode Dropdown
        ttk.Label(self.root, text="Color Mode:").pack(anchor="w", padx=15, pady=(15, 2))
        color_cb = ttk.Combobox(self.root, textvariable=self.color_mode, state="readonly")
        color_cb['values'] = ("Grayscale (B/W)", "Color", "High-Contrast B/W")
        color_cb.pack(fill="x", padx=15, pady=2)

        # Zoom Percentage Dropdown
        ttk.Label(self.root, text="Zoom Level (%):").pack(anchor="w", padx=15, pady=(15, 2))
        zoom_cb = ttk.Combobox(self.root, textvariable=self.zoom_level)
        zoom_cb['values'] = (50, 75, 90, 100, 110, 125, 150, 200)
        zoom_cb.pack(fill="x", padx=15, pady=2)

        # Fit Option
        ttk.Checkbutton(self.root, text="Fit image content to page margins", variable=self.auto_fit).pack(anchor="w", padx=15, pady=10)

        # Action Buttons
        btn_frame = ttk.Frame(self.root)
        btn_frame.pack(fill="x", padx=15, pady=20)
        
        ttk.Button(btn_frame, text="Export to PDF", command=lambda: self.process_images(mode="pdf")).pack(side="left", expand=True, fill="x", padx=(0, 5))
        ttk.Button(btn_frame, text="Send to Printer", command=lambda: self.process_images(mode="print")).pack(side="right", expand=True, fill="x", padx=(5, 0))

    def browse_folder(self):
        selected = filedialog.askdirectory()
        if selected:
            self.folder_path.set(selected)

    def process_images(self, mode="pdf"):
        folder = self.folder_path.get()
        if not folder or not os.path.exists(folder):
            messagebox.showerror("Error", "Please select a valid folder.")
            return

        # Find matching images containing "print-me"
        valid_exts = ('.jpg', '.jpeg', '.png', '.bmp', '.tiff')
        target_files = [
            os.path.join(folder, f) for f in os.listdir(folder)
            if "print-me" in f.lower() and f.lower().endswith(valid_exts)
        ]

        if not target_files:
            messagebox.showwarning("No Matches", "No images containing 'print-me' were found in this folder.")
            return

        processed_images = []
        try:
            zoom_factor = float(self.zoom_level.get()) / 100.0
        except ValueError:
            zoom_factor = 1.0

        for path in target_files:
            img = Image.open(path).convert("RGB")

            # Apply Color Processing Options
            if self.color_mode.get() == "Grayscale (B/W)":
                img = ImageOps.grayscale(img).convert("RGB")
            elif self.color_mode.get() == "High-Contrast B/W":
                gray = ImageOps.grayscale(img)
                img = gray.point(lambda p: 255 if p > 128 else 0).convert("RGB")

            # Apply Zoom / Scaling
            if zoom_factor != 1.0:
                new_w = max(1, int(img.width * zoom_factor))
                new_h = max(1, int(img.height * zoom_factor))
                img = img.resize((new_w, new_h), Image.Resampling.LANCZOS)

            processed_images.append(img)

        # Output Handling
        if mode == "pdf":
            out_pdf = os.path.join(folder, "batch_print_output.pdf")
            processed_images[0].save(out_pdf, save_all=True, append_images=processed_images[1:])
            messagebox.showinfo("Success", f"Saved {len(processed_images)} page(s) to:\n{out_pdf}")
        elif mode == "print":
            if sys.platform == "win32":
                import win32api, win32print
                printer = win32print.GetDefaultPrinter()
                temp_pdf = os.path.join(folder, "_temp_print.pdf")
                processed_images[0].save(temp_pdf, save_all=True, append_images=processed_images[1:])
                win32api.ShellExecute(0, "print", temp_pdf, None, ".", 0)
                messagebox.showinfo("Printing", f"Sent {len(processed_images)} document(s) to {printer}.")
            else:
                messagebox.showerror("Unsupported", "Direct printing in this script is configured for Windows. Use 'Export to PDF' for macOS/Linux.")

if __name__ == "__main__":
    root = tk.Tk()
    app = BatchPrinterApp(root)
    root.mainloop()