import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
import os, sys, time
from cryptography.fernet import Fernet

APP_NAME = "Serpad"
BACKUP_DIR = os.path.join(os.path.expanduser("~"), ".minicodepad_backups")
RECENT_MAX = 5

os.makedirs(BACKUP_DIR, exist_ok=True)

# Create a Fernet key from a password string (derive key safely)
import base64
import hashlib

def create_key(password: str) -> bytes:
    # Derive a 32-byte key from the password using SHA256 and base64 encode for Fernet
    digest = hashlib.sha256(password.encode()).digest()
    return base64.urlsafe_b64encode(digest)

def encrypt_text(text: str, key: bytes) -> bytes:
    return Fernet(key).encrypt(text.encode())

def decrypt_text(data: bytes, key: bytes) -> str:
    return Fernet(key).decrypt(data).decode()

class SecureEditor:
    def __init__(self, root):
        self.root = root
        self.root.title(APP_NAME)
        self.file_path = None
        self.encrypted = False
        self.key = None
        self.recent_files = []

        self.text = tk.Text(root, font=("Consolas", 12), undo=True, wrap="none")
        self.text.pack(fill=tk.BOTH, expand=True)
        self.status = tk.StringVar()
        tk.Label(root, textvariable=self.status, anchor="w").pack(fill=tk.X)
        self.text.bind("<KeyRelease>", self.update_status)

        menu = tk.Menu(root)
        root.config(menu=menu)

        fileMenu = tk.Menu(menu, tearoff=0)
        fileMenu.add_command(label="Open", command=self.open_file)
        fileMenu.add_command(label="Open Encrypted", command=self.open_encrypted)
        fileMenu.add_command(label="Save", command=self.save_file)
        fileMenu.add_command(label="Save As", command=self.save_as)
        fileMenu.add_separator()
        self.recentMenu = tk.Menu(fileMenu, tearoff=0)
        fileMenu.add_cascade(label="Recent Files", menu=self.recentMenu)
        fileMenu.add_separator()
        fileMenu.add_command(label="Quit", command=self.quit)
        menu.add_cascade(label="File", menu=fileMenu)

        editMenu = tk.Menu(menu, tearoff=0)
        editMenu.add_command(label="Find & Replace", command=self.find_replace)
        menu.add_cascade(label="Edit", menu=editMenu)

        # Auto backup every 5 minutes (300000 ms)
        root.after(300000, self.auto_backup)

    def update_status(self, event=None):
        line, col = self.text.index("insert").split(".")
        self.status.set(f"Line {line}, Column {col}")

    def auto_backup(self):
        content = self.text.get("1.0", tk.END)
        name = "untitled" if not self.file_path else os.path.basename(self.file_path)
        bak_path = os.path.join(BACKUP_DIR, f"{name}-{int(time.time())}.bak")
        try:
            with open(bak_path, "w", encoding="utf-8") as f:
                f.write(content)
        except Exception as e:
            print(f"Backup failed: {e}")
        self.root.after(300000, self.auto_backup)

    def open_file(self):
        path = filedialog.askopenfilename()
        if not path:
            return
        if path.endswith(".enc"):
            self.open_encrypted(path)
        else:
            self._load_file(path, encrypted=False)

    def save_file(self):
        if self.file_path:
            self._save(self.file_path)
        else:
            self.save_as()

    def save_as(self):
        path = filedialog.asksaveasfilename(defaultextension=".txt")
        if not path:
            return
        self._save(path)

    def _save(self, path):
        content = self.text.get("1.0", tk.END)
        try:
            if self.encrypted:
                data = encrypt_text(content, self.key)
                path = path if path.endswith(".enc") else path + ".enc"
                with open(path, "wb") as f:
                    f.write(data)
            else:
                with open(path, "w", encoding="utf-8") as f:
                    f.write(content)
            self.file_path = path
            self.add_recent(path)
            self.root.title(f"{APP_NAME} - {os.path.basename(path)}")
            messagebox.showinfo("Saved", f"Saved to {self.file_path}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save:\n{e}")

    def open_encrypted(self, path=None):
        if not path:
            path = filedialog.askopenfilename(filetypes=[("Encrypted Files", "*.enc")])
            if not path:
                return
        password = simpledialog.askstring("Password", "Enter decryption password:", show="*")
        if not password:
            messagebox.showerror("Error", "No password entered")
            return
        self.encrypted = True
        self.key = create_key(password)
        self._load_file(path, encrypted=True)

    def _load_file(self, path, encrypted=False):
        try:
            if encrypted:
                with open(path, "rb") as f:
                    data = f.read()
                content = decrypt_text(data, self.key)
            else:
                with open(path, "r", encoding="utf-8") as f:
                    content = f.read()
            self.text.delete("1.0", tk.END)
            self.text.insert(tk.END, content)
            self.file_path = path
            self.encrypted = encrypted
            self.add_recent(path)
            self.root.title(f"{APP_NAME} - {os.path.basename(path)}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed opening file:\n{e}")

    def find_replace(self):
        fr = tk.Toplevel(self.root)
        fr.title("Find & Replace")
        fr.transient(self.root)
        fr.resizable(False, False)
        tk.Label(fr, text="Find:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        tk.Label(fr, text="Replace:").grid(row=1, column=0, padx=5, pady=5, sticky="e")

        find_entry = tk.Entry(fr, width=30)
        repl_entry = tk.Entry(fr, width=30)
        find_entry.grid(row=0, column=1, padx=5, pady=5)
        repl_entry.grid(row=1, column=1, padx=5, pady=5)

        def do_replace():
            self.text.tag_remove("match", "1.0", tk.END)
            search = find_entry.get()
            replace = repl_entry.get()
            if not search:
                messagebox.showwarning("Warning", "Find field cannot be empty.")
                return
            idx = "1.0"
            while True:
                idx = self.text.search(search, idx, nocase=1, stopindex=tk.END)
                if not idx:
                    break
                lastidx = f"{idx}+{len(search)}c"
                self.text.delete(idx, lastidx)
                self.text.insert(idx, replace)
                idx = lastidx
            fr.destroy()

        tk.Button(fr, text="Replace All", command=do_replace).grid(row=2, column=0, columnspan=2, pady=10)

    def add_recent(self, path):
        if path in self.recent_files:
            self.recent_files.remove(path)
        self.recent_files.insert(0, path)
        self.recent_files = self.recent_files[:RECENT_MAX]

        self.recentMenu.delete(0, tk.END)
        for p in self.recent_files:
            self.recentMenu.add_command(label=p, command=lambda pp=p: self._load_file(pp, pp.endswith(".enc")))

    def quit(self):
        if messagebox.askokcancel("Quit", "Are you sure you want to quit?"):
            self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = SecureEditor(root)
    root.mainloop()
