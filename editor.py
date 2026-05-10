import tkinter as tk
from tkinter import filedialog
from tkinter.scrolledtext import ScrolledText


class NovaWrite(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("PoLLelya")
        self.geometry("1150x850")
        self.configure(bg="#1a1a1e")

        self.colors = {
            "bg": "#1a1a1e",
            "surface": "#252529",
            "accent": "#7c4dff",
            "text": "#e1e1e1",
            "gray": "#626266",
            "border": "#333338"
        }

        self.current_tags = set()
        self.setup_ui()
        self.setup_tags()
        self.setup_bindings()

    def setup_ui(self):
        self.sidebar = tk.Frame(self, bg=self.colors["surface"], width=70)
        self.sidebar.pack(side=tk.LEFT, fill=tk.Y)

        for icon, cmd in [("📄", self.new_file), ("💾", self.save_file), ("📂", self.open_file)]:
            btn = tk.Label(self.sidebar, text=icon, bg=self.colors["surface"], fg=self.colors["gray"],
                           font=("Segoe UI Symbol", 20), pady=15, cursor="hand2")
            btn.pack(fill=tk.X)
            btn.bind("<Button-1>", lambda e, c=cmd: c())
            btn.bind("<Enter>", lambda e, b=btn: b.config(fg=self.colors["accent"]))
            btn.bind("<Leave>", lambda e, b=btn: b.config(fg=self.colors["gray"]))

        right_side = tk.Frame(self, bg=self.colors["bg"])
        right_side.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        toolbar_container = tk.Frame(right_side, bg=self.colors["bg"], pady=20, padx=40)
        toolbar_container.pack(fill=tk.X)

        self.toolbar = tk.Frame(toolbar_container, bg=self.colors["surface"], padx=15, pady=8)
        self.toolbar.pack(fill=tk.X)

        self.btns = {}
        for label, tag in [("B", "bold"), ("I", "italic"), ("U", "underline")]:
            btn = tk.Button(self.toolbar, text=label, bg=self.colors["surface"], fg=self.colors["text"],
                            activebackground=self.colors["accent"], relief="flat", bd=0,
                            font=("Segoe UI", 11, "bold" if label == "B" else "normal"),
                            width=3, command=lambda t=tag: self.toggle_tag(t))
            btn.pack(side=tk.LEFT, padx=2)
            self.btns[tag] = btn

        tk.Frame(self.toolbar, width=2, bg=self.colors["border"]).pack(side=tk.LEFT, fill=tk.Y, padx=12, pady=5)

        # Убрали justify, оставили 3 рабочих режима
        for icon, mode in [("⇤", "left"), ("↔", "center"), ("⇥", "right")]:
            btn = tk.Button(self.toolbar, text=icon, bg=self.colors["surface"], fg=self.colors["gray"],
                            activebackground=self.colors["accent"], relief="flat", bd=0,
                            font=("Segoe UI", 12, "bold"), width=3,
                            command=lambda m=mode: self.set_alignment(m))
            btn.pack(side=tk.LEFT, padx=2)
            btn.bind("<Enter>", lambda e, b=btn: b.config(fg=self.colors["text"]))
            btn.bind("<Leave>", lambda e, b=btn: b.config(fg=self.colors["gray"]))

        self.editor = ScrolledText(
            right_side, bg=self.colors["surface"], fg=self.colors["text"],
            font=("Consolas", 14), bd=0, padx=40, pady=40,
            insertbackground=self.colors["accent"], undo=True, autoseparators=True
        )
        self.editor.pack(fill=tk.BOTH, expand=True, padx=40, pady=(0, 40))
        self.editor.focus_set()

    def setup_tags(self):
        self.editor.tag_configure("bold", font=("Consolas", 14, "bold"))
        self.editor.tag_configure("italic", font=("Consolas", 14, "italic"))
        self.editor.tag_configure("underline", underline=True)

        for align in ["left", "center", "right"]:
            self.editor.tag_configure(align, justify=align)

    def setup_bindings(self):
        self.bind("<Control-b>", lambda e: self.toggle_tag("bold"))
        self.bind("<Control-i>", lambda e: self.toggle_tag("italic"))
        self.bind("<Control-u>", lambda e: self.toggle_tag("underline"))
        self.editor.bind("<Control-a>", self.select_all)
        self.editor.bind("<Control-A>", self.select_all)
        self.editor.bind("<Key>", self.apply_active_tags)

    def toggle_tag(self, tag):
        try:
            sel_start, sel_end = self.editor.index("sel.first"), self.editor.index("sel.last")
            if tag in self.editor.tag_names(sel_start):
                self.editor.tag_remove(tag, sel_start, sel_end)
            else:
                self.editor.tag_add(tag, sel_start, sel_end)
        except tk.TclError:
            if tag in self.current_tags:
                self.current_tags.remove(tag)
                self.btns[tag].config(fg=self.colors["text"], bg=self.colors["surface"])
            else:
                self.current_tags.add(tag)
                self.btns[tag].config(fg="white", bg=self.colors["accent"])

    def set_alignment(self, mode):
        try:
            start, end = self.editor.index("sel.first"), self.editor.index("sel.last")
        except tk.TclError:
            start, end = "insert linestart", "insert lineend"

        for m in ["left", "center", "right"]:
            self.editor.tag_remove(m, start, end)

        self.editor.tag_add(mode, start, end)

    def apply_active_tags(self, event):
        if event.char and ord(event.char) > 31:
            def late_apply():
                idx = self.editor.index("insert-1c")
                for tag in self.current_tags:
                    self.editor.tag_add(tag, idx)

            self.after(10, late_apply)

    def select_all(self, event=None):
        self.editor.tag_add("sel", "1.0", "end")
        return "break"

    def new_file(self):
        self.editor.delete("1.0", tk.END)

    def open_file(self):
        path = filedialog.askopenfilename()
        if path:
            with open(path, "r", encoding="utf-8") as f:
                self.editor.delete("1.0", tk.END)
                self.editor.insert("1.0", f.read())

    def save_file(self):
        path = filedialog.asksaveasfilename(defaultextension=".txt")
        if path:
            with open(path, "w", encoding="utf-8") as f:
                f.write(self.editor.get("1.0", tk.END))


if __name__ == "__main__":
    app = NovaWrite()
    app.mainloop()
