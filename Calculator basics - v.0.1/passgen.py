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
    