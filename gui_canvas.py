import tkinter as tk
from spreadsheet import Worksheet

root = tk.Tk()
root.title("Spreadsheet")
root.geometry("1080x1080")
root.minsize(400,220)

root.update_idletasks()

# Define the number of rows and columns in the spreadsheet
num_rows = 30
num_cols = 5

worksheet = Worksheet()

font_spec = ('Arial', 22)

canvas_height = root.winfo_height()

# Calculate the width and height of each cell
cell_width = 150
cell_height = 50

col_header_height = cell_height
row_header_width  = cell_width // 2

first_cell_x = row_header_width
first_cell_y = col_header_height

entry_frame = tk.Frame(root)
entry_frame.pack(pady=5, fill='x', expand=False)

cell_name_text = tk.StringVar()

cell_name = tk.Entry(
        entry_frame,
        width=12,
        textvariable=cell_name_text,
        highlightthickness=1,
        highlightbackground="gray")
cell_name.pack(side='left', padx=(10,5))
cell_name.configure(font=font_spec)

cell_name_text.set('a1')

entry_text = tk.StringVar()

entry = tk.Entry(
        entry_frame,
        textvariable=entry_text,
        highlightthickness=1,
        highlightbackground="gray")
entry.pack(side='right', fill='both', expand=True, padx=(5,10))
entry.configure(font=font_spec)
entry.insert(0, "=a1+b2")

# Create a scrollable canvas
canvas_frame = tk.Frame(root)
canvas_frame.pack(fill='both', expand=True)
canvas_frame.grid_rowconfigure(1, weight=1)
canvas_frame.grid_columnconfigure(1, weight=1)

canvas = tk.Canvas(canvas_frame, height=canvas_height, bg="white")
canvas.grid(row=1, column=1, sticky="nsew")

cell_selection_text = tk.StringVar()
cell_selection = tk.Entry(root,
                          textvariable=cell_selection_text,
                          highlightthickness=1,
                          highlightbackground='gray')
cell_selection.configure(font=font_spec)
cell_selection.insert(0, "=a1+b2")
cell_selection.focus()
cell_selection_id = canvas.create_window(
        cell_width*2, cell_height*2,
        window=cell_selection,
        width=cell_width,
        height=cell_height,
        state=tk.HIDDEN)

canvas.coords(cell_selection_id,
              first_cell_x + cell_width  // 2,
              first_cell_y + cell_height // 2)



def mirror_text(event):
    if event.widget == entry:
        #print(f'entry: {event}')
        cell_selection_text.set(entry_text.get())
    elif event.widget == cell_selection:
        #print(f'cell: {event}')
        entry_text.set(cell_selection_text.get())
    else:
        print(f'else: {event}')


entry.bind('<KeyRelease>', mirror_text)
cell_selection.bind('<KeyRelease>', mirror_text)


def scroll_x(*args):
    #print(args)
    pass

def scroll_y(*args):
    #print(args)
    pass

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


def render_grid(from_row, from_col):
    x = first_cell_x
    for col in range(num_cols):
        canvas.create_text(x + cell_width // 2, cell_height // 2, text=chr(97 + col), anchor="center", font=font_spec)
        x += cell_width  # Start from the second column

    y = cell_height // 1
    for row in range(num_rows):
        y = (row + 1) * cell_height  # Start from the second row
        canvas.create_text(cell_width // 4, y + cell_height // 2, text=str(row + 1), anchor="center", font=font_spec)

    canvas_width  = root.winfo_width()
    canvas_height  = root.winfo_height()

    # Draw the grid lines
    y = 0
    for row in range(1, num_rows + 2):
        y += cell_height
        canvas.create_line(0, y, canvas_width, y, fill="gray")

    x = cell_width // 2
    for col in range(1, num_cols + 2):
        canvas.create_line(x, 0, x, canvas_height, fill="gray")
        x += cell_width


def render_values():
    cells = worksheet.render_cells(0, 0, 20, 20)
    for row in range(num_rows):
        for col in range(num_cols):
            #value = cells[col, row]

            cell_x = row_header_width  + (cell_width  * col)
            cell_y = col_header_height + (cell_height * row)
            
            cell_x += cell_width  // 32
            cell_y += cell_height // 2

            text = f'r{row+1}c{col+1}'
            canvas.create_text(
                    cell_x, cell_y,
                    text=text,
                    anchor="w",
                    font=font_spec)


def render_worksheet(event=None):
    render_grid(0, 0)
    render_values()


def cell_index(event):
    row = ((event.y + col_header_height) // cell_height) - 2
    col = ((event.x + row_header_width) // cell_width) - 1
    return row, col


def cell_name_a1_style(row, col):
    col_name = chr(97 + col)
    return col_name, row + 1


def click_canvas(event):
    #print(event)
    row, col = cell_index(event)
    #print((row,col))

    col_name, row_name = cell_name_a1_style(row, col)


    if (row, col) == (-1, -1):
        print('#')
        return
    elif row == -1:
        print(f'{col_name}:{col_name}')
        return
    elif col == -1:
        print(f'{row+1}:{row+1}')
        return

    name = f'{col_name}{row+1}'
    #print(name)

    cell_name_text.set(name)
    entry_text.set(f'cell formula: {name}')

    entry.focus()
    entry.icursor(tk.END)

    canvas.itemconfig(cell_selection_id, state=tk.HIDDEN)


def double_click_canvas(event):
    row, col = cell_index(event)
    col_name, row_name = cell_name_a1_style(row, col)

    #print((row,col))
    cell_x = row_header_width  + (cell_width  * col)
    cell_y = col_header_height + (cell_height * row)
    canvas.coords(cell_selection_id,
                  cell_x + cell_width // 2,
                  cell_y + cell_height // 2)

    cell_selection_text.set(f'{col_name}{row_name}')
    cell_selection.select_range(0, tk.END)
    cell_selection.icursor(tk.END)
    canvas.itemconfig(cell_selection_id, state=tk.NORMAL)


# Bind the scrollable area to the mouse wheel
canvas.bind("<Configure>", render_worksheet)
canvas.bind("<Button-1>", click_canvas)
canvas.bind("<Double-1>", double_click_canvas)
#canvas.bind_all("<MouseWheel>", lambda event: canvas.yview_scroll(int(-1 * (event.delta / 120)), "units"))

def escape(event):
    #print(event)
    canvas.itemconfig(cell_selection_id, state=tk.HIDDEN)
    root.focus_set()

root.bind('<Escape>', escape)

root.mainloop()

