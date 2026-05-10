import tkinter as tk
from tkinter import filedialog, messagebox
from file_manager import save_file, open_file


class TextEditor:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Text Editor")
        self.root.geometry("900x600")

        self.current_file = None

        self.text_area = tk.Text(
            self.root,
            wrap="word",
            font=("Arial", 14)
        )

        self.text_area.pack(expand=True, fill="both")

        self.create_menu()

    def create_menu(self):
        menu_bar = tk.Menu(self.root)

        file_menu = tk.Menu(menu_bar, tearoff=0)

        file_menu.add_command(label="New", command=self.new_file)
        file_menu.add_command(label="Open", command=self.open_file)
        file_menu.add_command(label="Save", command=self.save_file)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)

        menu_bar.add_cascade(label="File", menu=file_menu)

        self.root.config(menu=menu_bar)

    def new_file(self):
        self.text_area.delete(1.0, tk.END)
        self.current_file = None
        self.root.title("Text Editor - New File")

    def open_file(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")]
        )

        if file_path:
            content = open_file(file_path)

            self.text_area.delete(1.0, tk.END)
            self.text_area.insert(tk.END, content)

            self.current_file = file_path
            self.root.title(f"Text Editor - {file_path}")

    def save_file(self):
        if not self.current_file:
            self.current_file = filedialog.asksaveasfilename(
                defaultextension=".txt",
                filetypes=[("Text Files", "*.txt")]
            )

        if self.current_file:
            content = self.text_area.get(1.0, tk.END)

            save_file(self.current_file, content)

            messagebox.showinfo("Saved", "File saved successfully")

    def run(self):
        self.root.mainloop()
