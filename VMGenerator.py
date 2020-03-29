from CompilationEngine import Node
from SymbolTable import SymbolTable
from VMWriter import write_call
from constant import *

op = {'+': 'add', '-': 'sub', '*': write_call('multiply'), '/': write_call('divide')}


class VMGenerator:
    vm_code = []
    symbol_table = SymbolTable()

    def process(self, node: Node):
        if node.type == 'classVarDec':
            return self.process_class_var_dec(node)
        return None

    def process_class_var_dec(self, node: Node):
        # [kind, type, var name, var name]
        var_kind = node.children[0].value
        var_type = node.children[1].value
        var_names = [n.value for n in node.children[2:] if n.type == TOKEN_IDENTIFIER]
        for var_name in var_names:
            self.symbol_table.define(var_name, var_type, var_kind)
        return []

    def process_expression(self, node: Node):
        # expression: term (op term)*
        code = self.process_term(node.children[0])
        i = 2
        while i < len(node.children):
            code.extend(self.process_term(node.children[i]))
            code.append(op[node.children[i-1].value])
            i += 2
        return code

    def process_term(self, node: Node):
        if len(node.children) == 1:  # constant / variable
            return [node.children[0].value]
        return []
