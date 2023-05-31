import re

import tkinter as tk
from tkinter import font

window = tk.Tk()
window.title('Grid Test')

default_font = font.nametofont('TkDefaultFont')
default_font.configure(family='Consolas', size=24)

window.option_add("*Font", default_font)
window.configure(padx=5, pady=5)


def on_enter(event):
    current_widget = event.widget
    current_row = int(current_widget.grid_info()['row'])
    current_col = int(current_widget.grid_info()['column'])

    #print(current_row, current_col)

    next_row = current_row + 1

    if next_row <= len(rows):
        next_widget = rows[next_row-1][current_col-1]
        next_widget.focus_set()

window.bind('<Return>', on_enter)
#window.bind('<Escape>', lambda e: window.focus())
window.bind('<Escape>', lambda e: exit(0))


def on_enter(event):
    widget = event.widget
    widget.configure(background='lightblue')
    formula = getattr(widget, 'formula', None)
    if formula is None:
        return
    #print(f'{formula=}')

    widget.delete(0, tk.END)
    widget.insert(0, formula)


def is_number(s):
    try:
        f = float(s)
        return True
    except ValueError:
        pass

    try:
        i = int(s)
        return True
    except ValueError:
        pass

    return False

#print(is_number('3.14'))
#print(is_number('10'))

def on_leave(event):
    widget = event.widget
    widget.configure(background='white')

    expr = widget.get()
    #print(f'{expr=}')
    widget.formula = expr

    failed = True
    orig_expr = expr

    for i in range(10):
        try:
            new_value = eval(expr)
            failed = False
        except SyntaxError:
            return
        except NameError as ne:
            name = ne.name
            col_name, row = name
            col = "_abc".find(col_name)

            ref_widget = window.grid_slaves(row=int(row), column=int(col))[0]
            ref_value  = ref_widget.get()
            expr = re.sub(f'\\b{name}\\b', ref_value, expr, re.IGNORECASE)
            continue

    if failed:
        return

    if is_number(new_value):
        widget.configure(justify='right')
    else:
        widget.configure(justify='left')

    widget.delete(0, tk.END)
    widget.insert(0, new_value)

# add headers

h1 = tk.Label(window, text="a")
h1.grid(row=0, column=1)

h2 = tk.Label(window, text="b")
h2.grid(row=0, column=2)

h3 = tk.Label(window, text="c")
h3.grid(row=0, column=3)

rows = []
def add_row(n):
    r1 = tk.Label(window, text=str(n))
    r1.grid(row=n, column=0, padx=10, pady=5)

    row = []
    for i in range(1, 4):
        e = tk.Entry(window)
        e.grid(row=n, column=i, padx=5)
        e.bind('<Enter>', on_enter)
        e.bind('<Leave>', on_leave)
        e.bind('<FocusIn>', on_enter)
        e.bind('<FocusOut>', on_leave)
        row.append(e)

    rows.append(row)

for i in range(1, 10):
    add_row(i)

for i in range(3):
    window.grid_columnconfigure(i, weight=1)

for i in range(len(rows)):
    window.grid_rowconfigure(i+1, weight=1)

rows[0][1].focus_set()

window.mainloop()

