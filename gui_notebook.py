
import tkinter as tk
from tkinter import ttk

root = tk.Tk()
root.geometry("400x300")
root.title("ListNoteBook Demo")

notebook = ttk.Notebook(root)
notebook.pack(fill=tk.BOTH, expand=True)

# Create and add tabs to the Notebook
tab1 = ttk.Frame(notebook)
tab2 = ttk.Frame(notebook)
tab3 = ttk.Frame(notebook)

notebook.add(tab1, text="Tab 1")
notebook.add(tab2, text="Tab 2")
notebook.add(tab3, text="Tab 3")

# Add content to the tabs
label1 = ttk.Label(tab1, text="Content of Tab 1", padding=10)
label1.pack()

label2 = ttk.Label(tab2, text="Content of Tab 2", padding=10)
label2.pack()

label3 = ttk.Label(tab3, text="Content of Tab 3", padding=10)
label3.pack()

root.mainloop()
