import tkinter as tk
from tkinter import filedialog, messagebox
import pygments.lexers
from chlorophyll import CodeView

APP_NAME = "MiniCodePad Pro"

class ProEditor:
    def __init__(self, root):
        self.root = root
        root.title(APP_NAME)
        root.geometry("900x650")

        self.editor = CodeView(root, lexer=pygments.lexers.PythonLexer,
                               color_scheme="monokai", tab_width=4,
                               autohide_scrollbar=False)
        self.editor.pack(fill="both", expand=True)

        # Menu
        menu = tk.Menu(root)
        root.config(menu=menu)
        file_menu = tk.Menu(menu, tearoff=0)
        menu.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Open...", command=self.open_file)
        file_menu.add_command(label="Save", command=self.save_file)
        file_menu.add_command(label="Save As...", command=self.save_as)
        file_menu.add_separator()
        file_menu.add_command(label="Quit", command=self.quit)
        help_menu = tk.Menu(menu, tearoff=0)
        menu.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self.show_about)

        self.file_path = None

    def open_file(self):
        path = filedialog.askopenfilename(filetypes=[("All Files", "*.*")])
        if path:
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    text = f.read()
                self.editor.delete("1.0", tk.END)
                self.editor.insert("1.0", text)
                self.file_path = path
                self.root.title(f"{APP_NAME} — {path}")
            except Exception as e:
                messagebox.showerror("Error", f"Could not open file:\n{e}")

    def save_file(self):
        if self.file_path:
            self._write(self.file_path)
        else:
            self.save_as()

    def save_as(self):
        path = filedialog.asksaveasfilename(defaultextension=".py",
                                            filetypes=[("Python Files", "*.py"),
                                                       ("Text Files", "*.txt"),
                                                       ("All Files", "*.*")])
        if path:
            self._write(path)
            self.file_path = path
            self.root.title(f"{APP_NAME} — {path}")

    def _write(self, path):
        try:
            content = self.editor.get("1.0", tk.END)
            with open(path, 'w', encoding='utf-8') as f:
                f.write(content)
            messagebox.showinfo("Saved", f"Saved to {path}")
        except Exception as e:
            messagebox.showerror("Error", f"Could not save file:\n{e}")

    def show_about(self):
        messagebox.showinfo("About", f"{APP_NAME}\n\nA simple code editor with syntax highlighting.\n(c) 2025 by YourName")

    def quit(self):
        if messagebox.askokcancel("Quit", "Exit the editor?"):
            self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = ProEditor(root)
    root.mainloop()
