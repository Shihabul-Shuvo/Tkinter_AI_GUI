# main application and navigation
import os
import shutil
import tkinter as tk
from tkinter import ttk, filedialog
from app.views.home_view import HomeView
from app.controllers.model_controller import ModelController


class ToolTip:
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tip = None
        widget.bind("<Enter>", self.show)
        widget.bind("<Leave>", self.hide)

    def show(self, _e=None):
        if self.tip is not None:
            return
        x, y, _, _ = self.widget.bbox("insert") if hasattr(self.widget, "bbox") else (0, 0, 0, 0)
        x += self.widget.winfo_rootx() + 20
        y += self.widget.winfo_rooty() + 20
        self.tip = tk.Toplevel(self.widget)
        self.tip.wm_overrideredirect(True)
        self.tip.wm_geometry(f"+{x}+{y}")
        lbl = ttk.Label(self.tip, text=self.text, relief="solid", borderwidth=1, padding=4)
        lbl.pack()

    def hide(self, _e=None):
        if self.tip is not None:
            self.tip.destroy()
            self.tip = None


class MainApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Tkinter AI GUI")
        self.geometry("1000x700")
        self.minsize(900, 600)
        self.center_window()

        self.ttk_style = ttk.Style(self)
        # Configure custom styles (accent colors)
        primary = "#2C7BE5"
        secondary = "#21C197"
        self.ttk_style.configure("Accent.TButton", foreground="#ffffff", background=primary)
        self.ttk_style.map("Accent.TButton", background=[("active", primary)])
        self.ttk_style.configure("Nav.TButton", padding=6)
        self.active_nav = "home"

        # state
        self.last_error = None
        self.logs = []
        self.history = []  # list of dicts
        self.cache_path = os.environ.get("HF_HOME", os.path.join(os.path.expanduser("~"), ".cache", "huggingface"))

        # header
        self.header = ttk.Frame(self)
        self.header.pack(fill="x")
        title = ttk.Label(self.header, text="Tkinter AI GUI", font=("Segoe UI", 16, "bold"))
        title.pack(side="left", padx=12, pady=10)

        # nav
        self.nav = ttk.Frame(self)
        self.nav.pack(fill="x")
        self.home_btn = ttk.Button(self.nav, text="🏠 Home", style="Nav.TButton", command=lambda: self.switch_nav("home"))
        self.model_btn = ttk.Button(self.nav, text="📚 Models", style="Nav.TButton", command=lambda: self.switch_nav("model"))
        self.help_btn = ttk.Button(self.nav, text="❓ Help", style="Nav.TButton", command=lambda: self.switch_nav("help"))
        self.settings_btn = ttk.Button(self.nav, text="⚙ Settings", style="Nav.TButton", command=lambda: self.switch_nav("settings"))
        for b in (self.home_btn, self.model_btn, self.help_btn, self.settings_btn):
            b.pack(side="left", padx=6, pady=4)

        # main container
        self.container = ttk.Frame(self)
        self.container.pack(fill="both", expand=True, padx=10, pady=10)

        # expandable status bar
        self.status_container = ttk.Frame(self)
        self.status_container.pack(fill="x", side="bottom")
        self.status_bar = ttk.Frame(self.status_container)
        self.status_bar.pack(fill="x")
        self.status_label = ttk.Label(self.status_bar, text="Ready")
        self.status_label.pack(side="left", padx=8, pady=4)
        self.status_prog = ttk.Progressbar(self.status_bar, mode="determinate", length=240)
        self.status_prog.pack(side="left", padx=8)
        self.cache_label = ttk.Label(self.status_bar, text=self._cache_badge_text())
        self.cache_label.pack(side="right", padx=8)
        self.clear_cache_btn = ttk.Button(self.status_bar, text="Clear cache", command=self.clear_cache)
        self.clear_cache_btn.pack(side="right", padx=8)

        # collapsible log panel
        self.log_panel = ttk.Frame(self.status_container)
        self.log_text = tk.Text(self.log_panel, height=6, wrap="none")
        self.log_text.pack(fill="both", expand=True, padx=8, pady=4)
        self.log_controls = ttk.Frame(self.log_panel)
        self.log_controls.pack(fill="x", padx=8, pady=(0, 6))
        ttk.Button(self.log_controls, text="Clear logs", command=self.clear_logs).pack(side="right")
        ttk.Button(self.log_controls, text="Copy full log", command=self.copy_logs).pack(side="right", padx=6)
        self.log_visible = False
        self.status_bar.bind("<Button-1>", self.toggle_log_panel)

        # controller
        self.model_controller = ModelController()
        self._current_view = None
        self.switch_nav("home")


    def center_window(self):
        self.update_idletasks()
        w = self.winfo_width() or 1000
        h = self.winfo_height() or 700
        x = (self.winfo_screenwidth() // 2) - (w // 2)
        y = (self.winfo_screenheight() // 2) - (h // 2)
        self.geometry(f"{w}x{h}+{x}+{y}")


    # Navigation
    def switch_nav(self, target: str):
        self.active_nav = target
        self._apply_nav_styles()
        if target == "home":
            self.show_home()
        elif target == "model":
            self.show_model()
        elif target == "help":
            self.show_help()
        elif target == "settings":
            self.show_settings()

    def _apply_nav_styles(self):
        mapping = {
            "home": self.home_btn,
            "model": self.model_btn,
            "help": self.help_btn,
            "settings": self.settings_btn,
        }
        for key, btn in mapping.items():
            if key == self.active_nav:
                btn.configure(style="Accent.TButton")
            else:
                btn.configure(style="Nav.TButton")

    def show_home(self):
        self._clear_container()
        self._current_view = HomeView(self.container, self.model_controller, app=self)
        self._current_view.pack(fill="both", expand=True)

    def show_model(self):
        self._clear_container()
        frm = ttk.Frame(self.container, padding=12)
        frm.pack(fill="both", expand=True)
        ttk.Label(frm, text="Model Information", font=("Segoe UI", 12, "bold")).pack(anchor="w", pady=(0, 6))
        text = tk.Text(frm, height=20, wrap="word")
        text.pack(fill="both", expand=True)
        try:
            with open("app/model_info.md", "r", encoding="utf-8") as f:
                text.insert("1.0", f.read())
        except Exception as e:
            text.insert("1.0", f"Could not load model info: {e}")
        text.configure(state="disabled")
        self._current_view = frm

    def show_help(self):
        self._clear_container()
        frm = ttk.Frame(self.container, padding=12)
        frm.pack(fill="both", expand=True)
        ttk.Label(frm, text="Help", font=("Segoe UI", 12, "bold")).pack(anchor="w", pady=(0, 6))
        text = tk.Text(frm, height=22, wrap="word")
        text.pack(fill="both", expand=True)
        try:
            with open("app/help.md", "r", encoding="utf-8") as f:
                text.delete("1.0", "end")
                text.insert("1.0", f.read())
        except Exception:
            msg = (
                "If an error occurs during testing an input, it will appear here.\n"
                "Check your internet connection, requirements, or use HF Inference API."
            )
            text.insert("1.0", msg)
        if self.last_error:
            text.insert("end", f"\n\nLast error:\n{self.last_error}")
        text.configure(state="disabled")
        self._help_text = text
        self._current_view = frm

    def show_settings(self):
        self._clear_container()
        frm = ttk.Frame(self.container, padding=12)
        frm.pack(fill="both", expand=True)
        ttk.Label(frm, text="Settings", font=("Segoe UI", 12, "bold")).pack(anchor="w", pady=(0, 6))
        # HF cache
        cache_row = ttk.Frame(frm)
        cache_row.pack(fill="x", pady=6)
        ttk.Label(cache_row, text="HF Cache folder:").pack(side="left")
        self.cache_entry = ttk.Entry(cache_row, width=60)
        self.cache_entry.insert(0, self.cache_path)
        self.cache_entry.pack(side="left", padx=8)
        ttk.Button(cache_row, text="Change", command=self.choose_cache_dir).pack(side="left")

        # Buttons
        btn_row = ttk.Frame(frm)
        btn_row.pack(fill="x", pady=12)
        ttk.Button(btn_row, text="Save", style="Accent.TButton", command=self.save_settings).pack(side="left")
        ttk.Button(btn_row, text="Cancel", command=self.switch_nav_to_current).pack(side="left", padx=8)

        self._current_view = frm

    def switch_nav_to_current(self):
        # Re-render current page
        self.switch_nav(self.active_nav)

    # Status bar helpers
    def set_status(self, text: str, running: bool = False):
        self.status_label.configure(text=text, foreground=("#F87171" if text.startswith("Error") else ""))
        if running:
            self.status_prog.configure(mode="indeterminate")
            self.status_prog.start(10)
        else:
            self.status_prog.stop()
            self.status_prog.configure(mode="determinate", value=0)

    def log(self, message: str):
        ts = self._now()
        line = f"[{ts}] {message}"
        self.logs.append(line)
        if len(self.logs) > 1000:
            self.logs = self.logs[-1000:]
        if self.log_visible:
            try:
                self.log_text.configure(state="normal")
                self.log_text.insert("end", line + "\n")
                self.log_text.see("end")
                self.log_text.configure(state="disabled")
            except Exception:
                pass

    def clear_logs(self):
        self.logs.clear()
        try:
            self.log_text.configure(state="normal")
            self.log_text.delete("1.0", "end")
            self.log_text.configure(state="disabled")
        except Exception:
            pass

    def copy_logs(self):
        try:
            import pyperclip
            pyperclip.copy("\n".join(self.logs))
        except Exception:
            pass

    def toggle_log_panel(self, _e=None):
        # expand/collapse logs panel
        self.log_visible = not self.log_visible
        if self.log_visible:
            self.log_panel.pack(fill="x")
            try:
                self.log_text.configure(state="normal")
                self.log_text.delete("1.0", "end")
                self.log_text.insert("1.0", "\n".join(self.logs))
                self.log_text.configure(state="disabled")
            except Exception:
                pass
        else:
            self.log_panel.pack_forget()

    # Cache helpers
    def _cache_badge_text(self):
        size = self._folder_size(self.cache_path)
        return f"Cache: {self._format_bytes(size)}"

    def _folder_size(self, path):
        total = 0
        try:
            for root, _, files in os.walk(path):
                for f in files:
                    fp = os.path.join(root, f)
                    try:
                        total += os.path.getsize(fp)
                    except Exception:
                        pass
        except Exception:
            pass
        return total

    def _format_bytes(self, size):
        for unit in ["B", "KB", "MB", "GB", "TB"]:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} PB"

    def clear_cache(self):
        try:
            if os.path.isdir(self.cache_path):
                # delete only model hub cache within folder, not entire user profile
                for name in os.listdir(self.cache_path):
                    p = os.path.join(self.cache_path, name)
                    try:
                        if os.path.isdir(p):
                            shutil.rmtree(p, ignore_errors=True)
                        else:
                            os.remove(p)
                    except Exception:
                        pass
            self.cache_label.configure(text=self._cache_badge_text())
            self.log("Cache cleared")
        except Exception as e:
            self.log(f"Cache clear error: {e}")
            self.set_status(f"Error: {e}", running=False)

    # Settings helpers
    def choose_cache_dir(self):
        d = filedialog.askdirectory()
        if d:
            self.cache_entry.delete(0, "end")
            self.cache_entry.insert(0, d)

    def save_settings(self):
        # Save HF_HOME; user must restart shell for setx to take effect globally
        new_cache = self.cache_entry.get().strip()
        if new_cache and os.path.isdir(new_cache):
            os.environ["HF_HOME"] = new_cache
            self.cache_path = new_cache
            try:
                # best-effort persist for future sessions on Windows
                if os.name == "nt":
                    os.system(f'setx HF_HOME "{new_cache}" > NUL')
            except Exception:
                pass
            self.cache_label.configure(text=self._cache_badge_text())
            self.log(f"HF_HOME set to {new_cache}")
        self.switch_nav("home")

    def update_help_page(self):
        if hasattr(self, "_help_text") and isinstance(self._help_text, tk.Text):
            try:
                self._help_text.configure(state="normal")
                self._help_text.insert("end", f"\n\nLast error:\n{self.last_error}")
                self._help_text.configure(state="disabled")
            except Exception:
                pass

    def _now(self):
        import time
        return time.strftime("%H:%M:%S")

    def _clear_container(self):
        for w in self.container.winfo_children():
            w.destroy()
