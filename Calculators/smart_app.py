import tkinter as tk
import math

# Initialize window
root = tk.Tk()
root.title("Smart Calculator")
root.geometry("400x600")
root.resizable(False, False)
root.configure(bg="#2e2e2e")

# Global variable to track input
expression = ""

# Display
entry_var = tk.StringVar()
entry = tk.Entry(root, textvariable=entry_var, font=("Arial", 24), bg="#1e1e1e", fg="white", bd=0, relief="flat", justify="right")
entry.pack(fill="both", ipadx=8, ipady=20, padx=10, pady=10)

# Function to update expression
def press(key):
    global expression
    expression += str(key)
    entry_var.set(expression)

# Function to clear
def clear():
    global expression
    expression = ""
    entry_var.set("")

# Function to delete last character
def backspace():
    global expression
    expression = expression[:-1]
    entry_var.set(expression)

# Function to calculate result
def equal():
    global expression
    try:
        result = eval(expression)
        entry_var.set(result)
        expression = str(result)
    except:
        entry_var.set("Error")
        expression = ""

# Scientific functions
def sqrt():
    global expression
    try:
        result = math.sqrt(eval(expression))
        entry_var.set(result)
        expression = str(result)
    except:
        entry_var.set("Error")
        expression = ""

def sin():
    global expression
    try:
        result = math.sin(math.radians(eval(expression)))
        entry_var.set(result)
        expression = str(result)
    except:
        entry_var.set("Error")
        expression = ""

def cos():
    global expression
    try:
        result = math.cos(math.radians(eval(expression)))
        entry_var.set(result)
        expression = str(result)
    except:
        entry_var.set("Error")
        expression = ""

def tan():
    global expression
    try:
        result = math.tan(math.radians(eval(expression)))
        entry_var.set(result)
        expression = str(result)
    except:
        entry_var.set("Error")
        expression = ""

def log():
    global expression
    try:
        result = math.log10(eval(expression))
        entry_var.set(result)
        expression = str(result)
    except:
        entry_var.set("Error")
        expression = ""

# Button layout
buttons = [
    ['7', '8', '9', '/', 'sqrt'],
    ['4', '5', '6', '*', 'log'],
    ['1', '2', '3', '-', 'sin'],
    ['0', '.', '%', '+', 'cos'],
    ['C', '⌫', '=', '', 'tan']
]

# Button functions mapping
functions = {
    '=': equal,
    'C': clear,
    '⌫': backspace,
    'sqrt': sqrt,
    'sin': sin,
    'cos': cos,
    'tan': tan,
    'log': log
}

# Button container
frame = tk.Frame(root, bg="#2e2e2e")
frame.pack(expand=True, fill="both")

# Create buttons
for row_index, row in enumerate(buttons):
    for col_index, label in enumerate(row):
        if label == '':
            continue
        action = functions.get(label, lambda x=label: press(x))
        btn = tk.Button(frame, text=label, font=("Arial", 16), command=action,
                        bg="#3e3e3e", fg="white", activebackground="#5e5e5e", bd=0)
        btn.grid(row=row_index, column=col_index, sticky="nsew", padx=1, pady=1)

# Grid config
for i in range(len(buttons)):
    frame.rowconfigure(i, weight=1)
for j in range(5):
    frame.columnconfigure(j, weight=1)

# Keyboard support
def key_input(event):
    key = event.char
    if key in '0123456789.+-*/%':
        press(key)
    elif key == '\r':  # Enter
        equal()
    elif key == '\x08':  # Backspace
        backspace()

root.bind("<Key>", key_input)

# Start app
root.mainloop()
