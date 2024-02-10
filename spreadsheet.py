class Worksheet():
    def __init__(self, min_rows=5, min_cols=20):
        self.name = "Sheet1"
        self.cell_values   = {}
        self.cell_formulas = {}
        self.cell_dependents = set()
        self.cell_precedents = set()


    def render_cells(self, x_offset, y_offset, w, h):
        cells = []
        y = y_offset
        for i in range(h):
            row_cells = []
            x = x_offset
            for j in range(w):
                c = chr(97 + x)
                row_cells.append(f'{c}{y+1}')
                x += 1
            cells.append(row_cells)
            y += 1
        return cells


    def set_formula(self, x, y):
        pass


    def get_formula(self, x, y):
        pass


