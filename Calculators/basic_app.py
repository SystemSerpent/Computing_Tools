import tkinter as tk

# Create the main window
root = tk.Tk()
root.title("Simple Calculator")
root.geometry("300x400")
root.resizable(False, False)

# Entry field for input/output
entry = tk.Entry(root, font=("Arial", 20), borderwidth=2, relief="solid", justify="right")
entry.pack(fill="both", ipadx=8, ipady=15, padx=10, pady=10)

# Function to handle button click
def on_click(symbol):
    if symbol == "C":
        entry.delete(0, tk.END)
    elif symbol == "=":
        try:
            result = eval(entry.get())
            entry.delete(0, tk.END)
            entry.insert(0, str(result))
        except:
            entry.delete(0, tk.END)
            entry.insert(0, "Error")
    else:
        entry.insert(tk.END, symbol)

# Button labels in a grid layout
buttons = [
    ['7', '8', '9', '/'],
    ['4', '5', '6', '*'],
    ['1', '2', '3', '-'],
    ['0', '.', 'C', '+'],
    ['=']
]

# Frame to hold buttons
button_frame = tk.Frame(root)
button_frame.pack(expand=True, fill="both")

# Create buttons dynamically
for row_index, row in enumerate(buttons):
    for col_index, label in enumerate(row):
        button = tk.Button(button_frame, text=label, font=("Arial", 16), command=lambda x=label: on_click(x))
        button.grid(row=row_index, column=col_index, sticky="nsew", padx=2, pady=2)

# Configure grid weights
for i in range(5):  # 5 rows
    button_frame.rowconfigure(i, weight=1)
for j in range(4):  # 4 columns
    button_frame.columnconfigure(j, weight=1)

# Start the GUI loop
root.mainloop()
