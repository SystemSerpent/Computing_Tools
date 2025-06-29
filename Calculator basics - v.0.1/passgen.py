import tkinter as tk
from tkinter import messagebox
import string
import random

def generate_password():
    try:
        length = int(length_var.get)
        if length < 4:
            raise ValueError
        
        characters = ""
        if use_uppercase.get():
            characters += string.ascii_uppercase
        if use_lowercase.get():
            characters += string.ascii_lowercase
        if use_numbers.get():
            characters += string.digits
        if use_symbols.get():
            characters += string.punctuation

        if not characters:
            messagebox.showwarning("Warning", "Select at least one character type.")
            return
        
        password = ''.join(random.choice(characters) for _ in range(length))
        password_var.set(password)
        update_strength(password)

    except ValueError:
        messagebox.showerror("Invalid Input", "Please enter a valid number for length (4 or more).")

def update_strength(password):
    score = 0
    if len(password) >= 8:
        score += 1
    if any(c.islower() for c in password):
        score += 1
    if any(c.isupper() for c in password):
        score += 1
    if any(c.isdigit() for c in password):
        score += 1
    if any(c in string.punctuation for c in password):
        score += 1

    if score <= 2:
        strength_var.se("Weak")
        strength_label.config(fg="red")
    elif score in [3,4]:
        strength_var.set("Moderate")
        strength_label.config(fg="orange")
    else:
        strength_var.set("Strong")
        strength_label.config(fg="green")


def copy_to_clipboard():
    root.clipboard_clear()
    messagebox.showinfo("Clipboard Cleared", "Clipboard content cleared for your safety!")

root = tk.Tk()
root.title("Smart Password Generator")
root.geometry("400x480")
root.resizable(False, False)
root.configure(bg="#2c2f33")

password_var = tk.StringVar()
length_var = tk.StringVar(value=12)
strength_var = tk.StringVar(value="")

use_uppercase = tk.BooleanVar(value=True)
use_lowercase = tk.BooleanVar(value=True)
use_numbers = tk.BooleanVar(value=True)
use_symbols = tk.BooleanVar(value=True)


tk.Label(root, text="Smart Password Generator", font=("Arial", 16, "bold"), bg="#2c2f33", fg="#ffffff").pack(pady=10)

frame = tk.Frame(root, bg="#2c2f33")
frame.pack(pady=10)

tk.Label(frame, text="Password Length:", font=("Arial", 12), bg="#2c2f33", fg="#ffffff").grid(row=0, column=0, sticky="w")
tk.Entry(frame, textvariable=length_var, width=5, font=("Arial", 12)).grid(row=0, column=1, padx=5)

tk.Checkbutton(frame, text="Uppercase (A-Z)", variable=use_uppercase, bg="#2c2f33", fg="white", font=("Arial", 10)).grid(row=1, column=0, sticky="w")
tk.Checkbutton(frame, text="Lowercase (a-z)", variable=use_lowercase, bg="#2c2f33", fg="white", font=("Arial", 10)).grid(row=2, column=0, sticky="w")
tk.Checkbutton(frame, text="Numbers (0-9)", variable=use_numbers, bg="#2c2f33", fg="white", font=("Arial", 10)).grid(row=3, column=0, sticky="w")
tk.Checkbutton(frame, text="Symbols (!@#)", variable=use_symbols, bg="#2c2f33", fg="white", font=("Arial", 10)).grid(row=4, column=0, sticky="w")

tk.Button(root, text="Generate Password", font=("Arial", 12, "bold"), bg="#7289da", fg="white", command=generate_password).pack(pady=15)

tk.Entry(root, textvariable=password_var, font=("Arial", 14), justify="center", bd=2, relief="sunken", width=30).pack(pady=5)
tk.Button(root, text="Copy to Clipboard", font=("Arial", 10), bg="#99aab5", fg="black", command=copy_to_clipboard).pack(pady=5)
tk.Button(root, text="Clear Clipboard", font=("Arial", 10), bg="#ff5555", fg="white", command=clear_clipboard).pack(pady=5)

strength_label = tk.Label(root, textvariable=strength_var, font=("Arial", 12, "bold"), bg="#2c2f33")
strength_label.pack(pady=5)

root.mainloop()