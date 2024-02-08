class Worksheet():
    def __init__(self, min_rows=5, min_cols=20):
        self.name = "Sheet1"
        self.cell_values   = {}
        self.cell_formulas = {}
        self.cell_dependents = set()
        self.cell_precedents = set()

    def render_cells(self, x, y, w, h):
        pass

    def set_formula(self, x, y):
        pass

    def get_formula(self, x, y):
        pass
