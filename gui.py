import platform
import tkinter as tk
import subprocess
from tkinter import ttk
from spreadsheet import Worksheet

# Done
# alt + =  autosum

# TODO

# default formatting for formula
# default formatting for raw value

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

# ctrl+d fill down
# ctrl+r fill right


# insert selection into formula

# custom cell size
# custom cell format
# custom number format

root = tk.Tk()
root.title("Spreadsheet")
root.geometry("1080x1080")
root.minsize(400,220)

root.update_idletasks()

# Define the number of rows and columns in the spreadsheet
number_of_visible_rows = 60
number_of_visible_cols = 10

worksheet = Worksheet()
cells = None

font_spec = ('Consolas', 22)

style = ttk.Style()

system = platform.system()
#print(f'{system=}')

def macosx_is_darkmode():
    try:
        result = subprocess.run(
                ['defaults', 'read', '-g', 'AppleInterfaceStyle'],
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True)
        return 'Dark' in result.stdout
    except subprocess.CalledProcessError:
        return False


match system:
    case 'Windows':
        spreadsheet_background_colour = '#fffafa'
        cell_selection_fill = 'white'
        cell_selection_outline = '#444'
        #range_selection_colour = 'systemInfoBackground'
        range_selection_colour = 'lightblue'
    case 'Darwin':
        if macosx_is_darkmode():
            spreadsheet_background_colour = '#444'
            cell_selection_fill = '#222'
            cell_selection_outline = '#444'
            range_selection_colour = '#449'
        else:
            cell_selection_fill = 'white'
            cell_selection_outline = '#444'
            range_selection_colour = 'lightblue'
    case _:
        raise ValueError(f'unknown {system=}')

cursor_mode = 'excel'

row_headers = []
col_headers = []

viewport_offset_row = 0
viewport_offset_col = 0

viewport_width  = 6
viewport_height = 19

viewport_max_row = 20
viewport_max_col = 6

selected_cell_row = 0
selected_cell_col = 0

selected_range = None

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

entry_frame = ttk.Frame(root)
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

status_bar_text = tk.StringVar()
status_bar_text.set('vim normal')

status_bar = tk.Label(
        root,
        textvariable=status_bar_text,
        bd=1,
        relief=tk.SUNKEN,
        anchor=tk.E,
        padx=5,
        pady=5)
status_bar.pack(side=tk.BOTTOM, fill=tk.X)

# Create a scrollable canvas
canvas_frame = tk.Frame(root)
canvas_frame.pack(fill='both', expand=True)
canvas_frame.grid_rowconfigure(1, weight=1)
canvas_frame.grid_columnconfigure(1, weight=1)

canvas = tk.Canvas(
        canvas_frame,
        height=canvas_height,
        background=spreadsheet_background_colour)
canvas.grid(row=1, column=1, sticky="nsew")

cell_formula_text = tk.StringVar()
cell_formula = tk.Entry(root,
                          textvariable=cell_formula_text,
                          highlightthickness=1,
                          highlightbackground='red')
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


range_selection_id = canvas.create_rectangle(
        50, 100, 250, 200,
        fill=range_selection_colour,
        tags=('range-selection',),
        state=tk.HIDDEN)



cell_selection_id = canvas.create_rectangle(
        50, 100, 250, 200,
        fill=cell_selection_fill,
        outline=cell_selection_outline,
        width=3,
        tags=('cell-selection',),
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
    row, col = get_row_col('cell_selection', 'worldspace')
    set_formula(row, col, formula)
    select_cell(row, col)
    return "break"


def formula_on_tab(event):
    root.focus()
    return "break"

def cell_formula_on_enter(event):
    row, col = get_row_col('cell_selection', 'worldspace')

    formula =  formula_text.get()
    set_formula(row, col, formula)

    shift_pressed = event.state & shift_mask
    offset = -1 if shift_pressed else 1
    edit_cell(row + offset, col)
    return "break"

def cell_formula_on_tab(event):
    row, col = get_row_col('cell_selection', 'worldspace')

    formula =  formula_text.get()
    set_formula(row, col, formula)
    shift_pressed = event.state & shift_mask
    offset = -1 if shift_pressed else 1
    edit_cell(row, col + offset)
    return "break"


formula_entry.bind('<Return>', formula_on_enter)
cell_formula.bind('<Return>', cell_formula_on_enter)

formula_entry.bind('<Tab>', formula_on_tab)
cell_formula.bind('<Tab>', cell_formula_on_tab)

formula_entry.bind('<KeyRelease>', mirror_text)
cell_formula.bind('<KeyRelease>', mirror_text)


def scroll_x(*args):
    print(args)
    pass

def scroll_y(*args):
    #print(args)
    match args:
        case 'moveto', offset:
            offset = float(offset)
            new_offset_rows = int(viewport_max_row * offset)
            update_scroll(new_offset_rows, viewport_offset_col)
        case 'scroll', offset, 'pages':
            page_size = 10
            offset = int(offset) * page_size
            new_offset_rows = viewport_offset_row + offset
            update_scroll(new_offset_rows, viewport_offset_col)
        case _:
            raise ValueError(f'{args=}')

# Create a horizontal scrollbar
scrollbar_x = tk.Scrollbar(canvas_frame, orient="horizontal", command=scroll_x)
scrollbar_x.grid(row=2, column=1, sticky="ew")
scrollbar_x.set(0.0, 0.5)

# Create a vertical scrollbar
scrollbar_y = tk.Scrollbar(canvas_frame, orient="vertical", command=scroll_y)
scrollbar_y.grid(row=1, column=2, sticky="ns")
scrollbar_y.set(0.0, 0.5)

def render_headers():
    x = first_cell_x
    for col in range(number_of_visible_cols):
        col_id = canvas.create_text(x + cell_width // 2, cell_height // 2, text=chr(97 + col), anchor="center", font=font_spec)
        col_headers.append(col_id)
        x += cell_width  # Start from the second column

    y = cell_height // 1
    for row in range(number_of_visible_rows):
        y = (row + 1) * cell_height  # Start from the second row
        row_id = canvas.create_text(cell_width // 4, y + cell_height // 2, text=str(row + 1), anchor="center", font=font_spec)
        row_headers.append(row_id)


def update_headers():
    row = viewport_offset_row
    col = viewport_offset_col

    for row_id in row_headers:
        canvas.itemconfig(row_id, text=str(row + 1))
        row += 1

    for col_id in col_headers:
        canvas.itemconfig(col_id, text=chr(97 + col))
        col += 1


def render_grid():
    canvas_width  = root.winfo_width()
    canvas_height  = root.winfo_height()

    # Draw the grid lines
    y = 0
    for row in range(1, number_of_visible_rows + 2):
        y += cell_height
        canvas.create_line(0, y, canvas_width*2, y, fill="gray")

    x = cell_width // 2
    for col in range(1, number_of_visible_cols + 2):
        canvas.create_line(x, 0, x, canvas_height*2, fill="gray")
        x += cell_width


def create_cells():
    global cells
    cells = []
    new_cells = worksheet.render_cells(0, 0, number_of_visible_cols, number_of_visible_rows)
    for row in range(number_of_visible_rows):
        row_cells = []
        for col in range(number_of_visible_cols):
            #value = cells[col, row]

            cell_x = row_header_width  + (cell_width  * col)
            cell_y = col_header_height + (cell_height * row)
            
            cell_x += cell_width  // 32
            cell_y += cell_height // 2

            text = new_cells[row][col]

            cell_id = canvas.create_text(
                    cell_x, cell_y,
                    text=text,
                    anchor="w",
                    font=font_spec)
            row_cells.append(cell_id)
        cells.append(row_cells)


def update_cells():
    new_cells = worksheet.render_cells(
        viewport_offset_col, viewport_offset_row,
        number_of_visible_cols, number_of_visible_rows)

    for row in range(number_of_visible_rows):
        row_cells = []
        for col in range(number_of_visible_cols):
            cell_id = cells[row][col]
            new_text = new_cells[row][col]
            if new_text is None:
                new_text = ''
            canvas.itemconfig(cell_id, text=new_text)


def get_row_col(name, space):
    match name:
        case 'cell_selection':
            row, col = selected_cell_row, selected_cell_col
        case 'selected_range_from':
            [row1, col1], [row2, col2] = selected_range
            row, col = row1, col1
        case 'selected_range_to':
            [row1, col1], [row2, col2] = selected_range
            row, col = row2, col2
        case 'viewport_from':
            row, col = viewport_offset_row, viewport_offset_col
        case 'viewport_to':
            row, col = viewport_offset_row, viewport_offset_col
            row += viewport_height
            col += viewport_width
        case _:
            raise ValueError(f'{name=} {space=}')

    match space:
        case 'screenspace':
            row -= viewport_offset_row
            col -= viewport_offset_col
        case 'worldspace':
            pass
        case _:
            raise ValueError(f'{name=} {space=}')

    return row, col


def get_xy(name, space):
    row, col = get_row_col(name, space)

    x = row_header_width   + (cell_width  * col)
    y = col_header_height  + (cell_height  * row)
    return x, y


def get_rect_row_col(name, space):
    match name:
        case 'selected_range':
            row1, col1 = get_row_col('selected_range_from', space)
            row2, col2 = get_row_col('selected_range_to',   space)
        case 'viewport':
            row1, col1 = get_row_col('viewport_from', space)
            row2, col2 = get_row_col('viewport_to',   space)
        case _:
            raise ValueError(f'{name=} {space=}')

    return (row1, col1), (row2, col2)


def get_rect_xy(name, space):
    if name != 'selected_range':
        assert False

    x1, y1 = get_xy('selected_range_from', space)
    x2, y2 = get_xy('selected_range_to',   space)

    x2 += cell_width
    y2 += cell_height

    return (x1, y1), (x2, y2)

    #x1 = row_header_width  + (cell_width  * col1)
    #y1 = col_header_height + (cell_height * row1)

    #x2 = row_header_width  + (cell_width  * col2) + cell_width
    #y2 = col_header_height + (cell_height * row2) + cell_height


def update_selection():
    # cell formula
    # cell selection
    # range selection

    cell_x, cell_y = get_xy('cell_selection', 'screenspace')

    if cell_y == 0:
        cell_y -= col_header_height

    canvas.coords(cell_formula_id,
                  cell_x + cell_width // 2,
                  cell_y + cell_height // 2)

    canvas.coords(cell_selection_id,
                  cell_x, cell_y,
                  cell_x + cell_width, cell_y + cell_height)


    if selected_range is None:
        print('no selection')
        return

    render_range_selection()


def set_formula(row, col, formula):

    changes = worksheet.set_formula(row, col, formula)
    #print(changes)
    for change in changes:
        (row, col), new_value = change
        row -= viewport_offset_row
        col -= viewport_offset_col
        cell_id = cells[row][col]
        canvas.itemconfig(cell_id, text=new_value)


def render_worksheet(event=None):
    render_grid()
    render_headers()
    create_cells()


def cell_index(event, space):
    row = ((event.y + col_header_height) // cell_height) - 2
    col = ((event.x + row_header_width) // cell_width) - 1

    if space == 'worldspace':
        row += viewport_offset_row
        col += viewport_offset_col

    return row, col


def cell_name_a1_style(row, col):
    col_name = chr(97 + col)
    return col_name, row + 1


def range_name_a1_style(row1, col1, row2, col2):
    col_name1, row_name1 = cell_name_a1_style(row1, col1)
    col_name2, row_name2 = cell_name_a1_style(row2, col2)

    lhs = f'{col_name1}{row_name1}'
    rhs = f'{col_name2}{row_name2}'

    if lhs == rhs:
        text = lhs
    else:
        text = lhs + ':' + rhs

    return text


def click_canvas(event):
    cf = canvas.itemconfig(cell_formula_id)
    state = cf['state'][4]

    if state == 'normal':
        cell_formula_on_enter(event)

    #print(event)
    row, col = cell_index(event, 'worldspace')
    #print((row,col))

    select_cell(row, col)


def press_canvas(event):
    #print('press')
    click_canvas(event)
    motion_canvas(event)
    canvas.itemconfig(range_selection_id, state=tk.NORMAL)


def release_canvas(event):
    pass


def motion_canvas(event):
    global selected_range

    row1, col1 = cell_index(event, 'worldspace')
    row2, col2 = selected_cell_row, selected_cell_col

    #row1 = max(0, min(row1, number_of_visible_rows - 1))
    #row2 = max(0, min(row2, number_of_visible_rows - 1))
    #col1 = max(0, min(col1, number_of_visible_cols - 1))
    #col2 = max(0, min(col2, number_of_visible_cols - 1))

    if row1 > row2:
        row1, row2 = row2, row1

    if col1 > col2:
        col1, col2 = col2, col1

    selected_range = [[row1, col1], [row2, col2]]

    render_range_selection()

    (row1, col1), (row2, col2) = get_rect_row_col('selected_range', 'worldspace')

    text = range_name_a1_style(row1, col1, row2, col2)

    cell_name_text.set(text)


def render_range_selection():
    if selected_range is None:
        return

    (row1, col1), (row2, col2) = get_rect_row_col('selected_range', 'worldspace')

    (x1, y1), (x2, y2) = get_rect_xy('selected_range', 'screenspace')

    if y2 <= col_header_height:
        (x1, y1), (x2, y2) = (0, 0), (0, 0)
        #canvas.itemconfig(range_selection_id, state=tk.HIDDEN)
    
    if y1 <= col_header_height:
        y1 = col_header_height

    canvas.coords(range_selection_id,
                  x1, y1,
                  x2, y2)



def scroll_canvas(event):
    if event.delta > 0:
        row_offset = -4
    else:
        row_offset = +4

    update_scroll(viewport_offset_row + row_offset, viewport_offset_col)


def update_scroll(row, col):
    global viewport_offset_row
    global viewport_offset_col
    global viewport_max_row
    global viewport_max_col

    #print((row, col))

    viewport_offset_row = row
    viewport_offset_col = col

    viewport_offset_row = max(viewport_offset_row, 0)
    viewport_offset_col = max(viewport_offset_col, 0)

    (row1, col1), (row2, col2) = get_rect_row_col('viewport', 'worldspace')
    #print((row1, col1), (row2, col2))

    if row2 > viewport_max_row:
        viewport_max_row = row2

    if col2 > viewport_max_col:
        viewport_max_col = col2

    first = row1 / viewport_max_row
    last  = row2 / viewport_max_row

    #print((first, last))

    scrollbar_y.set(first, last)

    update_headers()
    update_cells()
    update_selection()


def double_click_canvas(event):
    row, col = cell_index(event, 'worldspace')
    edit_cell(row, col)
    #print('double')


def edit_cell(row, col):
    global selected_cell_row
    global selected_cell_col

    #row = max(0, min(row, number_of_visible_rows - 1))
    #col = max(0, min(col, number_of_visible_cols - 1))

    select_cell(row, col)

    col_name, row_name = cell_name_a1_style(row, col)

    cell_x, cell_y = get_xy('cell_selection', 'screenspace')
    canvas.coords(cell_formula_id,
                  cell_x + cell_width // 2,
                  cell_y + cell_height // 2)

    status_bar_text.set('vim insert')

    cell_name_text.set(f'{col_name}{row_name}')
    formula = worksheet.get_formula(row, col)
    cell_formula_text.set(formula)

    cell_formula.select_range(0, tk.END)
    cell_formula.icursor(tk.END)

    canvas.itemconfig(range_selection_id, state=tk.HIDDEN)
    canvas.itemconfig(cell_selection_id, state=tk.HIDDEN)
    canvas.itemconfig(cell_formula_id, state=tk.NORMAL)
    cell_formula.focus()


def select_cell(row, col):
    global selected_cell_row
    global selected_cell_col

    #print((row, col))

    #row = max(0, min(row, number_of_visible_rows - 1))
    col = max(0, min(col, number_of_visible_cols - 1))

    select_range(row, col, row, col)

    status_bar_text.set('vim normal')

    canvas.itemconfig(cell_formula_id, state=tk.HIDDEN)

    selected_cell_row = row
    selected_cell_col = col


    cell_x, cell_y = get_xy('cell_selection', 'screenspace')

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


def select_range(row1, col1, row2, col2):
    global selected_range

    selected_range = (row1, col1), (row2, col2)
    canvas.itemconfig(range_selection_id, state=tk.NORMAL)

    render_range_selection()


def move_cursor(event):
    if event.widget != root:
        return

    shift_pressed = event.state & shift_mask
    ctrl_pressed  = event.state & ctrl_mask
    alt_pressed   = event.state & alt_mask

    # print(event)

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
        elif event.keysym == 'Up':
            x, y = 0, -1
        elif event.keysym == 'Down':
            x, y = 0, 1
        elif event.keysym == 'Left':
            x, y = -1, 0
        elif event.keysym == 'Right':
            x, y = 1, 0
        elif event.keysym == 'Tab':
            x, y = 1, 0
        elif event.keysym == 'Return':
            x, y = 0, 1
        else:
            return "break"

    row, col = get_row_col('cell_selection', 'worldspace')
    #print((row, col))

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
canvas.bind("<ButtonPress-1>", press_canvas)
canvas.bind("<ButtonRelease-1>", release_canvas)
canvas.bind("<B1-Motion>", motion_canvas)
canvas.bind("<MouseWheel>", scroll_canvas)

canvas.bind("<Double-1>", double_click_canvas)
#canvas.bind_all("<MouseWheel>", lambda event: canvas.yview_scroll(int(-1 * (event.delta / 120)), "units"))

root.update()

def escape(event):
    #print(event)
    #canvas.itemconfig(cell_formula_id, state=tk.HIDDEN)
    select_cell(selected_cell_row, selected_cell_col)
    root.focus_set()

cell_formula.bind('<Escape>', escape)

def on_keypress(event):
    if event.widget != root:
        return

    #print(event)

    #print(cursor_mode)
    match cursor_mode:
        case 'excel':
            return on_keypress_excel(event)
        case 'vim':
            return on_keypress_vim(event)
        case _:
            assert False


def on_keypress_excel(event):
    #print(event)
    match event.keysym:
        case 'Escape':
            return escape(event)
        case 'Tab' | 'Return' | 'Up' | 'Down' | 'Left' | 'Right':
            return move_cursor(event)
        case 'BackSpace' | 'Delete':
            pass
        case 'Prior' | 'Next':
            pass
        case 'Control_L' | 'Control_R' | 'Alt_L' | 'Alt_R':
            pass
        case 'Alt_L' | 'Alt_R':
            pass
        case 'Shift_L' | 'Shift_R':
            pass
        case 'equal':
            row, col = get_row_col('cell_selection', 'worldspace')
            autosum_formula = 'sum above'
            set_formula(row, col, autosum_formula)
            select_cell(row, col)
            return None
        case _:
            pass

    if event.char == '':
        #print(event)
        return

    edit_cell(selected_cell_row, selected_cell_col)
    cell_formula_text.set(event.char)
    cell_formula.select_range(tk.END, tk.END)
    cell_formula.icursor(tk.END)


def on_keypress_vim(event):
    #print(event)
    match event.keysym:
        case 'Escape':
            return escape(event)
        case 'Tab' | 'Return' | 'h' | 'j'| 'k' | 'l' | 'Up' | 'Down' | 'Left' | 'Right':
            return move_cursor(event)
        case 'i':
            return edit_cursor(event)
        case _:
            pass


root.bind('<KeyPress>', on_keypress)


def on_copy(event=None):
    (row1, col1), (row2, col2) = get_rect_row_col('selected_range', 'worldspace')
    #print( (row1, col1), (row2, col2) )

    num_selected_cols = col2 - col1 + 1
    num_selected_rows = row2 - row1 + 1
    #print((num_selected_rows, num_selected_cols))


    new_cells = worksheet.render_cells(
            col1, row1,
            num_selected_cols,
            num_selected_rows,
            )
    #print(new_cells)

    lines = []
    for row in new_cells:
        #print(row)
        line = '\t'.join('' if cell_value is None else str(cell_value) for cell_value in row)
        lines.append(line)


    tsv = '\n'.join(lines)
    #print(repr(tsv))

    root.clipboard_clear()
    root.clipboard_append(tsv)

    return 'break'


def on_paste(event=None):
    text = root.clipboard_get()
    #print(repr(text))

    if '\t' in text:
        clipboard_rows = tsv_to_list(text)
    elif ',' in text:
        clipboard_rows = csv_to_list(text)
    elif '\n' in text: # handle single column
        clipboard_rows = text.strip('\n').split('\n')
    else:
        clipboard_rows = [[text.strip('\n')]]

    #print(clipboard_rows)

    row = selected_cell_row


    cell = clipboard_rows[0][0]
    s = parse_number(cell)
    formula_text.set(s)

    for clipboard_row in clipboard_rows:
        col = selected_cell_col
        for cell in clipboard_row:
            #print((row, col, cell))
            s = parse_number(cell)
            set_formula(row, col, s)
            col += 1
        row += 1


root.bind('<Control-c>', on_copy)
root.bind('<Command-c>', on_copy)

root.bind('<Control-v>', on_paste)
root.bind('<Command-v>', on_paste)


set_formula(1, 1, '1')
set_formula(1, 2, '2')
set_formula(2, 1, '3')
set_formula(2, 2, '4')
set_formula(3, 1, '5')
set_formula(3, 2, '6')
set_formula(4, 1, 'sum above')

select_cell(0, 0)
select_cell(4, 1)
#edit_cell(0, 1)
#set_formula(0, 0, '1')
#set_formula(1, 1, '2')
#set_formula(1, 0, 'b2')
#set_formula(2, 0, 'a2')
#set_formula(3, 0, 'sum(a1:a3)')
#exit()


def tsv_to_list(t):
    lines = t.strip().split('\n')
    elems = [[None if c == '' else c for c in line.split('\t')] for line in lines]
    return elems


def csv_to_list(t):
    lines = t.strip().split('\n')
    elems = [line.split(',') for line in lines]
    return elems


def parse_number(s):
    if s is None:
        return None

    s = s.strip()
    if s.startswith('£'):
        s = s[1:]

    try:
        i = int(s)
        return s
    except ValueError:
        pass

    try:
        f = float(s)
        return s
    except ValueError:
        pass

    return repr(s)


#root.bind('<Double-1>', lambda e: print(e))
root.mainloop()


