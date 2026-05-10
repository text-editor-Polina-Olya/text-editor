import tkinter as tk
            command=self.text_area.edit_undo
        )
        edit_menu.add_command(
            label="Redo",
            command=self.text_area.edit_redo
        )

        menu_bar.add_cascade(label="Edit", menu=edit_menu)

        self.root.config(menu=menu_bar)

    def bind_shortcuts(self):
        self.root.bind("<Control-n>", lambda event: self.new_file())
        self.root.bind("<Control-o>", lambda event: self.open_file())
        self.root.bind("<Control-s>", lambda event: self.save_file())

    def new_file(self):
        self.text_area.delete(1.0, tk.END)
        self.file_path = None
        self.root.title("New File - Python Text Editor")

    def open_file(self):
        path = filedialog.askopenfilename(
            filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")]
        )

        if not path:
            return

        try:
            with open(path, "r", encoding="utf-8") as file:
                content = file.read()

            self.text_area.delete(1.0, tk.END)
            self.text_area.insert(tk.END, content)

            self.file_path = path
            self.root.title(f"{path} - Python Text Editor")

        except Exception as e:
            messagebox.showerror("Error", str(e))

    def save_file(self):
        if self.file_path:
            try:
                with open(self.file_path, "w", encoding="utf-8") as file:
                    file.write(self.text_area.get(1.0, tk.END))

                messagebox.showinfo("Saved", "File saved successfully")

            except Exception as e:
                messagebox.showerror("Error", str(e))
        else:
            self.save_as()

    def save_as(self):
        path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")]
        )

        if not path:
            return

        self.file_path = path
        self.save_file()


if __name__ == "__main__":
    root = tk.Tk()
    app = TextEditor(root)
    root.mainloop()
