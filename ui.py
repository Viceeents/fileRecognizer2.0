"Display file recognition results and extension tests with Tkinter."

import ctypes
import os
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox
from tkinter.scrolledtext import ScrolledText

from automata import process_string
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
        """Build the main window, file controls, and result panels."""
        self.root = TkinterDnD.Tk() if HAS_DRAG_AND_DROP else tk.Tk()
        self.root.title("RECOGNIZER")
        self.root.geometry("680x700")
        self.root.minsize(560, 620)
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
            text="Drop files here\n\nor choose files below",
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
                text="Choose files below to check their extensions."
            )

        tk.Button(
            self.root,
            text="Choose files",
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

        tk.Button(
            self.root, text="Test extensions", command=self._open_simulator,
            font=("Segoe UI", 9, "bold"), bg="#e5eaff", fg="#2449c6",
            relief="flat", padx=12, pady=6,
        ).pack(pady=(0, 8))

        self.result = ScrolledText(
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
            text="Show technical steps (DFA)",
            command=self._toggle_details,
            font=("Segoe UI", 9),
            bg="#e5eaff",
            fg="#2449c6",
            relief="flat",
            state="disabled",
        )
        self.details_button.pack(pady=(0, 8))
        self.details = ScrolledText(
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
            self.root.after(100, self._remove_minimize_maximize_buttons)

    def _remove_minimize_maximize_buttons(self):
        """Hide the minimize and maximize controls on Windows."""
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
        """Open the file picker and check the selected files."""
        paths = filedialog.askopenfilenames(parent=self.root, title="Choose files to recognize")
        if paths:
            self._show_results(paths)

    def _open_simulator(self):
        """Open or focus the extension-testing window."""
        existing = getattr(self, "_simulator", None)
        if existing is not None and existing.winfo_exists():
            existing.lift()
            existing.focus_set()
            return
        window = self._simulator = tk.Toplevel(self.root)
        window.title("Test extensions")
        window.geometry("700x680")
        window.minsize(560, 580)
        window.configure(bg="#f3f5f9")
        body = tk.Frame(window, bg="#f3f5f9", padx=20, pady=20)
        body.pack(fill="both", expand=True)
        tk.Label(body, text="Test an extension", font=("Segoe UI", 18, "bold"),
                 bg="#f3f5f9", fg="#172033", anchor="w").pack(fill="x")
        tk.Label(body, text="Supported: .pdf  .docx  .txt  .jpg  .png  .mp3  .mp4  .zip",
                 font=("Segoe UI", 9), bg="#f3f5f9", fg="#44516a", anchor="w").pack(fill="x", pady=(0, 12))
        cases = ScrolledText(body, height=6, font=("Consolas", 11), wrap="word",
                             relief="flat", padx=10, pady=10, undo=True)
        cases.pack(fill="x")
        cases.insert("1.0", ".pdf\n.docx\n.exe")
        actions = tk.Frame(body, bg="#f3f5f9")
        actions.pack(fill="x", pady=12)
        show_steps = tk.BooleanVar(value=False)
        summary = tk.StringVar(value="Ready - try the examples or enter your own extensions.")
        tk.Label(body, textvariable=summary, font=("Segoe UI", 10, "bold"),
                 bg="#f3f5f9", fg="#172033", anchor="w").pack(fill="x", pady=(0, 8))
        output = ScrolledText(body, font=("Segoe UI", 10), wrap="word", state="disabled",
                              relief="flat", padx=12, pady=12)
        output.pack(fill="both", expand=True)

        def run_cases(event=None):
            """Check each input line and display its result and explanation."""
            raw = cases.get("1.0", "end-1c")
            lines = raw.split("\n") if raw else []
            output.configure(state="normal")
            output.delete("1.0", "end")
            accepted_count = 0
            for number, value in enumerate(lines, 1):
                accepted, trace, _ = process_string(value)
                accepted_count += accepted
                result = "ACCEPTED" if accepted else "REJECTED"
                output.insert("end", f"Line {number}: {value!r} - {result}\n")
                if accepted:
                    reason = "Exact match for a supported extension."
                elif not value:
                    reason = "Empty input. Enter an extension such as .pdf."
                elif any(char.isspace() for char in value):
                    reason = "Spaces and other whitespace are not allowed."
                elif not value.startswith("."):
                    reason = "Start with a dot, for example .pdf. Enter an extension, not a filename."
                elif value != value.lower():
                    reason = "Use lowercase letters, for example .pdf instead of .PDF."
                else:
                    reason = "Not a complete supported extension. Check the supported list above."
                output.insert("end", reason + "\n")
                if show_steps.get():
                    output.insert("end", "\n" + "\n".join(trace) + "\n")
                output.insert("end", "\n")
            summary.set(f"{len(lines)} tested  |  {accepted_count} accepted  |  {len(lines) - accepted_count} rejected"
                        if lines else "Enter at least one extension to test.")
            output.configure(state="disabled")
            return "break"

        tk.Button(actions, text="Run tests", command=run_cases, font=("Segoe UI", 10, "bold"),
                  bg="#315efb", fg="white", activebackground="#2449c6", activeforeground="white",
                  relief="flat", padx=18, pady=8).pack(side="left")
        tk.Checkbutton(actions, text="Show technical steps (DFA)", variable=show_steps,
                       command=run_cases, bg="#f3f5f9", font=("Segoe UI", 9)).pack(side="left", padx=12)
        tk.Label(body, text="Ctrl+Enter to run tests. Blank lines are tested as empty inputs.",
                 bg="#f3f5f9", fg="#5d687b", font=("Segoe UI", 9), anchor="w").pack(fill="x", pady=(8, 0))
        window.bind("<Control-Return>", run_cases)
        cases.focus_set()

    def _on_drop(self, event):
        """Read dropped paths and check each file."""
        try:
            paths = self.root.tk.splitlist(event.data)
        except (tk.TclError, TypeError):
            paths = ()
        if not paths:
            messagebox.showwarning(
                "No file received",
                "Drop one or more files onto the drop area.",
                parent=self.root,
            )
            return "copy"
        self._show_results(paths)
        return "copy"

    def _show_result(self, path):
        """Display the recognition result for one file."""
        self._show_results([path])

    def _show_results(self, paths):
        """Display file details, results, and optional processing steps."""
        contents = []
        traces = []
        errors = []
        for path in paths:
            try:
                info = recognize_file(path)
            except OSError as error:
                errors.append(f"{path}: {error}")
                continue

            result = "ACCEPTED" if info["accepted"] else "REJECTED"
            metadata = info["metadata"]
            full_file_name = (
                f"The file name is {info['full_file_name']}.\n"
                if info["accepted"]
                else ""
            )
            contents.append(
                f"Recognition: {result}\n\n"
                f"File name: {info['name']}\n"
                f"{full_file_name}"
                f"Extension: {info['extension']}\n"
                f"Size: {metadata['size_bytes']:,} bytes\n"
                f"Type (extension-based guess): {metadata['mime_type']}\n"
                f"{metadata['created_label']}: {metadata['created']}\n"
                f"Modified: {metadata['modified']}\n\n"
                "Only the filename extension is checked; file contents are not verified."
            )
            traces.append(
                f"File: {info['name']}\n"
                f"Input: {info['extension']}\n"
                f"Final state: {info['final_state']}\n\n"
                + "\n".join(info["trace"])
            )

        if errors and not contents:
            messagebox.showerror(
                "Could not read file metadata", "\n".join(errors), parent=self.root
            )
            return
        if errors:
            contents.append("Could not read:\n" + "\n".join(errors))

        self.result.configure(state="normal")
        self.result.delete("1.0", "end")
        self.result.insert("1.0", "\n\n---\n\n".join(contents))
        self.result.configure(state="disabled")

        self.details.configure(state="normal")
        self.details.delete("1.0", "end")
        self.details.insert("1.0", "\n\n---\n\n".join(traces))
        self.details.configure(state="disabled")
        self.details_button.configure(state="normal", text="Show technical steps (DFA)")
        if self._details_visible:
            self.details.pack_forget()
            self._details_visible = False

    def _toggle_details(self):
        """Show or hide the processing steps."""
        if self._details_visible:
            self.details.pack_forget()
            self.details_button.configure(text="Show technical steps (DFA)")
        else:
            self.details.pack(fill="both", expand=True, padx=28, pady=(0, 16))
            self.details_button.configure(text="Hide technical steps (DFA)")
        self._details_visible = not self._details_visible

    def run(self):
        """Start the interface event loop."""
        self.root.mainloop()
