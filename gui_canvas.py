import tkinter as tk
from spreadsheet import Worksheet

# TODO
# scrolling
# filters
# cut, copy and paste
# cell formating
# zoom

# select range with the mouse
# o insert row below
# O insert row above

# Ctrl+Space select column
# Shift+Space select row

# ctrl+arrow to jump to next data

# cell formatting
# ctrl+f find

# ctrl+n new workbook
# ctrl+o open workbook
# ctrl+s save workbook

root = tk.Tk()
root.title("Spreadsheet")
root.geometry("1080x1080")
root.minsize(400,220)

root.update_idletasks()

# Define the number of rows and columns in the spreadsheet
num_rows = 15
num_cols = 5

worksheet = Worksheet()
cells = None

font_spec = ('Arial', 22)
selection_colour = '#C1F2FA'

selected_cell_row = 0
selected_cell_col = 0

shift_mask = 0x0001
ctrl_mask  = 0x0004
alt_mask   = 0x0008

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

cell_name_text.set('')

formula_text = tk.StringVar()

formula_entry = tk.Entry(
        entry_frame,
        textvariable=formula_text,
        highlightthickness=1,
        highlightbackground="gray")
formula_entry.pack(side='right', fill='both', expand=True, padx=(5,10))
formula_entry.configure(font=font_spec)
formula_entry.insert(0, '')

# Create a scrollable canvas
canvas_frame = tk.Frame(root)
canvas_frame.pack(fill='both', expand=True)
canvas_frame.grid_rowconfigure(1, weight=1)
canvas_frame.grid_columnconfigure(1, weight=1)

canvas = tk.Canvas(canvas_frame, height=canvas_height, bg="white")
canvas.grid(row=1, column=1, sticky="nsew")

cell_formula_text = tk.StringVar()
cell_formula = tk.Entry(root,
                          textvariable=cell_formula_text,
                          highlightthickness=1,
                          highlightbackground='gray')
cell_formula.configure(font=font_spec)
cell_formula.insert(0, '')
cell_formula.focus()
cell_formula_id = canvas.create_window(
        cell_width*2, cell_height*2,
        window=cell_formula,
        width=cell_width,
        height=cell_height,
        state=tk.HIDDEN)

canvas.coords(cell_formula_id,
              first_cell_x + cell_width  // 2,
              first_cell_y + cell_height // 2)


cell_selection_id = canvas.create_rectangle(
        50, 100, 250, 200,
        fill=selection_colour,
        tags=('selection',),
        state=tk.HIDDEN)


def mirror_text(event):
    if event.widget == formula_entry:
        #print(f'formula: {event}')
        cell_formula_text.set(formula_text.get())
    elif event.widget == cell_formula:
        #print(f'cell: {event}')
        formula_text.set(cell_formula_text.get())
    else:
        print(f'else: {event}')

    return 'break'


def formula_on_enter(event):
    formula =  formula_text.get()
    set_formula(selected_cell_row, selected_cell_col, formula)
    select_cell(selected_cell_row, selected_cell_col)
    return "break"


def formula_on_tab(event):
    root.focus()
    return "break"

def cell_formula_on_enter(event):
    formula =  formula_text.get()
    set_formula(selected_cell_row, selected_cell_col, formula)
    shift_pressed = event.state & shift_mask
    offset = -1 if shift_pressed else 1
    edit_cell(selected_cell_row + offset, selected_cell_col)
    return "break"

def cell_formula_on_tab(event):
    formula =  formula_text.get()
    set_formula(selected_cell_row, selected_cell_col, formula)
    shift_pressed = event.state & shift_mask
    offset = -1 if shift_pressed else 1
    edit_cell(selected_cell_row, selected_cell_col + offset)
    return "break"


formula_entry.bind('<Return>', formula_on_enter)
cell_formula.bind('<Return>', cell_formula_on_enter)

formula_entry.bind('<Tab>', formula_on_tab)
cell_formula.bind('<Tab>', cell_formula_on_tab)

formula_entry.bind('<KeyRelease>', mirror_text)
cell_formula.bind('<KeyRelease>', mirror_text)


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
    global cells
    cells = []
    new_cells = worksheet.render_cells(0, 0, num_cols, num_rows)
    for row in range(num_rows):
        row_cells = []
        for col in range(num_cols):
            #value = cells[col, row]

            cell_x = row_header_width  + (cell_width  * col)
            cell_y = col_header_height + (cell_height * row)
            
            cell_x += cell_width  // 32
            cell_y += cell_height // 2

            text = worksheet.get_value(row, col)
            text = new_cells[row][col]

            cell_id = canvas.create_text(
                    cell_x, cell_y,
                    text=text,
                    anchor="w",
                    font=font_spec)
            row_cells.append(cell_id)
        cells.append(row_cells)

    #cell_id = cells[4][4]
    #canvas.itemconfig(cell_id, text='hello')


def set_formula(row, col, formula):
    changes = worksheet.set_formula(row, col, formula)
    #print(changes)
    for change in changes:
        (row, col), new_value = change
        cell_id = cells[row][col]
        canvas.itemconfig(cell_id, text=new_value)


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

    select_cell(row, col)


def double_click_canvas(event):
    row, col = cell_index(event)
    edit_cell(row, col)


def edit_cell(row, col):
    global selected_cell_row
    global selected_cell_col

    row = max(0, min(row, num_rows - 1))
    col = max(0, min(col, num_cols - 1))

    selected_cell_row = row
    selected_cell_col = col

    col_name, row_name = cell_name_a1_style(row, col)

    #print((row,col))
    cell_x = row_header_width  + (cell_width  * col)
    cell_y = col_header_height + (cell_height * row)
    canvas.coords(cell_formula_id,
                  cell_x + cell_width // 2,
                  cell_y + cell_height // 2)


    cell_name_text.set(f'{col_name}{row_name}')
    formula = worksheet.get_formula(row, col)
    cell_formula_text.set(formula)

    cell_formula.select_range(0, tk.END)
    cell_formula.icursor(tk.END)

    canvas.itemconfig(cell_selection_id, state=tk.HIDDEN)
    canvas.itemconfig(cell_formula_id, state=tk.NORMAL)
    cell_formula.focus()


def select_cell(row, col):
    global selected_cell_row
    global selected_cell_col

    row = max(0, min(row, num_rows - 1))
    col = max(0, min(col, num_cols - 1))

    canvas.itemconfig(cell_formula_id, state=tk.HIDDEN)

    selected_cell_row = row
    selected_cell_col = col

    cell_x = row_header_width  + (cell_width  * col)
    cell_y = col_header_height + (cell_height * row)
    canvas.coords(cell_selection_id,
                  cell_x, cell_y,
                  cell_x + cell_width, cell_y + cell_height)
    canvas.itemconfig(cell_selection_id, state=tk.NORMAL)

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

    formula = worksheet.get_formula(row, col)
    cell_name_text.set(name)
    formula_text.set(formula)

    formula_entry.icursor(tk.END)

    root.focus()


def move_cursor(event):
    if event.widget != root:
        return

    shift_pressed = event.state & shift_mask
    ctrl_pressed  = event.state & ctrl_mask
    alt_pressed   = event.state & alt_mask

    #print(event)

    if shift_pressed:
        if event.keysym == 'Tab':
            x, y = -1, 0
        elif event.keysym == 'Return':
            x, y = 0, -1
        else:
            return "break"
    elif ctrl_pressed:
        return "break"
    elif alt_pressed:
        return "break"
    else:
        if event.keysym == 'h':
            x, y = -1, 0
        elif event.keysym == 'j':
            x, y = 0, 1
        elif event.keysym == 'k':
            x, y = 0, -1
        elif event.keysym == 'l':
            x, y = 1, 0
        elif event.keysym == 'Tab':
            x, y = 1, 0
        elif event.keysym == 'Return':
            x, y = 0, 1
        else:
            return "break"

    row, col = selected_cell_row, selected_cell_col

    row += y
    col += x

    select_cell(row, col)

    return "break"


def edit_cursor(event):
    if event.widget != root:
        return
    edit_cell(selected_cell_row, selected_cell_col)

render_worksheet()

# Bind the scrollable area to the mouse wheel
#canvas.bind("<Configure>", render_worksheet)
canvas.bind("<Button-1>", click_canvas)
canvas.bind("<Double-1>", double_click_canvas)
#canvas.bind_all("<MouseWheel>", lambda event: canvas.yview_scroll(int(-1 * (event.delta / 120)), "units"))

def escape(event):
    #print(event)
    #canvas.itemconfig(cell_formula_id, state=tk.HIDDEN)
    select_cell(selected_cell_row, selected_cell_col)
    root.focus_set()

root.bind('<Escape>', escape)

root.bind('<Return>', move_cursor)
root.bind('<Tab>', move_cursor)
root.bind('h', move_cursor)
root.bind('j', move_cursor)
root.bind('k', move_cursor)
root.bind('l', move_cursor)
root.bind('i', edit_cursor)


select_cell(0, 0)
#set_formula(0, 0, '1')
set_formula(1, 1, '2')
set_formula(1, 0, 'b2')
#set_formula(2, 0, 'a2')
#set_formula(3, 0, 'sum(a1:a3)')
#exit()

root.mainloop()

