import unittest

from SymbolTable import SymbolTable
from constant import KIND_STATIC, KIND_ARGUMENT, KIND_VAR


class SymbolTableTests(unittest.TestCase):
    def test_symbol_table(self):
        table = SymbolTable()
        table.define("x", "int", KIND_STATIC)
        table.define("x", "int", KIND_ARGUMENT)
        self.assertEqual(table.var_count(KIND_STATIC), 1)
        self.assertEqual(table.var_count(KIND_ARGUMENT), 1)
        table.define("y", "int", KIND_VAR)
        self.assertEqual(table.var_count(KIND_VAR), 1)
        table.start_subroutine()
        self.assertEqual(table.var_count(KIND_ARGUMENT), 0)
        self.assertEqual(table.var_count(KIND_VAR), 0)
        self.assertEqual(table.var_count(KIND_STATIC), 1)
        table.define("x", "int", KIND_VAR)
        with self.assertRaises(ValueError):
            table.type_of('y')
        table.define("x2", "int", KIND_VAR)
        table.define("x3", "int", KIND_VAR)
        self.assertEqual(table.index_of('x'), 0)
        self.assertEqual(table.index_of('x2'), 1)
        with self.assertRaises(ValueError):
            table.define("x", "char", KIND_ARGUMENT)


if __name__ == '__main__':
    unittest.main()
