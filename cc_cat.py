"""cc-cat: a floating cat that launches Claude Code on click."""
import tkinter as tk
from PIL import Image, ImageTk
import subprocess
import os
import sys
import shutil

# Use script directory as base path — works from any clone location
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
IMAGE_PATH = os.path.join(SCRIPT_DIR, "cat_icon.png")
# Search for claude in PATH, with common fallbacks
CLAUDE_CMD = shutil.which("claude") or shutil.which("claude.exe") or "claude"

class FloatingClaude:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("cc-cat")
        self.root.overrideredirect(True)      # borderless
        self.root.wm_attributes("-transparentcolor", "magenta")
        self.root.wm_attributes("-alpha", 0.4)       # semi-transparent by default

        # Load RGBA image, composite onto magenta for transparentcolor keying
        raw = Image.open(IMAGE_PATH).convert("RGBA")
        w, h = raw.size
        scale = min(120 / max(w, h), 1.0)  # fit within 120px, don't upscale
        new_w, new_h = int(w * scale), int(h * scale)
        raw = raw.resize((new_w, new_h), Image.LANCZOS)

        # Composite onto magenta background → transparent areas become magenta
        bg = Image.new("RGB", (new_w, new_h), "magenta")
        bg.paste(raw, mask=raw.split()[3])  # use alpha channel as mask
        self.photo_img = ImageTk.PhotoImage(bg)

        # Canvas with magenta background (will be transparent)
        self.canvas = tk.Canvas(
            self.root,
            width=new_w, height=new_h,
            bg="magenta", highlightthickness=0
        )
        self.canvas.pack()

        # Display image centered on canvas
        self.canvas.create_image(new_w // 2, new_h // 2, image=self.photo_img)
        self.canvas.bind("<Button-3>", self.on_right_click)

        # Drag support: hold left button and move to drag, release without moving = click
        self._drag_x = 0
        self._drag_y = 0
        self._drag_start_x = 0
        self._drag_start_y = 0
        self._dragging = False
        self.canvas.bind("<ButtonPress-1>", self.on_press)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_release)

        # Mouse hover: opaque when cursor is on the cat, translucent otherwise
        self.canvas.bind("<Enter>", lambda e: self.root.wm_attributes("-alpha", 1.0))
        self.canvas.bind("<Leave>", lambda e: self.root.wm_attributes("-alpha", 0.4))

        # Context menu
        self.menu = tk.Menu(self.root, tearoff=0)
        self.menu.add_command(label="Launch Claude Code", command=self.launch_claude)
        self.menu.add_separator()
        self.menu.add_command(label="Exit", command=self.root.destroy)

        # Position: bottom-right corner of screen
        screen_w = self.root.winfo_screenwidth()
        screen_h = self.root.winfo_screenheight()
        x = screen_w - new_w - 40
        y = screen_h - new_h - 80
        self.root.geometry(f"+{x}+{y}")

    def on_press(self, event):
        self._drag_start_x = event.x_root
        self._drag_start_y = event.y_root
        self._drag_x = event.x_root - self.root.winfo_x()
        self._drag_y = event.y_root - self.root.winfo_y()
        self._dragging = False

    def on_drag(self, event):
        dx = abs(event.x_root - self._drag_start_x)
        dy = abs(event.y_root - self._drag_start_y)
        if dx > 5 or dy > 5:
            self._dragging = True
        if self._dragging:
            x = event.x_root - self._drag_x
            y = event.y_root - self._drag_y
            self.root.geometry(f"+{x}+{y}")

    def on_release(self, event):
        if not self._dragging:
            self.launch_claude()

    def on_right_click(self, event):
        """Right click: show context menu."""
        self.menu.tk_popup(event.x_root, event.y_root)

    def launch_claude(self):
        subprocess.Popen(
            [CLAUDE_CMD],
            creationflags=subprocess.CREATE_NEW_CONSOLE
        )

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    FloatingClaude().run()
