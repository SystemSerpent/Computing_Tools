import tkinter as tk
from tkinter import ttk
from chlorophyll import CodeView
from pygments.lexers import get_lexer_by_name

class EditorTab:
    def __init__(self, parent):
        self.frame = ttk.Frame(parent)
        lexer = get_lexer_by_name("python")
        self.codeview = CodeView(self.frame, lexer=lexer, color_scheme="monokai")
        self.codeview.pack(fill="both", expand=True)

class MiniCodePadPro:
    def __init__(self, root):
        self.root = root
        self.root.title("MiniCodePad Pro")
        self.root.geometry("800x600")

        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill="both", expand=True)

        self.tabs = []
        self.add_tab()

        self.menu = tk.Menu(root)
        file_menu = tk.Menu(self.menu, tearoff=0)
        file_menu.add_command(label="New Tab", command=self.add_tab)
        file_menu.add_command(label="Exit", command=root.quit)
        self.menu.add_cascade(label="File", menu=file_menu)
        root.config(menu=self.menu)

    def add_tab(self):
        tab = EditorTab(self.notebook)
        self.tabs.append(tab)
        self.notebook.add(tab.frame, text="Untitled")
        self.notebook.select(tab.frame)

def main():
    root = tk.Tk()
    MiniCodePadPro(root)
    root.mainloop()

if __name__ == "__main__":
    main()
