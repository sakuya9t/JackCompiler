from CompilationEngine import Node
from SymbolTable import SymbolTable
from VMWriter import write_call, write_push
from constant import *

op = {'+': 'add', '-': 'sub', '*': write_call('multiply'), '/': write_call('divide')}
unop = {'-': 'neg', '~': 'not'}


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

    def process_expression_list(self, node: Node):
        code = []
        for child in node.children:
            if child.type != 'symbol':
                code.extend(self.process_expression(child))
        return code

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
        if node.desc == 'single':  # constant / variable
            # todo: change variable to 'local x'
            return [write_push(node.children[0].value)]
        if node.desc == '(exp)':
            return self.process_expression(node.children[1])
        if node.desc == 'unop(exp)':
            code = self.process_expression(node.children[2])
            code.append(unop[node.children[0].value])
            return code
        if node.desc == 'var[exp]':  # todo
            return None
        if node.desc == 'f(exps)':
            code = self.process_expression_list(node.children[2])
            # todo: attach current class name, transfer f to someclass.f
            code.append(write_call(node.children[0].value))
            return code
        if node.desc == 'a.b(exps)':  # todo: convert object variable to class name
            code = self.process_expression_list(node.children[4])
            obj_name = node.children[0].value
            func_name = node.children[2].value
            code.append(write_call(obj_name + '.' + func_name))
            return code
        raise Exception('Cannot compile node {node}'.format(node=str(node)))
