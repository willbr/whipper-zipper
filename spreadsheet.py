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


def rc_to_a1_ref(row, col):
    col_name = chr(97 + col)
    row_name = row + 1
    name = f'{col_name}{row_name}'
    return name


def range_to_addresses(a1_from_address, a1_to_address):
    from_r, from_c = a1_ref_to_rc(a1_from_address)
    to_r,   to_c = a1_ref_to_rc(a1_to_address)

    if from_r > to_r:
        from_r, to_r = to_r, from_r

    if from_c > to_c:
        from_c, to_c = to_c, from_c

    for col in range(from_c, to_c + 1):
        for row in range(from_r, to_r + 1):
            yield (row, col)


class Worksheet():
    def __init__(self, min_rows=5, min_cols=20):
        self.name = "Sheet1"
        self.cell_values   = {}
        self.cell_formulas = {}
        self.cell_dependents = {}
        self.cell_precedents = {}

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


    def set_formula(self, row, col, new_formula=None):
        address = (row, col)
        #print(f'set {address=}, {new_formula=}')

        assignment = None

        if new_formula is not None:
            matched = re.match('^s*(\w+)\s*=\s*(.*)', new_formula)
            if matched:
                assignment, new_formula = matched.groups()

        old_value = self.cell_values.get(address, None)
        new_value = self.eval_formula(row, col, new_formula)

        if new_value is None:
            changes = [(address, '')]
        else:
            changes = [(address, repr(new_value))]

        if assignment and col != 0:
            lhs_address = (row, col - 1)
            lhs_formula = self.get_formula(*lhs_address)
            if lhs_formula == '':
                lhs_changes = self.set_formula(*lhs_address, f"'{assignment}'")
                changes.extend(lhs_changes)


        if new_value != old_value:
            #print(f'dirty {new_value=} != {old_value=}')
            self.cell_values[address] = new_value

            precedents = self.cell_precedents.get(address, set())
            #print(f'{precedents=}')

            for precedent in precedents:
                precedent_changes = self.set_formula(*precedent, new_formula=None)
                changes.extend(precedent_changes)

        return changes


    def get_formula(self, row, col):
        address = (row, col)
        return self.cell_formulas.get(address, '')


    def get_value(self, row, col):
        value = self.cell_values.get((row, col), None)
        return value


    def eval_formula(self, row, col, formula=None):
        address = (row, col)

        if formula is None:
            formula = self.cell_formulas.get(address, '')
        else:
            self.cell_formulas[address] = formula

        #print(f'eval {address} {formula}')

        if formula.strip() == '':
            return None

        py_formula = formula
        py_formula = re.sub(r'(\w+):(\w+)', r"range_reference('\1', '\2')", py_formula)
        py_formula = re.sub(r"(?<!')([a-z]+\d+)", r"cell_reference('\1')", py_formula)
        #print(py_formula)

        filename = rc_to_a1_ref(row, col)
        try:
            raw_formula_ast = ast.parse(py_formula, filename=filename, mode='eval')
        except Exception as e:
            result = f'#Error {e} {formula=}'
            return result

        #print(ast.dump(raw_formula_ast, indent=4))

        new_formula_ast = raw_formula_ast
        #new_formula_ast = self.cell_transformer.visit(raw_formula_ast)
        #print(ast.dump(new_formula_ast, indent=4))

        self.parse_dependents(address, new_formula_ast)

        compiled_code = compile(new_formula_ast, filename='<ast>', mode='eval')
        #print(compiled_code)

        #expression = formula

        try:
            result = eval(compiled_code, self.eval_context, None)
            #result = eval(py_formula, self.eval_context, None)
        except Exception as e:
            result = f'#Error {e}'

        return result


    def cell_reference(self, a1_address):
        rc_address = a1_ref_to_rc(a1_address)
        value = self.get_value(*rc_address)
        return value


    def range_reference(self, a1_from_address, a1_to_address):
        for address in range_to_addresses(a1_from_address, a1_to_address):
            value = self.get_value(*address)
            if value is not None:
                yield value


    def parse_dependents(self, address, formula_ast):
        #print(f'{address=}')
        #print(ast.dump(formula_ast, indent=4))

        dependents = []
        for node in ast.walk(formula_ast):
            if not isinstance(node, ast.Call):
                continue
            #print(node)
            func_name = node.func.id
            if func_name == 'cell_reference':
                cell_name = node.args[0].value
                cell_rc = a1_ref_to_rc(cell_name)
                #print(f'{cell_name}, {cell_rc}')
                dependents.append(cell_rc)
            elif func_name == 'range_reference':
                from_cell = node.args[0].value
                to_cell   = node.args[1].value
                dependents.extend(range_to_addresses(from_cell, to_cell))
            else:
                pass
        self.cell_dependents[address] = dependents

        #print(f'{dependents=}')

        for dependent in dependents:
            precedents = self.cell_precedents.get(dependent, None)
            if precedents is None:
                precedents = set()
                self.cell_precedents[dependent] = precedents
            precedents.add(address)

        #print(f'{self.cell_dependents=}')
        #print(f'{self.cell_precedents=}')


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


