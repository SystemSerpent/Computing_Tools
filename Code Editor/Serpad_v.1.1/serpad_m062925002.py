import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog, font, colorchooser
from chlorophyll.codeview import CodeView
from pygments.lexers import guess_lexer_for_filename, get_lexer_by_name
from pygments.util import ClassNotFound
import json
import os

APP_NAME = "MiniCodePad Pro"
AUTOSAVE_INTERVAL = 300000  # 5 minutes in ms
PREFS_FILE = os.path.expanduser("~/.minicodepad_prefs.json")

class EditorTab:
    def __init__(self, parent_notebook, file_path=None, content="", prefs=None):
        self.frame = ttk.Frame(parent_notebook)
        self.file_path = file_path
        self.prefs = prefs or {}
        self.modified = False

        # Determine lexer based on file_path or default to plain text
        if file_path:
            try:
                with open(file_path, encoding="utf-8") as f:
                    content = f.read()
                self.lexer = guess_lexer_for_filename(file_path, content)
            except (FileNotFoundError, ClassNotFound):
                self.lexer = get_lexer_by_name("text")
        else:
            self.lexer = get_lexer_by_name("text")

        self.codeview = CodeView(self.frame, lexer=self.lexer,
                                 color_scheme="monokai" if self.prefs.get("theme", "light") == "dark" else "solarized_light",
                                 autohide_scrollbar=False,
                                 font=(self.prefs.get("font_family", "Consolas"), self.prefs.get("font_size", 12)),
                                 bg=self.prefs.get("bg_color_dark") if self.prefs.get("theme") == "dark" else self.prefs.get("bg_color_light"),
                                 fg=self.prefs.get("fg_color_dark") if self.prefs.get("theme") == "dark" else self.prefs.get("fg_color_light"),
                                 )
        self.codeview.pack(fill="both", expand=True)
        self.set_content(content)

        self.codeview.textwidget.bind("<<Modified>>", self._on_modified)

    def _on_modified(self, event=None):
        if self.codeview.textwidget.edit_modified():
            self.modified = True
            self.codeview.textwidget.edit_modified(False)  # reset flag

    def get_content(self):
        return self.codeview.get("1.0", "end-1c")

    def set_content(self, content):
        self.codeview.delete("1.0", "end")
        self.codeview.insert("1.0", content)
        self.codeview.highlight_all()
        self.modified = False

    def set_font(self, family, size):
        self.codeview.configure(font=(family, size))

    def set_colors(self, bg, fg, theme):
        self.codeview.configure(bg=bg, fg=fg)
        # Update color scheme accordingly
        if theme == "dark":
            self.codeview.color_scheme = "monokai"
        else:
            self.codeview.color_scheme = "solarized_light"
        self.codeview.highlight_all()

    def is_modified(self):
        return self.modified

    def reset_modified(self):
        self.modified = False
        self.codeview.textwidget.edit_modified(False)

class MiniCodePadPro:
    def __init__(self, root):
        self.root = root
        self.root.title(APP_NAME)
        self.root.geometry("900x600")
        self.tabs = []
        self.prefs = self.load_prefs()

        self.setup_ui()
        self.add_tab()
        self.apply_preferences()
        self.auto_save_all()

    def setup_ui(self):
        # Menu
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        # File menu
        filemenu = tk.Menu(menubar, tearoff=0)
        filemenu.add_command(label="New", accelerator="Ctrl+N", command=self.new_file)
        filemenu.add_command(label="Open...", accelerator="Ctrl+O", command=self.open_file)
        filemenu.add_command(label="Save", accelerator="Ctrl+S", command=self.save_file)
        filemenu.add_command(label="Save As...", accelerator="Ctrl+Shift+S", command=self.save_file_as)
        filemenu.add_separator()
        filemenu.add_command(label="Close Tab", accelerator="Ctrl+W", command=self.close_tab)
        filemenu.add_separator()
        filemenu.add_command(label="Quit", accelerator="Ctrl+Q", command=self.quit)
        menubar.add_cascade(label="File", menu=filemenu)

        # Edit menu
        editmenu = tk.Menu(menubar, tearoff=0)
        editmenu.add_command(label="Undo", accelerator="Ctrl+Z", command=self.undo)
        editmenu.add_command(label="Redo", accelerator="Ctrl+Y", command=self.redo)
        editmenu.add_separator()
        editmenu.add_command(label="Cut", accelerator="Ctrl+X", command=self.cut)
        editmenu.add_command(label="Copy", accelerator="Ctrl+C", command=self.copy)
        editmenu.add_command(label="Paste", accelerator="Ctrl+V", command=self.paste)
        editmenu.add_separator()
        editmenu.add_command(label="Find/Replace", accelerator="Ctrl+F", command=self.find_replace)
        menubar.add_cascade(label="Edit", menu=editmenu)

        # View menu
        viewmenu = tk.Menu(menubar, tearoff=0)
        viewmenu.add_command(label="Toggle Dark/Light Theme", command=self.toggle_theme)
        menubar.add_cascade(label="View", menu=viewmenu)

        # Tools menu
        toolsmenu = tk.Menu(menubar, tearoff=0)
        toolsmenu.add_command(label="Preferences", command=self.open_preferences)
        menubar.add_cascade(label="Tools", menu=toolsmenu)

        # Help menu
        helpmenu = tk.Menu(menubar, tearoff=0)
        helpmenu.add_command(label="About", command=self.show_about)
        menubar.add_cascade(label="Help", menu=helpmenu)

        # Notebook for tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True)
        self.notebook.bind("<<NotebookTabChanged>>", self.on_tab_changed)

        # Status bar
        self.statusbar = ttk.Label(self.root, text="Ready", anchor="w")
        self.statusbar.pack(side="bottom", fill="x")

        # Keyboard shortcuts
        self.root.bind_all("<Control-n>", lambda e: self.new_file())
        self.root.bind_all("<Control-o>", lambda e: self.open_file())
        self.root.bind_all("<Control-s>", lambda e: self.save_file())
        self.root.bind_all("<Control-S>", lambda e: self.save_file_as())
        self.root.bind_all("<Control-w>", lambda e: self.close_tab())
        self.root.bind_all("<Control-q>", lambda e: self.quit())
        self.root.bind_all("<Control-f>", lambda e: self.find_replace())
        self.root.bind_all("<Control-z>", lambda e: self.undo())
        self.root.bind_all("<Control-y>", lambda e: self.redo())
        self.root.bind_all("<Control-x>", lambda e: self.cut())
        self.root.bind_all("<Control-c>", lambda e: self.copy())
        self.root.bind_all("<Control-v>", lambda e: self.paste())

    def load_prefs(self):
        # Default preferences
        default_prefs = {
            "font_family": "Consolas",
            "font_size": 12,
            "theme": "light",
            "bg_color_light": "#ffffff",
            "fg_color_light": "#000000",
            "bg_color_dark": "#1e1e1e",
            "fg_color_dark": "#d4d4d4",
        }
        try:
            if os.path.exists(PREFS_FILE):
                with open(PREFS_FILE, "r", encoding="utf-8") as f:
                    loaded = json.load(f)
                    default_prefs.update(loaded)
        except Exception:
            pass
        return default_prefs

    def save_prefs(self):
        try:
            with open(PREFS_FILE, "w", encoding="utf-8") as f:
                json.dump(self.prefs, f, indent=4)
        except Exception:
            pass

    def add_tab(self, file_path=None, content=""):
        tab = EditorTab(self.notebook, file_path=file_path, content=content, prefs=self.prefs)
        self.tabs.append(tab)
        filename = os.path.basename(file_path) if file_path else "Untitled"
        self.notebook.add(tab.frame, text=filename)
        self.notebook.select(tab.frame)
        self.update_statusbar()
        return tab

    def current_tab(self):
        current = self.notebook.select()
        for tab in self.tabs:
            if str(tab.frame) == current:
                return tab
        return None

    def new_file(self):
        self.add_tab()

    def open_file(self):
        filepath = filedialog.askopenfilename()
        if filepath:
            for tab in self.tabs:
                if tab.file_path == filepath:
                    self.notebook.select(tab.frame)
                    return
            try:
                with open(filepath, encoding="utf-8") as f:
                    content = f.read()
                self.add_tab(file_path=filepath, content=content)
            except Exception as e:
                messagebox.showerror("Error", f"Could not open file: {e}")

    def save_file(self):
        tab = self.current_tab()
        if not tab:
            return False
        if tab.file_path:
            try:
                with open(tab.file_path, "w", encoding="utf-8") as f:
                    f.write(tab.get_content())
                tab.reset_modified()
                self.update_tab_title(tab)
                return True
            except Exception as e:
                messagebox.showerror("Error", f"Could not save file: {e}")
                return False
        else:
            return self.save_file_as()

    def save_file_as(self):
        tab = self.current_tab()
        if not tab:
            return False
        filepath = filedialog.asksaveasfilename(defaultextension=".txt")
        if filepath:
            try:
                with open(filepath, "w", encoding="utf-8") as f:
                    f.write(tab.get_content())
                tab.file_path = filepath
                tab.reset_modified()
                self.update_tab_title(tab)
                self.notebook.tab(tab.frame, text=os.path.basename(filepath))
                return True
            except Exception as e:
                messagebox.showerror("Error", f"Could not save file: {e}")
                return False
        return False

    def update_tab_title(self, tab):
        title = os.path.basename(tab.file_path) if tab.file_path else "Untitled"
        if tab.is_modified():
            title += "*"
        idx = self.notebook.index(tab.frame)
        self.notebook.tab(idx, text=title)

    def close_tab(self):
        tab = self.current_tab()
        if tab:
            if tab.is_modified():
                res = messagebox.askyesnocancel("Save Changes?", "Save changes before closing tab?")
                if res:  # yes
                    if not self.save_file():
                        return
                elif res is None:  # cancel
                    return
            idx = self.notebook.index(tab.frame)
            self.notebook.forget(idx)
            self.tabs.remove(tab)
            self.update_statusbar()

    def on_tab_changed(self, event=None):
        self.update_statusbar()

    def update_statusbar(self):
        tab = self.current_tab()
        if not tab:
            self.statusbar.config(text="No open file")
            return
        text_widget = tab.codeview.textwidget
        line, col = text_widget.index("insert").split(".")
        status = f"Ln {line}, Col {int(col)+1}"
        self.statusbar.config(text=status)
        self.update_tab_title(tab)

    def undo(self):
        tab = self.current_tab()
        if tab:
            try:
                tab.codeview.textwidget.edit_undo()
            except Exception:
                pass

    def redo(self):
        tab = self.current_tab()
        if tab:
            try:
                tab.codeview.textwidget.edit_redo()
            except Exception:
                pass

    def cut(self):
        tab = self.current_tab()
        if tab:
            tab.codeview.textwidget.event_generate("<<Cut>>")

    def copy(self):
        tab = self.current_tab()
        if tab:
            tab.codeview.textwidget.event_generate("<<Copy>>")

    def paste(self):
        tab = self.current_tab()
        if tab:
            tab.codeview.textwidget.event_generate("<<Paste>>")

    def find_replace(self):
        tab = self.current_tab()
        if not tab:
            return
        find_repl_win = tk.Toplevel(self.root)
        find_repl_win.title("Find and Replace")
        find_repl_win.transient(self.root)
        find_repl_win.resizable(False, False)

        tk.Label(find_repl_win, text="Find:").grid(row=0, column=0, sticky="w", padx=4, pady=4)
        find_entry = ttk.Entry(find_repl_win, width=30)
        find_entry.grid(row=0, column=1, padx=4, pady=4)

        tk.Label(find_repl_win, text="Replace with:").grid(row=1, column=0, sticky="w", padx=4, pady=4)
        replace_entry = ttk.Entry(find_repl_win, width=30)
        replace_entry.grid(row=1, column=1, padx=4, pady=4)

        def do_find():
            needle = find_entry.get()
            if not needle:
                return
            content = tab.get_content()
            idx = content.find(needle)
            if idx == -1:
                messagebox.showinfo("Find", "Text not found.")
                return
            line = content.count("\n", 0, idx) + 1
            col = idx - content.rfind("\n", 0, idx)
            tab.codeview.textwidget.mark_set("insert", f"{line}.{col}")
            tab.codeview.textwidget.see("insert")
            tab.codeview.textwidget.focus()

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
        self.prefs["theme"] = "dark" if self.prefs["theme"] == "light" else "light"
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
        font_family_var = tk.StringVar(value=self.prefs.get("font_family", "Consolas"))
        font_family_combo = ttk.Combobox(pref_win, textvariable=font_family_var, values=font_families, state="readonly")
        font_family_combo.grid(row=0, column=1, padx=4, pady=4)

        tk.Label(pref_win, text="Font Size:").grid(row=1, column=0, sticky="w", padx=4, pady=4)
        font_size_var = tk.IntVar(value=self.prefs.get("font_size", 12))
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
            tab.set_font(self.prefs.get("font_family", "Consolas"), self.prefs.get("font_size", 12))
            if self.prefs.get("theme") == "dark":
                tab.set_colors(self.prefs.get("bg_color_dark", "#1e1e1e"), self.prefs.get("fg_color_dark", "#d4d4d4"), "dark")
            else:
                tab.set_colors(self.prefs.get("bg_color_light", "#ffffff"), self.prefs.get("fg_color_light", "#000000"), "light")
            tab.codeview.highlight_all()

    def auto_save_all(self):
        for tab in self.tabs:
            if tab.is_modified() and tab.file_path:
                try:
                    with open(tab.file_path, "w", encoding="utf-8") as f:
                        f.write(tab.get_content())
                    tab.reset_modified()
                    self.update_tab_title(tab)
                except Exception:
                    pass
        self.root.after(AUTOSAVE_INTERVAL, self.auto_save_all)

    def quit(self):
        for tab in self.tabs[:]:
            self.notebook.select(tab.frame)
            if tab.is_modified():
                res = messagebox.askyesnocancel("Save Changes?", "Save changes before quitting?")
                if res:  # yes
                    if not self.save_file():
                        return
                elif res is None:  # cancel
                    return
        self.root.destroy()

    def show_about(self):
        messagebox.showinfo(APP_NAME, f"{APP_NAME}\n\nA lightweight, secure Python code editor.\n\nBy ChatGPT")

def main():
    root = tk.Tk()
    app = MiniCodePadPro(root)
    root.mainloop()

if __name__ == "__main__":
    main()
