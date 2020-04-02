from CompilationEngine import Node
from SymbolTable import SymbolTable
from VMWriter import write_call, write_push
from constant import *

op = {'+': 'add', '-': 'sub', '*': write_call('Math.multiply 2'), '/': write_call('Math.divide 2')}
unop = {'-': 'neg', '~': 'not'}


class VMGenerator:
    vm_code = []
    symbol_table = SymbolTable()
    current_class = ''

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

    def process_do(self, node: Node):
        # there is no a.b.c(args) call, so don't consider it.
        # do f(args); -> len = 6
        # do a.b(args); -> len = 8
        if len(node.children) not in [6, 8]:
            raise Exception('Do statement is not f(args) or a.b(args) formatted. Node: {node}'.format(node=node))

        func_name = node.children[-5].value
        obj_name = node.children[-7].value if len(node.children) == 8 else 'this'
        code = self.process_expression_list(node.children[-3])
        # todo: handle nArgs
        code.append(write_call(self.make_function(obj_name, func_name)))
        return code

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
            return [write_push(self.make_variable(node.children[0]))]
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
            code.append(write_call(self.make_function('this', node.children[0].value)))
            return code
        if node.desc == 'a.b(exps)':
            exps_cnt = node.children[4].desc['cnt']
            code = self.process_expression_list(node.children[4])
            obj_name = node.children[0].value
            func_name = node.children[2].value
            code.append(write_call(self.make_function(obj_name, func_name), exps_cnt))
            return code
        raise Exception('Cannot compile node {node}'.format(node=str(node)))

    def make_variable(self, variable_like_node):
        """
        Translate node contains a variable to something like 'local 4', 'var 3'.
        If not containing a variable, return itself. It can be a constant.
        TODO: Currently we are not considering string constant.
        :param variable_like_node: a name of variable
        :return: translated format generated using symbol table
        """
        if variable_like_node.type == TOKEN_STR:
            raise Exception('String constant not supported')
        if variable_like_node.type == TOKEN_INT:
            return 'constant {}'.format(variable_like_node.value)
        name = variable_like_node.value
        kind = self.symbol_table.vm_kind_of(name)
        index = self.symbol_table.index_of(name)
        return '{} {}'.format(kind, index)

    def make_function(self, obj_name, func_name):
        """
        Translate function name to Class.Method formation
        :param obj_name: class name or object name or 'this'
        :param func_name: function name
        :return: Class.Method formatted function
        """
        if obj_name == 'this':
            obj_name = self.current_class
        elif self.symbol_table.is_variable(obj_name):
            obj_name = self.symbol_table.type_of(obj_name)
        return '{}.{}'.format(obj_name, func_name)
