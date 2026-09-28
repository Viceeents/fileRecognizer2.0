"""Small Tkinter drag-and-drop interface for the extension DFA."""

import tkinter as tk
from tkinter import filedialog, messagebox
from pathlib import Path
import ctypes
import os

from extension_recognizer import recognize_file

try:
    from tkinterdnd2 import DND_FILES, TkinterDnD

    HAS_DRAG_AND_DROP = True
except ImportError:
    DND_FILES = None
    TkinterDnD = None
    HAS_DRAG_AND_DROP = False


class RecognizerWindow:
    def __init__(self):
        self.root = TkinterDnD.Tk() if HAS_DRAG_AND_DROP else tk.Tk()
        self.root.title("RECOGNIZER")
        self.root.geometry("560x590")
        self.root.minsize(460, 500)
        self.root.configure(bg="#f3f5f9")

        header = tk.Frame(self.root, bg="#f3f5f9")
        header.pack(pady=(20, 4))

        logo_path = Path(__file__).parent / "assets" / "logo" / "LOGO.png"
        self._window_icon = tk.PhotoImage(file=str(logo_path))
        self.root.iconphoto(True, self._window_icon)
        self.logo_image = tk.PhotoImage(file=str(logo_path))
        scale = max(1, (max(self.logo_image.width(), self.logo_image.height()) + 43) // 44)
        if scale > 1:
            self.logo_image = self.logo_image.subsample(scale, scale)
        tk.Label(header, image=self.logo_image, bg="#f3f5f9").pack(
            side="left", padx=(0, 10)
        )

        tk.Label(
            header,
            text="RECOGNIZER",
            font=("Segoe UI", 18, "bold"),
            bg="#f3f5f9",
            fg="#172033",
        ).pack(side="left")
        tk.Label(
            self.root,
            text="Accepted: .pdf  .docx  .txt  .jpg  .png  .mp3  .mp4  .zip",
            font=("Segoe UI", 10),
            bg="#f3f5f9",
            fg="#5d687b",
        ).pack(pady=(0, 16))

        self.drop_area = tk.Label(
            self.root,
            text="Drop a file here\n\nor choose a file below",
            font=("Segoe UI", 12),
            bg="white",
            fg="#44516a",
            relief="ridge",
            borderwidth=2,
            height=5,
        )
        self.drop_area.pack(fill="x", padx=28, pady=4)
        if HAS_DRAG_AND_DROP:
            self.drop_area.drop_target_register(DND_FILES)
            self.drop_area.dnd_bind("<<Drop>>", self._on_drop)
        else:
            self.drop_area.configure(
                text="Drag and drop requires tkinterdnd2.\nUse the file picker below, or install it to enable dropping."
            )

        tk.Button(
            self.root,
            text="Choose File",
            command=self._choose_file,
            font=("Segoe UI", 10, "bold"),
            bg="#315efb",
            fg="white",
            activebackground="#2449c6",
            activeforeground="white",
            relief="flat",
            padx=18,
            pady=8,
        ).pack(pady=12)

        self.result = tk.Text(
            self.root,
            height=8,
            wrap="word",
            font=("Segoe UI", 10),
            bg="white",
            fg="#172033",
            relief="flat",
            padx=12,
            pady=10,
            state="disabled",
        )
        self.result.pack(fill="both", expand=True, padx=28, pady=(0, 8))

        self.details_button = tk.Button(
            self.root,
            text="Show DFA steps",
            command=self._toggle_details,
            font=("Segoe UI", 9),
            bg="#e5eaff",
            fg="#2449c6",
            relief="flat",
            state="disabled",
        )
        self.details_button.pack(pady=(0, 8))
        self.details = tk.Text(
            self.root,
            height=8,
            wrap="word",
            font=("Consolas", 9),
            bg="white",
            fg="#44516a",
            relief="flat",
            padx=12,
            pady=8,
            state="disabled",
        )
        self._details_visible = False

        if os.name == "nt":
            # Remove only the minimize and maximize controls. The native title
            # bar and close button remain available.
            self.root.after(100, self._remove_minimize_maximize_buttons)

    def _remove_minimize_maximize_buttons(self):
        user32 = ctypes.WinDLL("user32", use_last_error=True)
        get_window_long = getattr(user32, "GetWindowLongPtrW", user32.GetWindowLongW)
        set_window_long = getattr(user32, "SetWindowLongPtrW", user32.SetWindowLongW)
        get_window_long.argtypes = (ctypes.c_void_p, ctypes.c_int)
        get_window_long.restype = ctypes.c_ssize_t
        set_window_long.argtypes = (ctypes.c_void_p, ctypes.c_int, ctypes.c_ssize_t)
        set_window_long.restype = ctypes.c_ssize_t

        hwnd = self.root.winfo_id()
        style_index = -16  # GWL_STYLE
        style = get_window_long(hwnd, style_index)
        style &= ~(0x00020000 | 0x00010000)  # WS_MINIMIZEBOX | WS_MAXIMIZEBOX
        set_window_long(hwnd, style_index, style)

        set_window_pos = user32.SetWindowPos
        set_window_pos.argtypes = (
            ctypes.c_void_p, ctypes.c_void_p, ctypes.c_int, ctypes.c_int,
            ctypes.c_int, ctypes.c_int, ctypes.c_uint,
        )
        set_window_pos.restype = ctypes.c_int
        set_window_pos(hwnd, None, 0, 0, 0, 0, 0x0027)  # SWP_FRAMECHANGED flags

    def _choose_file(self):
        path = filedialog.askopenfilename(title="Choose a file to recognize")
        if path:
            self._show_result(path)

    def _on_drop(self, event):
        paths = self.root.tk.splitlist(event.data)
        if paths:
            self._show_result(paths[0])

    def _show_result(self, path):
        try:
            info = recognize_file(path)
        except OSError as error:
            messagebox.showerror("Could not read file metadata", str(error), parent=self.root)
            return

        verdict = "ACCEPTED" if info["accepted"] else "REJECTED"
        metadata = info["metadata"]
        content = (
            f"Recognition: {verdict}\n\n"
            f"File name: {info['name']}\n"
            f"Extension: {info['extension']}\n"
            f"Size: {metadata['size_bytes']:,} bytes\n"
            f"Type (extension-based guess): {metadata['mime_type']}\n"
            f"{metadata['created_label']}: {metadata['created']}\n"
            f"Modified: {metadata['modified']}\n\n"
            "The DFA checks the filename extension; it does not verify file contents."
        )
        self.result.configure(state="normal")
        self.result.delete("1.0", "end")
        self.result.insert("1.0", content)
        self.result.configure(state="disabled")

        self.details.configure(state="normal")
        self.details.delete("1.0", "end")
        self.details.insert(
            "1.0",
            f"Input: {info['extension']}\n"
            f"Final state: {info['final_state']}\n\n"
            + "\n".join(info["trace"]),
        )
        self.details.configure(state="disabled")
        self.details_button.configure(state="normal", text="Show DFA steps")
        if self._details_visible:
            self.details.pack_forget()
            self._details_visible = False

    def _toggle_details(self):
        if self._details_visible:
            self.details.pack_forget()
            self.details_button.configure(text="Show DFA steps")
        else:
            self.details.pack(fill="both", expand=True, padx=28, pady=(0, 16))
            self.details_button.configure(text="Hide DFA steps")
        self._details_visible = not self._details_visible

    def run(self):
        if not HAS_DRAG_AND_DROP:
            self.root.after(
                300,
                lambda: messagebox.showinfo(
                    "Enable drag and drop",
                    "Install tkinterdnd2 with: pip install tkinterdnd2\n\n"
                    "The Choose File button works without it.",
                    parent=self.root,
                ),
            )
        self.root.mainloop()
