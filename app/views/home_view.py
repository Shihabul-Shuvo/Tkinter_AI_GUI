# create the view that offers task dropdown, input widgets, Run button, and output area
import tkinter as tk
from tkinter import filedialog
from tkinter import scrolledtext
from tkinter import ttk
from PIL import Image, ImageTk
import json
import time


try:
    # optional for drag-and-drop support
    from tkinterdnd2 import DND_FILES, TkinterDnD
except Exception:
    DND_FILES = None
    TkinterDnD = None


class _ToolTip:
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tip = None
        widget.bind("<Enter>", self._show)
        widget.bind("<Leave>", self._hide)

    def _show(self, _e=None):
        if self.tip is not None:
            return
        x = self.widget.winfo_rootx() + 16
        y = self.widget.winfo_rooty() + self.widget.winfo_height() + 6
        self.tip = tk.Toplevel(self.widget)
        self.tip.wm_overrideredirect(True)
        self.tip.wm_geometry(f"+{x}+{y}")
        lbl = ttk.Label(self.tip, text=self.text, relief="solid", borderwidth=1, padding=4)
        lbl.pack()

    def _hide(self, _e=None):
        if self.tip is not None:
            self.tip.destroy()
            self.tip = None


class HomeView(ttk.Frame):
    def __init__(self, parent, controller, app=None):
        super().__init__(parent, padding=12)
        self.controller = controller
        self.app = app
        self.selected_file = None
        self.placeholder_text = "Type or paste text here — up to 3000 characters"
        self.running = False
        self.history_items = []  # list of dicts
        self._build_ui()
        # responsive
        self.bind("<Configure>", self._on_resize)

    def _card(self, master):
        frm = ttk.Frame(master, padding=12, relief="groove")
        frm.columnconfigure(0, weight=1)
        return frm

    def _build_ui(self):
        # 3 columns: Left (controls), Center (output), Right (info)
        for c in range(3):
            self.columnconfigure(c, weight=(1 if c == 1 else 0))
        self.rowconfigure(0, weight=1)

        # Left column: Controls card
        self.left_wrap = ttk.Frame(self)
        self.left_wrap.grid(row=0, column=0, sticky="nswe")
        self.left_wrap.rowconfigure(0, weight=1)
        left = self._card(self.left_wrap)
        left.pack(fill="both", expand=True)

        # Top: Task selection
        ttk.Label(left, text="Select Task").pack(anchor="w")
        self.task_var = tk.StringVar(value="Image to Text")
        self.task_menu = ttk.Combobox(left, textvariable=self.task_var, state="readonly", values=["Image to Text", "Sentiment Analysis"], width=28)
        self.task_menu.pack(fill="x", pady=(4, 8))
        self.task_menu.bind("<<ComboboxSelected>>", lambda e: self._update_info_panel())

        # Execution mode display with tooltip
        exec_row = ttk.Frame(left)
        exec_row.pack(fill="x", pady=(0, 8))
        ttk.Label(exec_row, text="Execution Mode:").pack(side="left")
        self.exec_mode_entry = ttk.Entry(exec_row, width=20)
        self.exec_mode_entry.insert(0, "Local")
        self.exec_mode_entry.configure(state="readonly")
        self.exec_mode_entry.pack(side="left", padx=6)
        _ToolTip(self.exec_mode_entry, "Local downloads model weights on first run.")

        # Dynamic input area
        self.preview_card = self._card(left)
        self.preview_card.pack(fill="x")

        # Image controls
        img_row = ttk.Frame(self.preview_card)
        img_row.pack(fill="x")
        choose_btn = ttk.Button(img_row, text="Choose Image", width=16, command=self.choose_file)
        choose_btn.pack(side="left")
        sample_img_btn = ttk.Button(img_row, text="Use Sample", command=self.use_sample_image)
        sample_img_btn.pack(side="left", padx=6)

        # Preview box with clearer 2px border
        self.preview_box = ttk.Label(self.preview_card, text="320×240 preview", relief="solid", borderwidth=2, anchor="center")
        self.preview_box.pack(fill="x", pady=8)
        self.preview_box.configure(width=42)
        self.preview_box.bind("<Button-1>", self._open_full_image)
        _ToolTip(self.preview_box, "PNG, JPG, JPEG, BMP — up to 25 MB")

        # Drag-and-drop if available + visual feedback
        if DND_FILES is not None and hasattr(self.preview_box, "drop_target_register"):
            try:
                self.preview_box.drop_target_register(DND_FILES)
                self.preview_box.dnd_bind("<<DragEnter>>", self._on_drag_enter)
                self.preview_box.dnd_bind("<<DragLeave>>", self._on_drag_leave)
                self.preview_box.dnd_bind("<<Drop>>", self._on_drop_file)
            except Exception:
                pass

        # Text controls
        ttk.Label(self.preview_card, text="Text Input").pack(anchor="w", pady=(8, 4))
        self.text_input = tk.Text(self.preview_card, height=7, wrap="word")
        self.text_input.pack(fill="x")
        self._set_placeholder()
        self.text_input.bind("<FocusIn>", self._clear_placeholder)
        self.text_input.bind("<FocusOut>", self._restore_placeholder)
        txt_row = ttk.Frame(self.preview_card)
        txt_row.pack(fill="x", pady=6)
        ttk.Button(txt_row, text="Paste from Clipboard", command=self.paste_clipboard).pack(side="left")
        ttk.Button(txt_row, text="Use Sample Text", command=self.use_sample_text).pack(side="left", padx=6)

        # Optional language selector
        lang_row = ttk.Frame(self.preview_card)
        lang_row.pack(fill="x", pady=(0, 6))
        ttk.Label(lang_row, text="Language:").pack(side="left")
        self.lang_var = tk.StringVar(value="Auto-detect")
        ttk.Combobox(lang_row, textvariable=self.lang_var, state="readonly", values=["Auto-detect", "English", "Spanish", "French", "German"], width=18).pack(side="left", padx=6)

        # Controls row
        ctrl_row = ttk.Frame(left)
        ctrl_row.pack(fill="x", pady=8)
        self.run_btn = ttk.Button(ctrl_row, text="Run", command=self.run_task, width=14)
        self.run_btn.pack(side="left")
        ttk.Button(ctrl_row, text="Clear", command=self.clear_inputs, width=10).pack(side="left", padx=8)
        self.save_history_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(ctrl_row, text="Save to history", variable=self.save_history_var).pack(side="left")
        # Small spinner near run
        self.small_prog = ttk.Progressbar(ctrl_row, mode="indeterminate", length=80)
        self.small_prog.pack(side="left", padx=8)
        self.small_prog.stop()

        # History list
        hist_card = self._card(left)
        hist_card.pack(fill="both", expand=True, pady=(8, 0))
        ttk.Label(hist_card, text="History").pack(anchor="w", pady=(0, 4))
        self.history_list = tk.Listbox(hist_card, height=10)
        self.history_list.pack(fill="both", expand=True)
        self.history_list.bind("<<ListboxSelect>>", self._open_history_item)

        # Center column: Output/Result card
        self.center_wrap = ttk.Frame(self)
        self.center_wrap.grid(row=0, column=1, sticky="nswe", padx=12)
        self.rowconfigure(0, weight=1)
        center = self._card(self.center_wrap)
        center.pack(fill="both", expand=True)
        center.columnconfigure(0, weight=1)
        center.rowconfigure(1, weight=1)
        ttk.Label(center, text="Model Output", font=("Segoe UI", 12, "bold")).grid(row=0, column=0, sticky="w")
        self.output = scrolledtext.ScrolledText(center, height=16, width=80)
        self.output.grid(row=1, column=0, sticky="nswe")
        out_row = ttk.Frame(center)
        out_row.grid(row=2, column=0, sticky="w", pady=6)
        ttk.Button(out_row, text="Copy Result", command=self.copy_result).pack(side="left")
        ttk.Button(out_row, text="Save as TXT", command=lambda: self.export_result("txt")).pack(side="left", padx=6)
        ttk.Button(out_row, text="Export as JSON", command=lambda: self.export_result("json")).pack(side="left")

        # Right column: Model Info & OOP Explanation cards
        self.right_wrap = ttk.Frame(self)
        self.right_wrap.grid(row=0, column=2, sticky="nswe")
        self.right_wrap.rowconfigure(1, weight=1)
        right_top = self._card(self.right_wrap)
        right_top.grid(row=0, column=0, sticky="nsew")
        ttk.Label(right_top, text="Model Info", font=("Segoe UI", 11, "bold")).pack(anchor="w")
        self.model_panel = scrolledtext.ScrolledText(right_top, height=12, width=40)
        self.model_panel.pack(fill="both", expand=False)
        right_bottom = self._card(self.right_wrap)
        right_bottom.grid(row=1, column=0, sticky="nsew", pady=(8, 0))
        ttk.Label(right_bottom, text="OOP concepts used", font=("Segoe UI", 11, "bold")).pack(anchor="w")
        self.info_panel = scrolledtext.ScrolledText(right_bottom, height=10, width=40)
        self.info_panel.pack(fill="both", expand=True)
        ttk.Button(right_bottom, text="Copy Panels", command=self.copy_panels).pack(anchor="e", pady=(6, 0))

        # Initialize right panels
        self._update_info_panel()

    # Responsive reflow
    def _on_resize(self, _event=None):
        w = self.winfo_width() or 1000
        compact = w < 900
        if compact:
            # stack columns
            try:
                self.left_wrap.grid_configure(row=0, column=0, padx=0, pady=(0, 8), sticky="nswe", columnspan=3)
                self.center_wrap.grid_configure(row=1, column=0, padx=0, pady=(0, 8), sticky="nswe", columnspan=3)
                self.right_wrap.grid_configure(row=2, column=0, padx=0, pady=(0, 0), sticky="nswe", columnspan=3)
                self.rowconfigure(0, weight=0)
                self.rowconfigure(1, weight=1)
                self.rowconfigure(2, weight=1)
            except Exception:
                pass
        else:
            # 3-column layout
            try:
                self.left_wrap.grid_configure(row=0, column=0, padx=0, pady=0, sticky="nswe", columnspan=1)
                self.center_wrap.grid_configure(row=0, column=1, padx=12, pady=0, sticky="nswe", columnspan=1)
                self.right_wrap.grid_configure(row=0, column=2, padx=0, pady=0, sticky="nswe", columnspan=1)
                for r in range(3):
                    self.rowconfigure(r, weight=(1 if r == 0 else 0))
            except Exception:
                pass

    # Placeholder behavior for Text
    def _set_placeholder(self):
        self.text_input.delete("1.0", "end")
        self.text_input.insert("1.0", self.placeholder_text)
        self.text_input.configure(fg="#888")

    def _clear_placeholder(self, _event=None):
        if self.text_input.get("1.0", "end").strip() == self.placeholder_text:
            self.text_input.delete("1.0", "end")
            self.text_input.configure(fg="#000")

    def _restore_placeholder(self, _event=None):
        if not self.text_input.get("1.0", "end").strip():
            self._set_placeholder()

    # Drag-and-drop handlers
    def _on_drag_enter(self, _event=None):
        try:
            self.preview_box.configure(text="➕ Drop image", foreground="#2C7BE5")
        except Exception:
            pass

    def _on_drag_leave(self, _event=None):
        try:
            if not hasattr(self, "_preview_img"):
                self.preview_box.configure(text="320×240 preview", foreground="")
            else:
                self.preview_box.configure(foreground="")
        except Exception:
            pass

    def _on_drop_file(self, event):
        if not event.data:
            return
        path = event.data.strip().strip("{}")
        try:
            pil = Image.open(path)
            self.selected_file = path
            self._set_preview(pil)
            self.preview_box.configure(foreground="")
        except Exception:
            pass

    # Utility actions
    def paste_clipboard(self):
        try:
            import pyperclip
            txt = pyperclip.paste()
            if txt:
                self.text_input.delete("1.0", "end")
                self.text_input.insert("1.0", txt)
                self.text_input.configure(fg="#000")
        except Exception:
            pass

    def use_sample_image(self):
        img = Image.new("RGB", (320, 240), color=(220, 230, 240))
        self._set_preview(img)
        self.selected_file = None

    def use_sample_text(self):
        sample = "I absolutely love this product. It exceeded my expectations!"
        self.text_input.delete("1.0", "end")
        self.text_input.insert("1.0", sample)
        self.text_input.configure(fg="#000")

    def _set_preview(self, pil_image):
        pil = pil_image.copy()
        pil.thumbnail((320, 240))
        self._preview_img = ImageTk.PhotoImage(pil)
        self.preview_box.configure(image=self._preview_img, text="")

    def _open_full_image(self, _event=None):
        if not hasattr(self, "_preview_img"):
            return
        top = tk.Toplevel(self)
        top.title("Image Preview")
        lbl = ttk.Label(top, image=self._preview_img)
        lbl.pack()

    def clear_inputs(self):
        self.selected_file = None
        self.preview_box.configure(image="", text="320×240 preview")
        self._set_placeholder()
        self.output.delete("1.0", "end")
        self.model_panel.delete("1.0", "end")
        self.info_panel.delete("1.0", "end")
        self._update_info_panel()
        self._reset_run_state()

    def choose_file(self):
        f = filedialog.askopenfilename(filetypes=[("Images", "*.png;*.jpg;*.jpeg;*.bmp")])
        if f:
            self.selected_file = f
            try:
                pil = Image.open(f)
                self._set_preview(pil)
            except Exception:
                self.preview_box.configure(text=f)

    def run_task(self):
        if self.running:
            return
        task_label = self.task_var.get()
        task = "image" if task_label.lower().startswith("image") else "sentiment"
        self.output.delete("1.0", "end")
        self._update_info_panel()
        # disable run, set status and small spinner
        self.running = True
        if self.app:
            self.app.set_status("Running…", running=True)
        self.run_btn.configure(state="disabled", text="Running…")
        try:
            self.small_prog.start(10)
        except Exception:
            pass
        if task == "image":
            if not (self.selected_file or hasattr(self, "_preview_img")):
                self._handle_error("No image selected")
                return
            image_input = self.selected_file if self.selected_file else self._image_from_preview()
            self.controller.run_image_caption(image_input, self._on_result)
        else:
            txt = self.text_input.get("1.0", "end").strip()
            if not txt or txt == self.placeholder_text:
                self._handle_error("No text entered")
                return
            self.controller.run_sentiment(txt, self._on_result)

    def _reset_run_state(self):
        self.running = False
        try:
            self.small_prog.stop()
        except Exception:
            pass
        self.run_btn.configure(state="normal", text="Run")
        if self.app:
            self.app.set_status("Ready", running=False)

    def _image_from_preview(self):
        return Image.new("RGB", (320, 240), color=(220, 230, 240))

    def _on_result(self, err, result):
        self._reset_run_state()
        if err:
            self._handle_error(str(err))
            return
        self.output.insert("end", f"{result}\n")
        # add to history
        if self.save_history_var.get():
            item = {
                "ts": time.strftime("%H:%M:%S"),
                "task": self.task_var.get(),
                "result": result,
            }
            self.history_items.append(item)
            self.history_list.insert("end", f"{item['ts']} — {item['task']}")

    def _open_history_item(self, _event=None):
        idxs = self.history_list.curselection()
        if not idxs:
            return
        idx = idxs[0]
        item = self.history_items[idx]
        self.output.delete("1.0", "end")
        self.output.insert("1.0", json.dumps(item, indent=2, default=str))

    def _handle_error(self, message):
        self.output.insert("end", f"Error: {message}\n")
        self._reset_run_state()
        if self.app is not None:
            self.app.last_error = message
            self.app.log(f"Error: {message}")
            self.app.set_status(f"Error: {message}", running=False)

    def copy_result(self):
        try:
            import pyperclip
            pyperclip.copy(self.output.get("1.0", "end"))
        except Exception:
            pass

    def export_result(self, fmt: str):
        data = self.output.get("1.0", "end").strip()
        if not data:
            return
        if fmt == "txt":
            path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text", "*.txt")])
            if path:
                with open(path, "w", encoding="utf-8") as f:
                    f.write(data)
        else:
            path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON", "*.json")])
            if path:
                try:
                    parsed = json.loads(data)
                except Exception:
                    parsed = {"result": data}
                with open(path, "w", encoding="utf-8") as f:
                    json.dump(parsed, f, ensure_ascii=False, indent=2)

    def copy_panels(self):
        txt = "Model Info:\n" + self.model_panel.get("1.0", "end") + "\nOOP:\n" + self.info_panel.get("1.0", "end")
        try:
            import pyperclip
            pyperclip.copy(txt)
        except Exception:
            pass

    def _update_info_panel(self):
        task_label = self.task_var.get()
        if task_label.lower().startswith("image"):
            model_id = "nlpconnect/vit-gpt2-image-captioning"
            model_info = (
                "Task: Image → Text (Captioning)\n"
                f"Model ID: {model_id}\n"
                "Library: Transformers pipeline(image-to-text)\n"
                "Description: ViT encoder + GPT-2 decoder for captions."
            )
            oop = (
                "Multiple inheritance: ImageCaptionWrapper + PreprocessMixin (image preprocessing).\n"
                "Decorators: @timing and @simple_cache on process().\n"
                "Encapsulation: _pipeline, _model_name; Polymorphism: process() overridden.\n"
                "Why: mixin for PIL conversion; cache identical inputs; uniform interface."
            )
        else:
            model_id = "tabularisai/multilingual-sentiment-analysis"
            model_info = (
                "Task: Sentiment Analysis\n"
                f"Model ID: {model_id}\n"
                "Library: Transformers pipeline(text-classification)\n"
                "Description: small multilingual sentiment classifier."
            )
            oop = (
                "BaseModelWrapper overridden by SentimentWrapper.process().\n"
                "Decorator: @timing measures latency; encapsulated pipeline.\n"
                "Why: consistent interface; easy extension to other text models."
            )
        self.model_panel.delete("1.0", "end")
        self.model_panel.insert("end", model_info)
        self.info_panel.delete("1.0", "end")
        self.info_panel.insert("end", oop)
