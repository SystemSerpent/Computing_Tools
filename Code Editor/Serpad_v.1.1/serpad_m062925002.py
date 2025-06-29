import tkinter as tk
from tkinter import ttk, filedialog, font, messagebox
from chlorophyll import CodeView
from pygments.lexers import guess_lexer_for_filename, get_lexer_by_name
import os

class EditorTab:
    def __init__(self, parent, file_path=None, theme="light", font_family="Consolas", font_size=12):
        self.frame = ttk.Frame(parent)
        self.file_path = file_path
        self.lexer = get_lexer_by_name("text")

        if file_path:
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
                self.lexer = guess_lexer_for_filename(file_path, content)
            except:
                content = ""
        else:
            content = ""

        self.codeview = CodeView(self.frame,
                                 lexer=self.lexer,
                                 color_scheme="monokai" if theme == "dark" else "solarized_light",
                                 font=(font_family, font_size))
        self.codeview.insert("1.0", content)
        self.codeview.pack(fill="both", expand=True)

    def get_content(self):
        return self.codeview.get("1.0", "end-1c")

    def set_font(self, family, size):
        self.codeview.configure(font=(family, size))

    def set_theme(self, theme):
        scheme = "monokai" if theme == "dark" else "solarized_light"
        self.codeview.set_color_scheme(scheme)


class Serpad:
    def __init__(self, root):
        self.root = root
        self.root.title("Serpad")
        self.root.geometry("900x600")

        self.tabs = []
        self.font_family = "Consolas"
        self.font_size = 12
        self.theme = "light"

        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill="both", expand=True)

        self.status = ttk.Label(root, text="Ready", anchor="w")
        self.status.pack(side="bottom", fill="x")

        self.build_menu()
        self.add_tab()

    def build_menu(self):
        menu = tk.Menu(self.root)
        self.root.config(menu=menu)

        file_menu = tk.Menu(menu, tearoff=0)
        file_menu.add_command(label="New", command=self.add_tab)
        file_menu.add_command(label="Open", command=self.open_file)
        file_menu.add_command(label="Save", command=self.save_file)
        file_menu.add_command(label="Save As", command=self.save_file_as)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        menu.add_cascade(label="File", menu=file_menu)

        edit_menu = tk.Menu(menu, tearoff=0)
        edit_menu.add_command(label="Find/Replace", command=self.find_replace)
        edit_menu.add_command(label="Change Font...", command=self.change_font)
        menu.add_cascade(label="Edit", menu=edit_menu)

        view_menu = tk.Menu(menu, tearoff=0)
        view_menu.add_command(label="Toggle Theme", command=self.toggle_theme)
        menu.add_cascade(label="View", menu=view_menu)

    def add_tab(self, file_path=None):
        tab = EditorTab(self.notebook, file_path, self.theme, self.font_family, self.font_size)
        self.tabs.append(tab)
        name = os.path.basename(file_path) if file_path else "Untitled"
        self.notebook.add(tab.frame, text=name)
        self.notebook.select(tab.frame)
        self.status.config(text=f"Opened: {name}")

    def current_tab(self):
        selected = self.notebook.select()
        for tab in self.tabs:
            if str(tab.frame) == selected:
                return tab
        return None

    def open_file(self):
        path = filedialog.askopenfilename()
        if path:
            self.add_tab(path)

    def save_file(self):
        tab = self.current_tab()
        if tab and tab.file_path:
            try:
                with open(tab.file_path, "w", encoding="utf-8") as f:
                    f.write(tab.get_content())
                self.status.config(text=f"Saved: {tab.file_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Could not save file:\n{e}")
        else:
            self.save_file_as()

    def save_file_as(self):
        tab = self.current_tab()
        if tab:
            path = filedialog.asksaveasfilename(defaultextension=".txt")
            if path:
                try:
                    with open(path, "w", encoding="utf-8") as f:
                        f.write(tab.get_content())
                    tab.file_path = path
                    idx = self.notebook.index(tab.frame)
                    self.notebook.tab(idx, text=os.path.basename(path))
                    self.status.config(text=f"Saved as: {path}")
                except Exception as e:
                    messagebox.showerror("Error", f"Could not save file:\n{e}")

    def change_font(self):
        win = tk.Toplevel(self.root)
        win.title("Change Font")
        win.geometry("300x100")

        tk.Label(win, text="Font Family:").pack()
        fam_var = tk.StringVar(value=self.font_family)
        fam_menu = ttk.Combobox(win, textvariable=fam_var, values=sorted(font.families()), state="readonly")
        fam_menu.pack()

        tk.Label(win, text="Font Size:").pack()
        size_var = tk.IntVar(value=self.font_size)
        size_spin = ttk.Spinbox(win, from_=6, to=48, textvariable=size_var)
        size_spin.pack()

        def apply_font():
            self.font_family = fam_var.get()
            self.font_size = size_var.get()
            for tab in self.tabs:
                tab.set_font(self.font_family, self.font_size)
            win.destroy()

        ttk.Button(win, text="Apply", command=apply_font).pack(pady=5)

    def toggle_theme(self):
        self.theme = "dark" if self.theme == "light" else "light"
        for tab in self.tabs:
            tab.set_theme(self.theme)
        self.status.config(text=f"Theme changed to {self.theme.capitalize()}")

    def find_replace(self):
        tab = self.current_tab()
        if not tab:
            return

        win = tk.Toplevel(self.root)
        win.title("Find and Replace")
        win.geometry("300x120")

        tk.Label(win, text="Find:").pack()
        find_var = tk.StringVar()
        find_entry = tk.Entry(win, textvariable=find_var)
        find_entry.pack()

        tk.Label(win, text="Replace:").pack()
        replace_var = tk.StringVar()
        replace_entry = tk.Entry(win, textvariable=replace_var)
        replace_entry.pack()

        def do_replace():
            content = tab.codeview.get("1.0", "end-1c")
            new_content = content.replace(find_var.get(), replace_var.get())
            tab.codeview.delete("1.0", "end")
            tab.codeview.insert("1.0", new_content)
            win.destroy()

        ttk.Button(win, text="Replace All", command=do_replace).pack(pady=5)

def main():
    root = tk.Tk()
    Serpad(root)
    root.mainloop()

if __name__ == "__main__":
    main()
