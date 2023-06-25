
import tkinter as tk
from tkinter import ttk

root = tk.Tk()
root.geometry("800x600")

# Create a canvas
canvas = tk.Canvas(root)
canvas.grid(row=0, column=0, sticky=tk.NSEW)

# Create a vertical scrollbar
scrollbar = ttk.Scrollbar(root, orient=tk.VERTICAL, command=canvas.yview)
scrollbar.grid(row=0, column=1, sticky=tk.NS)
canvas.configure(yscrollcommand=scrollbar.set)

# Create a frame inside the canvas
frame = ttk.Frame(canvas)
canvas.create_window((0, 0), window=frame, anchor=tk.NW)

# Create a list to hold the text widgets
text_widgets = []

# Create labels and text widgets
for i in range(7):
    # Create the label
    label = ttk.Label(frame, text=f"Text Widget {i+1}")
    label.grid(row=i, column=0, sticky=tk.W)

    # Create the text widget
    text_widget = tk.Text(frame)
    text_widget.grid(row=i, column=1, sticky=tk.NSEW)

    # Insert some text into the text widget
    text_widget.insert(tk.END, f"Hello, Text widget {i+1}!")

    # Add the text widget to the list
    text_widgets.append(text_widget)

# Configure the canvas to adjust scroll region when the frame is resized
def configure_canvas(event):
    canvas.configure(scrollregion=canvas.bbox("all"))

frame.bind("<Configure>", configure_canvas)

# Update frame width based on canvas width
def update_frame_width(event):
    canvas_width = canvas.winfo_width()
    canvas.itemconfig(frame_window, width=canvas_width)

frame_window = canvas.create_window((0, 0), window=frame, anchor=tk.NW)
canvas.bind("<Configure>", update_frame_width)

# Configure grid weights to allow the root window and canvas to expand
root.grid_rowconfigure(0, weight=1)
root.grid_columnconfigure(0, weight=1)
canvas.grid_rowconfigure(0, weight=1)
canvas.grid_columnconfigure(0, weight=1)

root.mainloop()
