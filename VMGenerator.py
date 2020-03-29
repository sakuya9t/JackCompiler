from CompilationEngine import Node
import VMWriter
import SymbolTable
from constant import *


class VMGenerator:
    root = None
    file_name = None
    symbol_table = SymbolTable.SymbolTable()

    def generate(self, node):
        if node.type == 'classVarDec':
            return self.process_class_var_dec(node)
        return None

    def process_class_var_dec(self, node):
        # [kind, type, var name, var name]
        var_kind = node.children[0].value
        var_type = node.children[1].value
        var_names = [n.value for n in node.children[2:] if n.type == TOKEN_IDENTIFIER]
        for var_name in var_names:
            self.symbol_table.define(var_name, var_type, var_kind)
        return []
