import tkinter as tk

root = tk.Tk()
root.title("Spreadsheet")
root.geometry("800x600")

# Define the number of rows and columns in the spreadsheet
num_rows = 15
num_cols = 5

canvas_width = 800
canvas_height = 600

# Calculate the width and height of each cell
cell_width = canvas_width // (num_cols + 1)  # +1 for column names
cell_height = canvas_height // (num_rows + 1)  # +1 for row numbers

entry_frame = tk.Frame(root)
entry_frame.pack(pady=10, fill='x', expand=False)

entry = tk.Entry(
        entry_frame,
        width=10,
        highlightthickness=2,
        highlightbackground="gray")
entry.pack(fill="both", expand=True)

# Configure the font size of the entry widget
entry.configure(font=("Arial", 28))

# Create a scrollable canvas
canvas_frame = tk.Frame(root)
canvas_frame.pack(fill='both', expand=True)
canvas_frame.grid_rowconfigure(1, weight=1)
canvas_frame.grid_columnconfigure(1, weight=1)

row_numbers_canvas = tk.Canvas(canvas_frame, width=cell_width//2, height=canvas_height, bg="white")
row_numbers_canvas.grid(row=1, column=0, sticky="ns")

column_headers_canvas = tk.Canvas(canvas_frame, width=canvas_width, height=cell_height, bg="white")
column_headers_canvas.grid(row=0, column=1, sticky="ew")

canvas = tk.Canvas(canvas_frame, width=canvas_width, height=canvas_height, bg="white")
canvas.grid(row=1, column=1, sticky="nsew")

# Create a horizontal scrollbar
scrollbar_x = tk.Scrollbar(canvas_frame, orient="horizontal", command=canvas.xview)
scrollbar_x.grid(row=2, column=1, sticky="ew")

# Create a vertical scrollbar
scrollbar_y = tk.Scrollbar(canvas_frame, orient="vertical", command=canvas.yview)
scrollbar_y.grid(row=1, column=2, sticky="ns")

# Configure the canvas to use the scrollbar
canvas.configure(
        xscrollcommand=scrollbar_x.set,
        yscrollcommand=scrollbar_y.set)

# Create a frame inside the canvas to hold the contents
canvas_frame_inner = tk.Frame(canvas)
canvas.create_window((0, 0), window=canvas_frame_inner, anchor="nw")

# Bind the scrollable area to the mouse wheel
canvas_frame_inner.bind("<Configure>", lambda event: canvas.configure(scrollregion=canvas.bbox("all")))
canvas.bind_all("<MouseWheel>", lambda event: canvas.yview_scroll(int(-1 * (event.delta / 120)), "units"))

# Draw the row numbers
for row in range(num_rows):
    y = (row + 1) * cell_height  # Start from the second row
    row_numbers_canvas.create_text(cell_width // 4, y + cell_height // 2, text=str(row + 1), anchor="center")

# Draw the column names
for col in range(num_cols):
    x = (col + 1) * cell_width  # Start from the second column
    column_headers_canvas.create_text(x + cell_width // 2, cell_height // 2, text=chr(65 + col), anchor="center")

# Draw the grid lines
for row in range(1, num_rows + 1):
    y = row * cell_height
    canvas.create_line(cell_width, y, canvas_width, y, fill="gray")

for col in range(1, num_cols + 1):
    x = col * cell_width
    canvas.create_line(x, cell_height, x, canvas_height, fill="gray")

root.mainloop()
