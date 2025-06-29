import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog, colorchooser, font
import pygments.lexers
from chlorophyll import CodeView
import os
import json

APP_NAME = "MiniCodePad Pro"
CONFIG_FILE = os.path.join(os.path.expanduser("~"), ".minicodepad_pro_config.json")
AUTOSAVE_INTERVAL = 300000  # 5 minutes

DEFAULT_PREFS = {
    "font_family": "Consolas",
    "font_size": 12,
    "bg_color_light": "#FFFFFF",
    "fg_color_light": "#000000",
    "bg_color_dark": "#272822",
    "fg_color_dark": "#F8F8F2",
    "theme": "light"
}

class EditorTab:
    def __init__(self, parent, file_path=None, content="", prefs=None):
        self.file_path = file_path
        self.prefs = prefs or DEFAULT_PREFS
        self.parent = parent
        self.frame = ttk.Frame(parent)
        self.lexer = pygments.lexers.PythonLexer

        self.codeview = CodeView(self.frame, lexer=self.lexer,
                                 color_scheme="monokai" if self.prefs["theme"]=="dark" else "default",
                                 autohide_scrollbar=False,
                                 font=(self.prefs["font_family"], self.prefs["font_size"]),
                                 bg=self.prefs["bg_color_dark"] if self.prefs["theme"]=="dark" else self.prefs["bg_color_light"],
                                 fg=self.prefs["fg_color_dark"] if self.prefs["theme"]=="dark" else self.prefs["fg_color_light"],
                                 )
        self.codeview.pack(fill="both", expand=True)
        self.codeview.insert("1.0", content)
        self.codeview.edit_modified(False)

    def get_content(self):
        return self.codeview.get("1.0", tk.END)

    def set_content(self, content):
        self.codeview.delete("1.0", tk.END)
        self.codeview.insert("1.0", content)
        self.codeview.edit_modified(False)

    def set_font(self, family, size):
        self.codeview.config(font=(family, size))

    def set_colors(self, bg, fg, theme):
        self.codeview.config(bg=bg, fg=fg)
        if theme == "dark":
            self.codeview.color_scheme = "monokai"
        else:
            self.codeview.color_scheme = "default"
        self.codeview.highlight_all()

    def is_modified(self):
        return self.codeview.edit_modified()

    def reset_modified(self):
        self.codeview.edit_modified(False)

class MiniCodePadPro:
    def __init__(self, root):
        self.root = root
        self.root.title(APP_NAME)
        self.root.geometry("1000x700")
        self.prefs = self.load_prefs()

        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill="both", expand=True)
        self.tabs = []

        self.create_menu()
        self.create_statusbar()

        # Add initial empty tab
        self.add_tab()

        # Bind tab change to update status
        self.notebook.bind("<<NotebookTabChanged>>", self.update_status)

        # Auto save timer
        self.root.after(AUTOSAVE_INTERVAL, self.auto_save_all)

    def load_prefs(self):
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                    prefs = json.load(f)
                return {**DEFAULT_PREFS, **prefs}
            except Exception:
                return DEFAULT_PREFS.copy()
        else:
            return DEFAULT_PREFS.copy()

    def save_prefs(self):
        try:
            with open(CONFIG_FILE, "w", encoding="utf-8") as f:
                json.dump(self.prefs, f, indent=4)
        except Exception as e:
            messagebox.showerror("Error", f"Could not save preferences:\n{e}")

    def create_menu(self):
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        # File Menu
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="New Tab", accelerator="Ctrl+N", command=self.add_tab)
        file_menu.add_command(label="Open...", accelerator="Ctrl+O", command=self.open_file)
        file_menu.add_command(label="Save", accelerator="Ctrl+S", command=self.save_file)
        file_menu.add_command(label="Save As...", accelerator="Ctrl+Shift+S", command=self.save_file_as)
        file_menu.add_separator()
        file_menu.add_command(label="Close Tab", accelerator="Ctrl+W", command=self.close_tab)
        file_menu.add_separator()
        file_menu.add_command(label="Quit", accelerator="Ctrl+Q", command=self.quit)
        menubar.add_cascade(label="File", menu=file_menu)

        # Edit Menu
        edit_menu = tk.Menu(menubar, tearoff=0)
        edit_menu.add_command(label="Undo", accelerator="Ctrl+Z", command=self.edit_undo)
        edit_menu.add_command(label="Redo", accelerator="Ctrl+Y", command=self.edit_redo)
        edit_menu.add_separator()
        edit_menu.add_command(label="Cut", accelerator="Ctrl+X", command=self.edit_cut)
        edit_menu.add_command(label="Copy", accelerator="Ctrl+C", command=self.edit_copy)
        edit_menu.add_command(label="Paste", accelerator="Ctrl+V", command=self.edit_paste)
        edit_menu.add_separator()
        edit_menu.add_command(label="Find/Replace", accelerator="Ctrl+F", command=self.find_replace)
        menubar.add_cascade(label="Edit", menu=edit_menu)

        # View Menu
        view_menu = tk.Menu(menubar, tearoff=0)
        view_menu.add_command(label="Toggle Dark/Light Theme", command=self.toggle_theme)
        menubar.add_cascade(label="View", menu=view_menu)

        # Tools Menu
        tools_menu = tk.Menu(menubar, tearoff=0)
        tools_menu.add_command(label="Preferences", command=self.open_preferences)
        menubar.add_cascade(label="Tools", menu=tools_menu)

        # Help Menu
        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label="About", command=self.show_about)
        menubar.add_cascade(label="Help", menu=help_menu)

        # Bind shortcuts
        self.root.bind_all("<Control-n>", lambda e: self.add_tab())
        self.root.bind_all("<Control-o>", lambda e: self.open_file())
        self.root.bind_all("<Control-s>", lambda e: self.save_file())
        self.root.bind_all("<Control-S>", lambda e: self.save_file_as())
        self.root.bind_all("<Control-w>", lambda e: self.close_tab())
        self.root.bind_all("<Control-q>", lambda e: self.quit())
        self.root.bind_all("<Control-f>", lambda e: self.find_replace())
        self.root.bind_all("<Control-z>", lambda e: self.edit_undo())
        self.root.bind_all("<Control-y>", lambda e: self.edit_redo())

    def create_statusbar(self):
        self.statusbar = ttk.Label(self.root, text="Ln 1, Col 0")
        self.statusbar.pack(side=tk.BOTTOM, fill=tk.X)

    def update_status(self, event=None):
        tab = self.get_current_tab()
        if not tab:
            self.statusbar.config(text="")
            return
        try:
            idx = tab.codeview.index("insert")
            line, col = idx.split(".")
            self.statusbar.config(text=f"Ln {line}, Col {col}")
        except Exception:
            self.statusbar.config(text="")

    def add_tab(self, file_path=None, content=""):
        tab = EditorTab(self.notebook, file_path=file_path, content=content, prefs=self.prefs)
        name = "Untitled" if not file_path else os.path.basename(file_path)
        self.tabs.append(tab)
        self.notebook.add(tab.frame, text=name)
        self.notebook.select(tab.frame)
        tab.codeview.bind("<<Change>>", lambda e: self.update_status())
        tab.codeview.bind("<KeyRelease>", lambda e: self.update_status())

    def get_current_tab(self):
        if not self.tabs:
            return None
        sel = self.notebook.select()
        for tab in self.tabs:
            if str(tab.frame) == sel:
                return tab
        return None

    def close_tab(self):
        tab = self.get_current_tab()
        if tab:
            if tab.is_modified():
                res = messagebox.askyesnocancel("Save Changes?", "Save changes before closing?")
                if res:  # yes
                    if not self.save_file():
                        return  # save canceled or failed
                elif res is None:  # cancel
                    return
            idx = self.tabs.index(tab)
            self.notebook.forget(tab.frame)
            self.tabs.remove(tab)
            if not self.tabs:
                self.add_tab()

    def open_file(self):
        path = filedialog.askopenfilename(filetypes=[("All Files", "*.*")])
        if path:
            try:
                with open(path, "r", encoding="utf-8") as f:
                    content = f.read()
                self.add_tab(file_path=path, content=content)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to open:\n{e}")

    def save_file(self):
        tab = self.get_current_tab()
        if not tab:
            return False
        if tab.file_path:
            return self._write_file(tab, tab.file_path)
        else:
            return self.save_file_as()

    def save_file_as(self):
        tab = self.get_current_tab()
        if not tab:
            return False
        path = filedialog.asksaveasfilename(defaultextension=".txt",
                                            filetypes=[("Text Files", "*.txt"),
                                                       ("Python Files", "*.py"),
                                                       ("All Files", "*.*")])
        if path:
            return self._write_file(tab, path)
        return False

    def _write_file(self, tab, path):
        try:
            content = tab.get_content()
            with open(path, "w", encoding="utf-8") as f:
                f.write(content)
            tab.file_path = path
            idx = self.tabs.index(tab)
            self.notebook.tab(idx, text=os.path.basename(path))
            tab.reset_modified()
            messagebox.showinfo("Saved", f"Saved: {path}")
            return True
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save:\n{e}")
            return False

    def edit_undo(self):
        tab = self.get_current_tab()
        if tab:
            try:
                tab.codeview.edit_undo()
            except:
                pass

    def edit_redo(self):
        tab = self.get_current_tab()
        if tab:
            try:
                tab.codeview.edit_redo()
            except:
                pass

    def edit_cut(self):
        tab = self.get_current_tab()
        if tab:
            tab.codeview.event_generate("<<Cut>>")

    def edit_copy(self):
        tab = self.get_current_tab()
        if tab:
            tab.codeview.event_generate("<<Copy>>")

    def edit_paste(self):
        tab = self.get_current_tab()
        if tab:
            tab.codeview.event_generate("<<Paste>>")

    def find_replace(self):
        tab = self.get_current_tab()
        if not tab:
            return

        find_repl_win = tk.Toplevel(self.root)
        find_repl_win.title("Find & Replace")
        find_repl_win.transient(self.root)
        find_repl_win.resizable(False, False)

        tk.Label(find_repl_win, text="Find:").grid(row=0, column=0, sticky="w", padx=4, pady=4)
        find_entry = tk.Entry(find_repl_win, width=30)
        find_entry.grid(row=0, column=1, padx=4, pady=4)
        find_entry.focus_set()

        tk.Label(find_repl_win, text="Replace:").grid(row=1, column=0, sticky="w", padx=4, pady=4)
        replace_entry = tk.Entry(find_repl_win, width=30)
        replace_entry.grid(row=1, column=1, padx=4, pady=4)

        def do_find():
            tab.codeview.tag_remove("search_match", "1.0", tk.END)
            needle = find_entry.get()
            if not needle:
                return
            idx = "1.0"
            while True:
                idx = tab.codeview.search(needle, idx, nocase=1, stopindex=tk.END)
                if not idx:
                    break
                lastidx = f"{idx}+{len(needle)}c"
                tab.codeview.tag_add("search_match", idx, lastidx)
                idx = lastidx
            tab.codeview.tag_config("search_match", background="yellow", foreground="black")

        def do_replace():
            needle = find_entry.get()
            repl = replace_entry.get()
            if not needle:
                return
            content = tab.get_content()
            new_content = content.replace(needle, repl)
            tab.set_content(new_content)

        btn_find = ttk.Button(find_repl_win, text="Find", command=do_find)
        btn_find.grid(row=2, column=0, padx=4, pady=4)
        btn_replace = ttk.Button(find_repl_win, text="Replace All", command=do_replace)
        btn_replace.grid(row=2, column=1, padx=4, pady=4)

    def toggle_theme(self):
        if self.prefs["theme"] == "light":
            self.prefs["theme"] = "dark"
        else:
            self.prefs["theme"] = "light"
        self.apply_preferences()
        self.save_prefs()

    def open_preferences(self):
        pref_win = tk.Toplevel(self.root)
        pref_win.title("Preferences")
        pref_win.transient(self.root)
        pref_win.resizable(False, False)

        tk.Label(pref_win, text="Font Family:").grid(row=0, column=0, sticky="w", padx=4, pady=4)
        font_families = list(font.families())
        font_families.sort()
        font_family_var = tk.StringVar(value=self.prefs["font_family"])
        font_family_combo = ttk.Combobox(pref_win, textvariable=font_family_var, values=font_families, state="readonly")
        font_family_combo.grid(row=0, column=1, padx=4, pady=4)

        tk.Label(pref_win, text="Font Size:").grid(row=1, column=0, sticky="w", padx=4, pady=4)
        font_size_var = tk.IntVar(value=self.prefs["font_size"])
        font_size_spin = ttk.Spinbox(pref_win, from_=6, to=48, textvariable=font_size_var)
        font_size_spin.grid(row=1, column=1, padx=4, pady=4)

        tk.Label(pref_win, text="Background Color (Light Theme):").grid(row=2, column=0, sticky="w", padx=4, pady=4)
        bg_light_btn = ttk.Button(pref_win, text="Select", command=lambda: self.choose_color("bg_color_light", pref_win))
        bg_light_btn.grid(row=2, column=1, padx=4, pady=4)

        tk.Label(pref_win, text="Foreground Color (Light Theme):").grid(row=3, column=0, sticky="w", padx=4, pady=4)
        fg_light_btn = ttk.Button(pref_win, text="Select", command=lambda: self.choose_color("fg_color_light", pref_win))
        fg_light_btn.grid(row=3, column=1, padx=4, pady=4)

        tk.Label(pref_win, text="Background Color (Dark Theme):").grid(row=4, column=0, sticky="w", padx=4, pady=4)
        bg_dark_btn = ttk.Button(pref_win, text="Select", command=lambda: self.choose_color("bg_color_dark", pref_win))
        bg_dark_btn.grid(row=4, column=1, padx=4, pady=4)

        tk.Label(pref_win, text="Foreground Color (Dark Theme):").grid(row=5, column=0, sticky="w", padx=4, pady=4)
        fg_dark_btn = ttk.Button(pref_win, text="Select", command=lambda: self.choose_color("fg_color_dark", pref_win))
        fg_dark_btn.grid(row=5, column=1, padx=4, pady=4)

        def save_prefs_action():
            self.prefs["font_family"] = font_family_var.get()
            self.prefs["font_size"] = font_size_var.get()
            self.apply_preferences()
            self.save_prefs()
            pref_win.destroy()

        save_btn = ttk.Button(pref_win, text="Save", command=save_prefs_action)
        save_btn.grid(row=6, column=0, columnspan=2, pady=8)

    def choose_color(self, key, window):
        color_code = colorchooser.askcolor()[1]
        if color_code:
            self.prefs[key] = color_code
            self.apply_preferences()
            self.save_prefs()

    def apply_preferences(self):
        for tab in self.tabs:
            tab.set_font(self.prefs["font_family"], self.prefs["font_size"])
            if self.prefs["theme"] == "dark":
                tab.set_colors(self.prefs["bg_color_dark"], self.prefs["fg_color_dark"], "dark")
            else:
                tab.set_colors(self.prefs["bg_color_light"], self.prefs["fg_color_light"], "light")

    def auto_save_all(self):
        # Save all tabs that have a file_path and modified content
        for tab in self.tabs:
            if tab.is_modified() and tab.file_path:
                try:
                    with open(tab.file_path, "w", encoding="utf-8") as f:
                        f.write(tab.get_content())
                    tab.reset_modified()
                except Exception:
                    # Ignore errors for autosave
                    pass
        self.root.after(AUTOSAVE_INTERVAL, self.auto_save_all)

    def show_about(self):
        messagebox.showinfo("About", f"{APP_NAME}\n\n"
                                     "A professional lightweight code editor with syntax highlighting.\n"
                                     "(c) 2025 by YourName")

    def quit(self):
        for tab in self.tabs:
            if tab.is_modified():
                res = messagebox.askyesnocancel("Save Changes?", "Save changes before quitting?")
                if res:  # yes
                    if not self.save_file():
                        return  # cancel quit if save failed
                elif res is None:  # cancel
                    return
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = MiniCodePadPro(root)
    root.mainloop()
