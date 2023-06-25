import tkinter as tk
from tkinter import ttk

root = tk.Tk()

paned_window = ttk.PanedWindow(root, orient=tk.HORIZONTAL)
paned_window.pack(fill=tk.BOTH, expand=True)

# Create and add two panes to the PanedWindow
pane1 = ttk.Frame(paned_window, width=200, height=300, relief=tk.RAISED)
pane2 = ttk.Frame(paned_window, width=400, height=300, relief=tk.RAISED)

paned_window.add(pane1)
paned_window.add(pane2)

# Add some content to the panes
label1 = ttk.Label(pane1, text="Pane 1", padding=10)
label1.pack()

label2 = ttk.Label(pane2, text="Pane 2", padding=10)
label2.pack()

root.mainloop()
