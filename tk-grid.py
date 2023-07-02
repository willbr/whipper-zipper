import re

import tkinter as tk
from tkinter import font
from dataclasses import dataclass
from typing import Any

number_of_rows    = 20
number_of_columns = 7

window = tk.Tk()
window.title('Grid Test')

default_font = font.nametofont('TkDefaultFont')
default_font.configure(family='Consolas', size=14)

window.option_add("*Font", default_font)
window.configure(padx=5, pady=5)

formula_frame = tk.Frame(window)
formula_frame.pack(side='top', fill='x')

cell_name = tk.Entry(formula_frame)
cell_name.pack(side='left')
cell_name.insert(0, 'cell_name')

formula_entry = tk.Entry(formula_frame)
formula_entry.pack(side='left', expand=True, fill='x')
formula_entry.insert(0, 'formula_entry')

worksheet = tk.Frame(window)
worksheet.pack(anchor='nw')

rows = []

def get_rc(widget):
    r = int(widget.grid_info()['row'])
    c = int(widget.grid_info()['column'])
    return (r, c)

def on_enter(event):
    select_cell_by_offset(event.widget, 0, 1)

resizing = False
def on_resize(event):
    global resizing
    if event.widget != window:
        return

    if resizing:
       return

    resizing = True

    window.update_idletasks()

    new_size = max(12, int(window.winfo_width() / 60))

    #default_font.configure(family='Consolas', size=new_size)

    window.update()

    resizing = False


def select_cell_by_offset(widget, x, y):
    r, c = get_rc(widget)

    next_row = r + y
    next_col = c + x

    next_row %= len(rows)
    next_col %= len(columns)

    next_widget = rows[next_row-1][next_col-1]
    next_widget.focus_set()


def move_cursor(event):
    if event.keysym == 'h':
        x, y = -1, 0
    elif event.keysym == 'j':
        x, y = 0, 1
    elif event.keysym == 'k':
        x, y = 0, -1
    elif event.keysym == 'l':
        x, y = 1, 0
    else:
        return

    select_cell_by_offset(event.widget, x, y)


window.bind('<Return>', on_enter)
#window.bind('<Escape>', lambda e: window.focus())
#window.bind('<Escape>', lambda e: exit(0))
window.bind('<Control-h>', move_cursor)
window.bind('<Control-j>', move_cursor)
window.bind('<Control-k>', move_cursor)
window.bind('<Control-l>', move_cursor)
window.bind('<Configure>', on_resize)

def on_enter(event):
    widget = event.widget
    widget.configure(background='lightblue')

    r, c = get_rc(widget)
    cell_name.delete(0, tk.END)
    cell_name.insert(0, cellname(r, c))

    formula = getattr(widget, 'formula', None)
    if formula is None:
        formula_entry.delete(0, tk.END)
        formula_entry.insert(0, "")
        return
    #print(f'{formula=}')

    formula_entry.delete(0, tk.END)
    formula_entry.insert(0, formula)

    widget.delete(0, tk.END)
    widget.insert(0, formula)
    widget.selection_range(0, 'end')
    widget.icursor('end')


def is_number(s):
    try:
        f = float(s)
        return True
    except ValueError:
        pass
    except TypeError:
        pass

    try:
        i = int(s)
        return True
    except ValueError:
        pass
    except TypeError:
        pass

    return False

#print(is_number('3.14'))
#print(is_number('10'))

@dataclass
class TestSpec:
    input_value: Any
    expected_result: Any

def to_rc(s):
    m = re.match('^(\w+?)(\d+)$' , s)
    s = m.groups()
    col = ord(s[0]) - ord('a') + 1
    row = int(s[1]) 
    return (row, col)

def test__to_rc():
    tests = [
            TestSpec('a1', (1, 1)),
            TestSpec('b2', (2, 2)),
            ]
    for test in tests:
        print(test)
        test_result = to_rc(test.input_value)
        if test_result != test.expected_result:
            print(f'{test.input_value=}, {test.expected_result=}, {test_result=}')
            assert False

test__to_rc()


def cellname(r, c):
    lhs = chr(ord('a') + c - 1)
    return f'{lhs}{r}'

i = (1, 1)
er = 'a1'
r = cellname(*i)
if r != er:
    print(f'{i=}, {er=}, {r=}')
    assert False

i = (2, 2)
er = 'b2'
r = cellname(*i)
if r != er:
    print(f'{i=}, {er=}, {r=}')
    assert False

def resolve_range_refs(s):
    matched = re.sub(r'(\w+):(\w+)', r"cell_range_ref('\1', '\2')", s)
    return matched

i  = 'sum(a1:b3)'
er = "sum(cell_range_ref('a1', 'b3'))"
r  = resolve_range_refs(i)

if r != er:
    print(f'{i=}, {er=}, {r=}')
    assert False

i  = 'sum(a1:a3)'
er = "sum(cell_range_ref('a1', 'a3'))"
r  = resolve_range_refs(i)

if r != er:
    print(f'{i=}, {er=}, {r=}')
    assert False

i  = 'a1:a2'
er = "cell_range_ref('a1', 'a2')"
r  = resolve_range_refs(i)

if r != er:
    print(f'{i=}, {er=}, {r=}')
    assert False

i  = 'a1:a3'
er = "cell_range_ref('a1', 'a3')"
r  = resolve_range_refs(i)

if r != er:
    print(f'{i=}, {er=}, {r=}')
    assert False

def resolve_refs(s):
    matched = re.sub(r"(?<!')([a-c]\d+)", r"cell_ref('\1')", s)
    return matched

i  = "sum(cell_range_ref('a1', 'b2'))"
er = "sum(cell_range_ref('a1', 'b2'))"
r  = resolve_refs(i)

if r != er:
    print(f'{i=}, {er=}, {r=}')
    assert False

i  = 'a1 + b1 + c1'
er = "cell_ref('a1') + cell_ref('b1') + cell_ref('c1')"
r  = resolve_refs(i)

if r != er:
    print(f'{i=}, {er=}, {r=}')
    assert False

i  = 'sum([a1, b2])'
er = "sum([cell_ref('a1'), cell_ref('b2')])"
r  = resolve_refs(i)

if r != er:
    print(f'{i=}, {er=}, {r=}')
    assert False

def cell_range_ref(lhs, rhs):
    #print(lhs, rhs)
    r1, c1 = to_rc(lhs)
    r2, c2 = to_rc(rhs)
    #print(lhs, (r1, c1), rhs, (r2, c2))

    #next_widget = rows[next_row-1][next_col-1]
    cells = []
    for c in range(c1, c2+1):
        for r in range(r1, r2+1):
            widget = rows[r-1][c-1]
            val = getattr(widget, 'value', 0)
            cells.append(val)
    #print(cells)
    return cells

def cell_ref(ref):
    r, c = to_rc(ref)
    #print(ref, (r, c))
    widget = rows[r-1][c-1]
    return getattr(widget, 'value', 0)

def resolve_expr(s):
    expr = s
    expr = resolve_range_refs(expr)
    expr = resolve_refs(expr)
    return expr

i  = 'sum(a1:b2)'
er = "sum(cell_range_ref('a1', 'b2'))"
r  = resolve_expr(i)

if r != er:
    print(f' {i=}\n{er=}\n {r=}')
    assert False

def on_leave(event):
    widget = event.widget
    widget.configure(background='white')

    raw_expr = widget.get().lstrip('=')
    #print(f'{expr=}')
    widget.formula = raw_expr

    if raw_expr == '':
        widget.value = 0
        return

    if raw_expr == 'sum above':
        r, c = get_rc(widget)
        r = max(1, r - 1)
        if r == 1:
            above = cellname(r, c) + ':' + cellname(r, c)
        else:
            above = cellname(1, c) + ':' + cellname(r, c)
        raw_expr = f'sum({above})'

    failed = True
    expr = resolve_expr(raw_expr)

    #print(expr)
    new_value = eval(expr)
    widget.value = new_value

    if is_number(new_value):
        widget.configure(justify='right')
    else:
        widget.configure(justify='left')

    widget.delete(0, tk.END)
    widget.insert(0, repr(new_value))

# add headers

headers = []
columns = []

for i in range(1, number_of_columns + 1):
    col_letter = chr(ord('a') + i - 1)
    window.grid_columnconfigure(i, minsize=80, weight=2)
    col_header = tk.Label(worksheet, text=col_letter)
    col_header.grid(row=0, column=i)
    headers.append(col_header)
    columns.append([])

def add_row(n):
    r1 = tk.Label(worksheet, text=str(n))
    r1.grid(row=n, column=0, padx=10, pady=5)

    row = []
    for i in range(1, number_of_columns + 1):
        e = tk.Entry(worksheet)
        e.grid(row=n, column=i, padx=0, sticky="nsew")
        #e.bind('<Enter>', on_enter)
        #e.bind('<Leave>', on_leave)
        e.bind('<FocusIn>', on_enter)
        e.bind('<FocusOut>', on_leave)
        row.append(e)
        columns[i-1].append(e)

    rows.append(row)

for i in range(1, number_of_rows + 1):
    add_row(i)


for i in range(1, number_of_rows + 1):
    worksheet.grid_rowconfigure(i, minsize=40, weight=2)

rows[0][1].focus_set()

window.mainloop()

