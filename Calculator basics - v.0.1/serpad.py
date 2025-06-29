import tkinter as tk
from tkinter import filedialog, messagebox

# -------------------- Core Functionality --------------------

class CodeEditor:
    def __init__(self, root):
        self.root = root
        self.root.title("SerPad")
        self.root.geometry("1300x600")

        self.file_path = None

        # Text Widget
        self.text_area = tk.Text(self.root, font=("Courier New", 12), undo=True, wrap="none")
        self.text_area.pack(fill=tk.BOTH, expand=1)

        # Scrollbars
        self.scroll_y = tk.Scrollbar(self.text_area, orient=tk.VERTICAL, command=self.text_area.yview)
        self.text_area.configure(yscrollcommand=self.scroll_y.set)
        self.scroll_y.pack(side=tk.RIGHT, fill=tk.Y)

        self.scroll_x = tk.Scrollbar(self.text_area, orient=tk.HORIZONTAL, command=self.text_area.xview)
        self.text_area.configure(xscrollcommand=self.scroll_x.set)
        self.scroll_x.pack(side=tk.BOTTOM, fill=tk.X)

        # Menu
        self.menu = tk.Menu(self.root)
        self.root.config(menu=self.menu)

        file_menu = tk.Menu(self.menu, tearoff=0)
        file_menu.add_command(label="Open", command=self.open_file)
        file_menu.add_command(label="Save", command=self.save_file)
        file_menu.add_command(label="Save As...", command=self.save_as_file)
        file_menu.add_separator()
        file_menu.add_command(label="Quit", command=self.quit_editor)
        self.menu.add_cascade(label="File", menu=file_menu)

    # -------------------- File Operations --------------------

    def open_file(self):
        path = filedialog.askopenfilename(
            filetypes=[("Text Files", "*.txt"), ("Python Files", "*.py"), ("All Files", "*.*")]
        )
        if path:
            try:
                with open(path, 'r', encoding="utf-8") as file:
                    content = file.read()
                    self.text_area.delete(1.0, tk.END)
                    self.text_area.insert(tk.END, content)
                    self.file_path = path
                    self.root.title(f"MiniCodePad - {path}")
            except Exception as e:
                messagebox.showerror("Error", f"Cannot open file:\n{e}")

    def save_file(self):
        if self.file_path:
            try:
                with open(self.file_path, 'w', encoding="utf-8") as file:
                    file.write(self.text_area.get(1.0, tk.END))
                messagebox.showinfo("Saved", "File saved successfully.")
            except Exception as e:
                messagebox.showerror("Error", f"Cannot save file:\n{e}")
        else:
            self.save_as_file()

    def save_as_file(self):
        path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text Files", "*.txt"), ("Python Files", "*.py"), ("All Files", "*.*")]
        )
        if path:
            try:
                with open(path, 'w', encoding="utf-8") as file:
                    file.write(self.text_area.get(1.0, tk.END))
                    self.file_path = path
                    self.root.title(f"MiniCodePad - {path}")
                messagebox.showinfo("Saved", "File saved successfully.")
            except Exception as e:
                messagebox.showerror("Error", f"Cannot save file:\n{e}")

    def quit_editor(self):
        if messagebox.askokcancel("Quit", "Are you sure you want to quit?"):
            self.root.destroy()

# -------------------- App Launch --------------------

if __name__ == "__main__":
    root = tk.Tk()
    app = CodeEditor(root)
    root.mainloop()
