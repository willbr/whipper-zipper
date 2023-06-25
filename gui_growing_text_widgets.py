
import tkinter as tk

def update_text_height(event):
    text_widget = event.widget
    text = text_widget.get("1.0", tk.END)
    if text == "\n":
        lines = 1
    else:
        lines = text.count("\n") + 1
    text_widget.config(height=lines)

# Create the main window
root = tk.Tk()
root.geometry("400x400")

# Create a list to store the Text widgets
text_widgets = []

# Add five Text widgets
for _ in range(5):
    text_widget = tk.Text(root, height=1)
    text_widget.pack(side=tk.TOP, padx=5, pady=5)
    text_widget.bind("<KeyRelease>", update_text_height)
    text_widgets.append(text_widget)

# Set focus on the first widget
text_widgets[0].focus_set()

# Start the main loop
root.mainloop()
