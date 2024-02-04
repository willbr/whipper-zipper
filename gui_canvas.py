import tkinter as tk

root = tk.Tk()
root.title("Spreadsheet")
root.geometry("1080x1080")

root.update_idletasks()

# Define the number of rows and columns in the spreadsheet
num_rows = 30
num_cols = 5

canvas_height = root.winfo_height()

# Calculate the width and height of each cell
cell_width = 150
cell_height = 50

entry_frame = tk.Frame(root)
entry_frame.pack(pady=5, fill='x', expand=True)

cell_name = tk.Entry(
        entry_frame,
        width=12,
        highlightthickness=1,
        highlightbackground="gray")
cell_name.pack(side='left', padx=(0,5))
cell_name.configure(font=("Arial", 28))
cell_name.insert(0, "name")

entry = tk.Entry(
        entry_frame,
        highlightthickness=1,
        highlightbackground="gray")
entry.pack(side='right', fill='both', expand=True, padx=(5,5))
entry.configure(font=("Arial", 28))
entry.insert(0, "formula")
entry.focus()

# Create a scrollable canvas
canvas_frame = tk.Frame(root)
canvas_frame.pack(fill='both', expand=True)
canvas_frame.grid_rowconfigure(1, weight=1)
canvas_frame.grid_columnconfigure(1, weight=1)

canvas = tk.Canvas(canvas_frame, height=canvas_height, bg="white")
canvas.grid(row=1, column=1, sticky="nsew")

def scroll_x(*args):
    print(args)

def scroll_y(*args):
    print(args)

# Create a horizontal scrollbar
scrollbar_x = tk.Scrollbar(canvas_frame, orient="horizontal", command=scroll_x)
scrollbar_x.grid(row=2, column=1, sticky="ew")

# Create a vertical scrollbar
scrollbar_y = tk.Scrollbar(canvas_frame, orient="vertical", command=scroll_y)
scrollbar_y.grid(row=1, column=2, sticky="ns")

# Configure the canvas to use the scrollbar
canvas.configure(
        xscrollcommand=scroll_x,
        yscrollcommand=scroll_y)


def render_grid(event=None):
# Draw the row numbers
    x = cell_height / 1
    for col in range(num_cols):
        x += cell_width  # Start from the second column
        canvas.create_text(x + cell_width // 2, cell_height // 2, text=chr(65 + col), anchor="center")

    y = cell_height / 1
    for row in range(num_rows):
        y = (row + 1) * cell_height  # Start from the second row
        canvas.create_text(cell_width // 4, y + cell_height // 2, text=str(row + 1), anchor="center")

    canvas_width  = root.winfo_width()
    canvas_height  = root.winfo_height()

    # Draw the grid lines
    y = 0
    for row in range(1, num_rows + 2):
        y += cell_height
        canvas.create_line(cell_width, y, canvas_width, y, fill="gray")

    x = 0
    for col in range(1, num_cols + 2):
        x += cell_width
        print((x, cell_height, canvas_height))
        canvas.create_line(x, cell_height, x, canvas_height, fill="gray")

# Bind the scrollable area to the mouse wheel
canvas.bind("<Configure>", render_grid)
#canvas.bind_all("<MouseWheel>", lambda event: canvas.yview_scroll(int(-1 * (event.delta / 120)), "units"))


root.mainloop()

