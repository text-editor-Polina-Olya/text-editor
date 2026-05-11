import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from tkinter.scrolledtext import ScrolledText


class PoLLelya(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("PoLLelya")
        self.geometry("1200x900")
        self.is_dark_theme = True
        self.filename = None
        self.last_saved_content = ""
        # current_tags хранит активные стили для БУДУЩЕГО ввода
        self.current_tags = set()
        self.set_theme_colors()
        self.setup_ui()
        self.setup_bindings()
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

    def set_theme_colors(self):
        if self.is_dark_theme:
            self.colors = {"bg": "#1a1a1e", "surface": "#252529", "accent": "#7c4dff", "text": "#e1e1e1",
                           "gray": "#626266", "border": "#333338"}
        else:
            self.colors = {"bg": "#f0f0f0", "surface": "#ffffff", "accent": "#7c4dff", "text": "#1a1a1e",
                           "gray": "#a0a0a0", "border": "#cccccc"}

    def setup_ui(self):
        # 1. Запоминаем данные, если редактор уже существовал
        saved_data = None
        current_font = "Times New Roman"
        current_size = "14"

        if hasattr(self, 'editor'):
            saved_data = self.editor.dump("1.0", "end-1c", tag=True, text=True)
            current_font = self.font_combo.get()
            current_size = self.size_combo.get()
            for widget in self.winfo_children():
                widget.destroy()

        self.configure(bg=self.colors["bg"])

        # Сайдбар
        self.sidebar = tk.Frame(self, bg=self.colors["surface"], width=70)
        self.sidebar.pack(side=tk.LEFT, fill=tk.Y)

        for icon, cmd in [("📄", self.new_file), ("💾", self.save_file), ("📂", self.open_file), ("🌗", self.toggle_theme)]:
            btn = tk.Label(self.sidebar, text=icon, bg=self.colors["surface"], fg=self.colors["gray"],
                           font=("Segoe UI Symbol", 20), pady=15, cursor="hand2")
            btn.pack(fill=tk.X)
            btn.bind("<Button-1>", lambda e, c=cmd: c())

        right_side = tk.Frame(self, bg=self.colors["bg"])
        right_side.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Тулбар
        toolbar_container = tk.Frame(right_side, bg=self.colors["bg"], pady=20, padx=40)
        toolbar_container.pack(fill=tk.X)
        self.toolbar = tk.Frame(toolbar_container, bg=self.colors["surface"], padx=15, pady=8)
        self.toolbar.pack(fill=tk.X)

        self.font_combo = ttk.Combobox(self.toolbar, values=["Times New Roman", "Arial", "Courier New", "Consolas"],
                                       width=15, state="readonly")
        self.font_combo.set(current_font)
        self.font_combo.pack(side=tk.LEFT, padx=10)
        self.font_combo.bind("<<ComboboxSelected>>", lambda e: self.on_style_change())

        self.size_combo = ttk.Combobox(self.toolbar, values=[8, 9, 10, 11, 12, 14, 16, 18, 20, 24, 30, 36, 48, 60, 72],
                                       width=5)
        self.size_combo.set(current_size)
        self.size_combo.pack(side=tk.LEFT, padx=10)
        self.size_combo.bind("<<ComboboxSelected>>", lambda e: self.on_style_change())

        self.btns = {}
        for label, tag in [("B", "bold"), ("I", "italic"), ("U", "underline")]:
            btn = tk.Button(self.toolbar, text=label, relief="flat", bd=0, font=("Segoe UI", 11), width=3,
                            command=lambda t=tag: self.toggle_tag(t))
            btn.pack(side=tk.LEFT, padx=2)
            self.btns[tag] = btn

        # Цвета
        colors_preset = ["#e1e1e1" if self.is_dark_theme else "#1a1a1e", "#ff4f4f", "#4fff7c", "#4f7cff", "#ffcf4f"]
        for c in colors_preset:
            btn = tk.Frame(self.toolbar, bg=c, width=20, height=20, cursor="hand2", highlightthickness=1,
                           highlightbackground=self.colors["border"])
            btn.pack(side=tk.LEFT, padx=3)
            btn.bind("<Button-1>", lambda e, color=c: self.change_color(color))

        # Редактор
        self.editor = ScrolledText(right_side, bg=self.colors["surface"], fg=self.colors["text"],
                                   font=(current_font, int(current_size)),
                                   bd=0, padx=40, pady=40, insertbackground=self.colors["accent"], undo=True)
        self.editor.pack(fill=tk.BOTH, expand=True, padx=40, pady=(0, 40))

        # 2. Восстанавливаем контент и визуальное состояние кнопок
        if saved_data:
            self.restore_content(saved_data)

        self.update_btn_ui()
        self.editor.focus_set()

    def restore_content(self, data):
        self.editor.delete("1.0", tk.END)
        # Сначала настраиваем стандартные теги
        self.editor.tag_configure("underline", underline=True)

        for type, value, index in data:
            if type == "text":
                self.editor.insert(index, value)
            elif type == "tagon" and value not in ["sel", "insert"]:
                # Восстанавливаем конфигурацию тега на лету
                if value.startswith("f_"):
                    parts = value.split("_")
                    if len(parts) >= 5:
                        f_name = parts[1].replace("-", " ")
                        f_weight, f_slant, f_size = parts[2], parts[3], parts[4]
                        self.editor.tag_configure(value, font=(f_name, int(f_size), f_weight, f_slant))
                elif value.startswith("fg_"):
                    color = value.split("_")[1]
                    self.editor.tag_configure(value, foreground=color)

                self.editor.tag_add(value, index)

    def get_current_settings(self):
        f_name = self.font_combo.get()
        f_size = self.size_combo.get() if self.size_combo.get().isdigit() else "14"
        weight = "bold" if "bold" in self.current_tags else "normal"
        slant = "italic" if "italic" in self.current_tags else "roman"
        return f_name, f_size, weight, slant

    def on_style_change(self):
        f_name, f_size, weight, slant = self.get_current_settings()
        try:
            s, e = self.editor.index("sel.first"), self.editor.index("sel.last")
            self.apply_font_style(s, e, f_name, f_size, weight, slant)
        except tk.TclError:
            pass
        self.editor.focus_set()

    def toggle_tag(self, tag):
        try:
            s, e = self.editor.index("sel.first"), self.editor.index("sel.last")
            if tag == "underline":
                if tag in self.editor.tag_names(s):
                    self.editor.tag_remove(tag, s, e)
                else:
                    self.editor.tag_add(tag, s, e)
            else:
                tags = self.editor.tag_names(s)
                is_b = any("bold" in t for t in tags if t.startswith("f_"))
                is_i = any("italic" in t for t in tags if t.startswith("f_"))

                new_b = (not is_b) if tag == "bold" else is_b
                new_i = (not is_i) if tag == "italic" else is_i

                f_name, f_size, _, _ = self.get_current_settings()
                self.apply_font_style(s, e, f_name, f_size, "bold" if new_b else "normal",
                                      "italic" if new_i else "roman")
        except tk.TclError:
            if tag in self.current_tags:
                self.current_tags.remove(tag)
            else:
                self.current_tags.add(tag)
            self.update_btn_ui()
        self.editor.focus_set()

    def update_btn_ui(self):
        for tag, btn in self.btns.items():
            active = tag in self.current_tags
            btn.config(
                bg=self.colors["accent"] if active else self.colors["surface"],
                fg="white" if active else self.colors["text"]
            )

    def apply_font_style(self, start, end, name, size, weight, slant):
        tag_name = f"f_{name.replace(' ', '-')}_{weight}_{slant}_{size}"
        self.editor.tag_configure(tag_name, font=(name, int(size), weight, slant))
        for t in self.editor.tag_names(start):
            if t.startswith("f_"):
                self.editor.tag_remove(t, start, end)
        self.editor.tag_add(tag_name, start, end)

    def change_color(self, color):
        tag_name = f"fg_{color}"
        self.editor.tag_configure(tag_name, foreground=color)
        try:
            s, e = self.editor.index("sel.first"), self.editor.index("sel.last")
            for t in self.editor.tag_names(s):
                if t.startswith("fg_"): self.editor.tag_remove(t, s, e)
            self.editor.tag_add(tag_name, s, e)
        except tk.TclError:
            self.current_tags = {t for t in self.current_tags if not t.startswith("fg_")}
            self.current_tags.add(tag_name)
        self.editor.focus_set()

    def handle_keypress(self, event):
        if event.char and ord(event.char) > 31:
            self.editor.insert(tk.INSERT, event.char)
            idx = self.editor.index("insert-1c")

            f_name, f_size, weight, slant = self.get_current_settings()
            tag_name = f"f_{f_name.replace(' ', '-')}_{weight}_{slant}_{f_size}"
            self.editor.tag_configure(tag_name, font=(f_name, int(f_size), weight, slant))
            self.editor.tag_add(tag_name, idx)

            if "underline" in self.current_tags:
                self.editor.tag_add("underline", idx)
            for t in self.current_tags:
                if t.startswith("fg_"):
                    self.editor.tag_add(t, idx)
            return "break"

    def setup_bindings(self):
        self.bind("<Control-b>", lambda e: self.toggle_tag("bold"))
        self.bind("<Control-i>", lambda e: self.toggle_tag("italic"))
        self.bind("<Control-u>", lambda e: self.toggle_tag("underline"))
        self.editor.bind("<KeyPress>", self.handle_keypress)

    def toggle_theme(self):
        self.is_dark_theme = not self.is_dark_theme
        self.set_theme_colors()
        self.setup_ui()
        self.setup_bindings()

    def is_modified(self):
        return self.editor.get("1.0", tk.END).strip() != self.last_saved_content.strip()

    def new_file(self):
        if self.is_modified() and messagebox.askyesno("Сохранение", "Сохранить изменения?"):
            self.save_file()
        self.editor.delete("1.0", tk.END)
        self.last_saved_content = ""
        self.filename = None

    def save_file(self):
        if not self.filename:
            self.filename = filedialog.asksaveasfilename(defaultextension=".txt")
        if self.filename:
            with open(self.filename, "w", encoding="utf-8") as f:
                c = self.editor.get("1.0", tk.END)
                f.write(c)
                self.last_saved_content = c.strip()

    def on_closing(self):
        if self.is_modified():
            ans = messagebox.askyesnocancel("Выход", "Сохранить изменения?")
            if ans is True:
                self.save_file()
                self.destroy()
            elif ans is False:
                self.destroy()
        else:
            self.destroy()

    def open_file(self):
        p = filedialog.askopenfilename()
        if p:
            with open(p, "r", encoding="utf-8") as f:
                c = f.read()
                self.editor.delete("1.0", tk.END)
                self.editor.insert("1.0", c)
                self.filename = p
                self.last_saved_content = c.strip()


if __name__ == "__main__":
    PoLLelya().mainloop()
