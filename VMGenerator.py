from CompilationEngine import Node
from FileHandler import FileHandler
from SymbolTable import SymbolTable
from VMWriter import write_call, write_push, write_function, write_pop, write_if, write_label, write_goto
from constant import *

op = {'+': 'add', '-': 'sub', '*': write_call('Math.multiply 2'), '/': write_call('Math.divide 2'), '=': 'eq',
      '>': 'gt', '<': 'lt', '&': 'and', '|': 'or'}
unop = {'-': 'neg', '~': 'not'}


class VMGenerator:

    def __init__(self):
        self.vm_code = []
        self.symbol_table = SymbolTable()
        self.label_seq = 0
        self.current_class = ''
        self.process_options = {'class': self.process_class,
                                'classVarDec': self.process_class_var_dec,
                                'varDec': self.process_var_dec,
                                'subroutineDec': self.process_subroutine,
                                'parameterList': self.process_parameter_list,
                                'subroutineBody': self.process_subroutine_body,
                                'statements': self.process_statements,
                                'ifStatement': self.process_if,
                                'whileStatement': self.process_while,
                                'doStatement': self.process_do,
                                'letStatement': self.process_let,
                                'returnStatement': self.process_return,
                                'term': self.process_term,
                                'expressionList': self.process_expression_list,
                                'expression': self.process_expression}

    def generate_vm_file(self, node: Node, filename: str):
        code = self.process(node)
        file_writer = FileHandler(None)
        file_writer.refresh_content(code)
        file_writer.write(filename)

    def process(self, node: Node):
        if node.type not in self.process_options.keys():
            raise ValueError('Cannot find handler for node type {}. Node: {}'.format(node.type, node))
        handler = self.process_options.get(node.type)
        return handler(node)

    def process_class(self, node: Node):
        self.current_class = node.children[1].value
        code = []
        for sub_node in node.children[2:]:
            if sub_node.type != TOKEN_SYMBOL:
                code.extend(self.process(sub_node))
        return code

    def process_subroutine(self, node: Node):
        if len(node.children) != 7:
            raise Exception('Cannot process subroutine node: {node}'.format(node=node))
        # format: method/function return_type name ( param_list ) body
        self.symbol_table.start_subroutine()
        self.reset_seq()
        # method: this -> argument 0, function don't do this.
        subroutine_type = node.children[0].value
        if subroutine_type == 'method':
            self.symbol_table.define(name='this', type=self.current_class, kind=KIND_ARGUMENT)
        subroutine_name = node.children[2].value
        func_label = '{}.{}'.format(self.current_class, subroutine_name)
        self.process_parameter_list(node.children[4])
        body_code = self.process_subroutine_body(node.children[6])
        arg_cnt = self.symbol_table.local_cnt()
        code = [write_function(func_label, arg_cnt)] + body_code
        return code

    def process_parameter_list(self, node: Node):
        i = 0
        while i * 3 < len(node.children):
            arg_type = node.children[i*3].value
            arg_name = node.children[i*3+1].value
            self.symbol_table.define(arg_name, arg_type, KIND_ARGUMENT)
            i += 1
        return (len(node.children) + 1) // 3

    def process_subroutine_body(self, node: Node):
        code = []
        for child in node.children:
            if child.type != TOKEN_SYMBOL:
                code.extend(self.process(child))
        return code

    def process_class_var_dec(self, node: Node):
        # [kind, type, var name, var name]
        var_kind = node.children[0].value
        var_type = node.children[1].value
        var_names = [n.value for n in node.children[2:] if n.type == TOKEN_IDENTIFIER]
        for var_name in var_names:
            self.symbol_table.define(var_name, var_type, var_kind)
        return []

    def process_var_dec(self, node: Node):
        var_type = node.children[1].value
        for i in range(2, len(node.children)):
            if node.children[i].type == 'identifier':
                self.symbol_table.define(node.children[i].value, var_type, KIND_VAR)
        return []

    def process_statements(self, node: Node):
        code = []
        for sub_node in node.children:
            code.extend(self.process(sub_node))
        return code

    def process_return(self, node: Node):
        # if no expression exist, return constant 0
        code = self.process_expression(node.children[1]) if node.children[1].type == 'expression' \
            else [write_push('constant 0')]
        code.append('return')
        return code

    def process_if(self, node: Node):
        # we don't consider elif in jack language
        if node.desc not in ['if', 'if-else']:
            raise Exception('If statement is neither if or if-else structured: {node}'.format(node=node))
        expr_code = self.process_expression(node.children[2])
        block_one = self.process_statements(node.children[5])
        code = expr_code
        label_1 = self.make_label()
        code.append('not')
        code.append(write_if(label_1))
        code.extend(block_one)
        if node.desc == 'if':
            code.append(write_label(label_1))
        elif node.desc == 'if-else':
            label_2 = self.make_label()
            code.append(write_goto(label_2))
            code.append(write_label(label_1))
            block_two = self.process_statements(node.children[9])
            code.extend(block_two)
            code.append(write_label(label_2))
        return code

    def process_while(self, node: Node):
        condition_code = self.process_expression(node.children[2])
        block_code = self.process_statements(node.children[5])
        start_label = self.make_label()
        end_label = self.make_label()
        code = [write_label(start_label)] + condition_code + ['not'] + [write_if(end_label)] + block_code + \
               [write_goto(start_label)] + [write_label(end_label)]
        return code

    def process_let(self, node: Node):
        # let var_name = expr;
        # TODO: let var_name[expr] = expr;
        var_node = node.children[1]
        value_node = node.children[3]
        code = self.process_expression(value_node)
        code.append(write_pop(self.make_variable(var_node)))
        return code

    def process_do(self, node: Node):
        # there is no a.b.c(args) call, so don't consider it.
        # do f(args); -> len = 6
        # do a.b(args); -> len = 8
        if len(node.children) not in [6, 8]:
            raise Exception('Do statement is not f(args) or a.b(args) formatted. Node: {node}'.format(node=node))
        func_name = node.children[-5].value
        obj_name = node.children[-7].value if len(node.children) == 8 else 'this'
        code = self.process_expression_list(node.children[-3])
        n_args = node.children[-3].desc['cnt']
        code.extend(self.make_function(obj_name, func_name, n_args))
        code.append(write_pop('temp 0'))  # void function return
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
            sub_node = node.children[0]
            if sub_node.value == 'true':
                return [write_push('constant 0'), 'not']
            elif sub_node.value == 'false':
                return [write_push('constant 0')]
            else:
                return [write_push(self.make_variable(sub_node))]
        if node.desc == '(exp)':
            return self.process_expression(node.children[1])
        if node.desc == 'unop(exp)':
            code = self.process_term(node.children[1])
            code.append(unop[node.children[0].value])
            return code
        if node.desc == 'var[exp]':  # todo
            return None
        if node.desc == 'f(exps)':
            code = self.process_expression_list(node.children[2])
            exps_cnt = node.children[2].desc['cnt']
            code.extend(self.make_function('this', node.children[0].value, exps_cnt))
            return code
        if node.desc == 'a.b(exps)':
            exps_cnt = node.children[4].desc['cnt']
            code = self.process_expression_list(node.children[4])
            obj_name = node.children[0].value
            func_name = node.children[2].value
            code.extend(self.make_function(obj_name, func_name, exps_cnt))
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

    def make_function(self, obj_name, func_name, n_args):
        """
        Translate function name to Class.Method formation
        :param obj_name: class name or object name or 'this'
        :param func_name: function name
        :param n_args: number of arguments
        :return: Class.Method formatted function
        """
        if obj_name == 'this':
            obj_name = self.current_class
        elif self.symbol_table.is_variable(obj_name):
            # TODO: handle object and Class type differently (need to put obj into this pointer)
            obj_name = self.symbol_table.type_of(obj_name)
        return [write_call('{}.{}'.format(obj_name, func_name), n_args)]

    def make_label(self):
        """
        Generate a label using Class seq
        :return: a generated sequential label name
        """
        return '{}{}'.format(self.current_class, self.next_seq())

    def next_seq(self):
        self.label_seq += 1
        return self.label_seq

    def reset_seq(self):
        self.label_seq = 0
