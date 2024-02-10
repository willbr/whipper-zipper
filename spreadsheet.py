import ast
import re
import time
from functools import wraps

def time_function(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.perf_counter()
        result = func(*args, **kwargs)
        end_time = time.perf_counter()
        print(f"{func.__name__} took {end_time - start_time} seconds to run.")
        return result
    return wrapper


def a1_ref_to_rc(address):
    parts = re.findall(r'[A-Za-z]+|\d+', address)

    col_name, row_name = parts
    col_name = col_name.lower()

    assert len(col_name) == 1

    col = ord(col_name) - 97
    row = int(row_name) - 1

    #print(f'{address} -> {col_name},{row_name} -> {row},{col}')

    return (row, col)


class Worksheet():
    def __init__(self, min_rows=5, min_cols=20):
        self.name = "Sheet1"
        self.cell_values   = {}
        self.cell_formulas = {}
        self.cell_dependents = set()
        self.cell_precedents = set()

        self.cell_transformer = CellReferenceTransformer(self)
        self.eval_context = {
                'cell_reference': self.cell_reference,
                'range_reference': self.range_reference,
                }


    def render_cells(self, x_offset, y_offset, width, height):
        cells = []
        row = y_offset
        for i in range(height):
            row_cells = []
            col = x_offset
            for j in range(width):
                value = self.get_value(row, col)
                row_cells.append(value)
                col += 1
            cells.append(row_cells)
            row += 1
        return cells


    def set_formula(self, row, col, new_formula):
        address = (row, col)
        #print(f'{address}, {new_formula}')

        self.cell_formulas[address] = new_formula

        new_value = self.eval_formula(row, col)

        changes = []
        changes.append((address, new_value))
        return changes


    def get_formula(self, row, col):
        address = (row, col)
        return self.cell_formulas.get(address, '')


    def get_value(self, row, col):
        value = self.cell_values.get((row, col), '')
        return value


    def eval_formula(self, row, col):
        address = (row, col)
        formula = self.cell_formulas.get(address, '')

        py_formula = formula
        py_formula = re.sub(r'(\w+):(\w+)', r"range_reference('\1', '\2')", py_formula)
        py_formula = re.sub(r"(?<!')([a-z]+\d+)", r"cell_reference('\1')", py_formula)
        print(py_formula)

        raw_formula_ast = ast.parse(py_formula, mode='eval')
        #print(ast.dump(raw_formula_ast, indent=4))

        new_formula_ast = raw_formula_ast
        #new_formula_ast = self.cell_transformer.visit(raw_formula_ast)
        #print(ast.dump(new_formula_ast, indent=4))

        compiled_code = compile(new_formula_ast, filename='<ast>', mode='eval')
        #print(compiled_code)

        #expression = formula

        try:
            result = eval(compiled_code, self.eval_context, None)
            #result = eval(expression, None, None) 
        except Exception as e:
            result = f'#Error {e}'

        self.cell_values[address] = result

        return repr(result)


    def cell_reference(self, a1_address):
        rc_address = a1_ref_to_rc(a1_address)
        value = self.get_value(*rc_address)
        return value


    def range_reference(self, from_address, to_address):
        from_r, from_c = a1_ref_to_rc(from_address)
        to_r,   to_c = a1_ref_to_rc(to_address)

        if from_r > to_r:
            from_r, to_r = to_r, from_r

        if from_c > to_c:
            from_c, to_c = to_c, from_c

        for col in range(from_c, to_c + 1):
            for row in range(from_r, to_r + 1):
                value = self.get_value(row, col)
                yield value


class CellReferenceTransformer(ast.NodeTransformer):
    def __init__(self, worksheet):
        super().__init__()
        self.worksheet = worksheet


    def visit_Name(self, node):
        cellref = ast.Name(
                id='cell_reference',
                ctx=ast.Load(),
                lineno = node.lineno,
                col_offset = node.col_offset)

        address = ast.Constant(
                value=node.id,
                lineno = node.lineno,
                col_offset = node.col_offset)

        call = ast.Call(
                func=cellref,
                args=[address],
                keywords=[],
                lineno=node.lineno,
                col_offset=node.col_offset)

        return call


