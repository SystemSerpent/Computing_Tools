import tkinter as tk
from tkinter import messagebox
import string
import random

# ------------------------ Password Generator Logic ------------------------
def generate_password():
    try:
        length = int(length_var.get())
        if length < 6:
            raise ValueError("Password must be at least 6 characters.")

        characters = string.ascii_letters + string.digits + string.punctuation
        password = ''.join(random.choice(characters) for _ in range(length))
        password_var.set(password)
        update_strength(password)

    except ValueError as ve:
        messagebox.showerror("Input Error", str(ve))
        password_var.set("")
        strength_var.set("")

# ------------------------ Password Strength Meter ------------------------
def update_strength(password):
    score = 0
    if len(password) >= 8: score += 1
    if any(c.islower() for c in password): score += 1
    if any(c.isupper() for c in password): score += 1
    if any(c.isdigit() for c in password): score += 1
    if any(c in string.punctuation for c in password): score += 1

    if score <= 2:
        strength_var.set("Weak")
        strength_label.config(fg="red")
    elif score == 3 or score == 4:
        strength_var.set("Moderate")
        strength_label.config(fg="orange")
    else:
        strength_var.set("Strong")
        strength_label.config(fg="green")

# ------------------------ GUI Setup ------------------------
root = tk.Tk()
root.title("Smart Password Generator")
root.geometry("400x300")
root.resizable(False, False)
root.configure(bg="#1e1e1e")

# ------------------------ Variables ------------------------
password_var = tk.StringVar()
length_var = tk.StringVar(value="12")
strength_var = tk.StringVar(value="")

# ------------------------ UI Layout ------------------------
tk.Label(root, text="Smart Password Generator", font=("Arial", 16, "bold"), bg="#1e1e1e", fg="white").pack(pady=10)

tk.Label(root, text="Password Length (min 6):", font=("Arial", 12), bg="#1e1e1e", fg="white").pack()
tk.Entry(root, textvariable=length_var, font=("Arial", 12), justify="center", width=5).pack(pady=5)

tk.Button(root, text="Generate Password", font=("Arial", 12), bg="#4caf50", fg="white", command=generate_password).pack(pady=10)

tk.Entry(root, textvariable=password_var, font=("Courier", 14), justify="center", width=30, bd=2, relief="sunken", state="readonly").pack(pady=10)

strength_label = tk.Label(root, textvariable=strength_var, font=("Arial", 12, "bold"), bg="#1e1e1e")
strength_label.pack(pady=5)

tk.Label(root, text="(Copy password manually from above)", font=("Arial", 10), bg="#1e1e1e", fg="gray").pack()

# ------------------------ Main Loop ------------------------
root.mainloop()
