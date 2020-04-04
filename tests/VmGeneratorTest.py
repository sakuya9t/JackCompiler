import unittest
from unittest.mock import patch

from CompilationEngine import Node
from VMGenerator import VMGenerator
from constant import KIND_STATIC, KIND_ARGUMENT, KIND_FIELD, KIND_VAR


class VMGeneratorTest(unittest.TestCase):

    @patch('VMGenerator.VMGenerator.process_class_var_dec')
    @patch('VMGenerator.VMGenerator.process_expression_list')
    def test_process(self, process_class_var_dec, process_expression_list):
        generator = VMGenerator()
        generator.process(Node('classVarDec', None))
        generator.process(Node('expressionList', None))
        with self.assertRaises(ValueError):
            generator.process(Node('yellow_dog', None))
        process_class_var_dec.assert_called()
        process_expression_list.assert_called()

    def test_process_class_var_dec(self):
        generator = VMGenerator()
        node = Node('classVarDec', None)
        node.children.append(Node('keyword', 'field'))
        node.children.append(Node('keyword', 'int'))
        node.children.append(Node('identifier', 'x'))
        node.children.append(Node('symbol', ','))
        node.children.append(Node('identifier', 'y'))
        node.children.append(Node('symbol', ';'))
        generator.process_class_var_dec(node)
        self.assertEqual(len(generator.symbol_table.class_table), 2)
        self.assertEqual(len(generator.symbol_table.subroutine_table), 0)

    def test_process_var_dec(self):
        generator = VMGenerator()
        node = Node('varDec', None)
        node.children.append(Node('keyword', 'var'))
        node.children.append(Node('keyword', 'int'))
        node.children.append(Node('identifier', 'x'))
        node.children.append(Node('symbol', ','))
        node.children.append(Node('identifier', 'y'))
        node.children.append(Node('symbol', ';'))
        generator.process_var_dec(node)
        self.assertEqual(len(generator.symbol_table.class_table), 0)
        self.assertEqual(len(generator.symbol_table.subroutine_table), 2)

    def test_process_parameter_list(self):
        generator = VMGenerator()
        node = Node('parameterList', None, [])
        arg_cnt = generator.process_parameter_list(node)
        self.assertEqual(arg_cnt, 0)
        self.assertEqual(len(generator.symbol_table.subroutine_table), 0)
        node = Node('parameterList', None, [Node('keyword', 'int'), Node('identifier', 'Ax'), Node('symbol', ','),
                                            Node('keyword', 'Object'), Node('identifier', 'Ay')])
        arg_cnt = generator.process_parameter_list(node)
        self.assertEqual(arg_cnt, 2)
        self.assertEqual(len(generator.symbol_table.subroutine_table), 2)
        self.assertTrue('Ax' in generator.symbol_table.subroutine_table.keys())
        self.assertTrue('Ay' in generator.symbol_table.subroutine_table.keys())

    def test_process_if(self):
        generator = VMGenerator()
        generator.current_class = 'Test'
        generator.symbol_table.define('x', 'int', KIND_VAR)
        condition = Node('expression', None, [Node('term', None, [Node('identifier', 'x')], 'single'),
                                              Node('symbol', '='),
                                              Node('term', None, [Node('integerConstant', '1')], 'single')])
        statements_1 = Node('statements', None,
                            [Node('doStatement', None,
                                  [Node('keyword', 'do'), Node('identifier', 'Memory'), Node('symbol', '.'),
                                   Node('identifier', 'test'), Node('symbol', '('),
                                   Node('expressionList', None, [], {'cnt': 0}),
                                   Node('symbol', ')'), Node('symbol', ';')])
                             ])
        statements_2 = Node('statements', None,
                            [Node('letStatement', None,
                                  [Node('keyword', 'let'), Node('identifier', 'x'), Node('symbol', '='),
                                   Node('expression', None,
                                        [Node('term', None, [Node('integerConstant', '1')], 'single'),
                                         Node('symbol', '+'),
                                         Node('term', None, [Node('integerConstant', '2')], 'single'),
                                         Node('symbol', '*'),
                                         Node('term', None, [Node('identifier', 'x')], 'single')
                                         ]),
                                   Node('symbol', ';')
                                   ])
                             ])
        node = Node('ifStatement', None, [Node('keyword', 'if'), Node('symbol', '('), condition, Node('symbol', ')'),
                                          Node('symbol', '{'), statements_1, Node('symbol', '}'),
                                          Node('keyword', 'else'), Node('symbol', '{'), statements_2,
                                          Node('symbol', '}')],
                    desc='if-else')
        code = generator.process_if(node)
        self.assertEqual(code, ['push local 0', 'push constant 1', 'eq', 'not', 'if-goto Test1',
                                'call Memory.test 0', 'pop temp 0', 'goto Test2', 'label Test1', 'push constant 1',
                                'push constant 2', 'add', 'push local 0', 'call Math.multiply 2', 'pop local 0',
                                'label Test2'])
        generator.reset_seq()
        node = Node('ifStatement', None, [Node('keyword', 'if'), Node('symbol', '('), condition, Node('symbol', ')'),
                                          Node('symbol', '{'), statements_1, Node('symbol', '}')],
                    desc='if')
        code = generator.process_if(node)
        self.assertEqual(code, ['push local 0', 'push constant 1', 'eq', 'not', 'if-goto Test1',
                                'call Memory.test 0', 'pop temp 0', 'label Test1'])

    def test_process_while(self):
        generator = VMGenerator()
        generator.current_class = 'Test'
        generator.symbol_table.define('x', 'int', KIND_FIELD)
        condition = Node('expression', None, [Node('term', None, [Node('identifier', 'x')], 'single'),
                                              Node('symbol', '='),
                                              Node('term', None, [Node('integerConstant', '1')], 'single')])
        loop_body = Node('statements', None,
                         [Node('doStatement', None,
                               [Node('keyword', 'do'), Node('identifier', 'Memory'), Node('symbol', '.'),
                                Node('identifier', 'test'), Node('symbol', '('),
                                Node('expressionList', None,
                                     [Node('expression', None,
                                           [Node('term', None, [Node('integerConstant', '2')], 'single')])],
                                     {'cnt': 1}),
                                Node('symbol', ')'), Node('symbol', ';')])
                          ])
        node = Node('ifStatement', None, [Node('keyword', 'while'), Node('symbol', '('), condition, Node('symbol', ')'),
                                          Node('symbol', '{'), loop_body, Node('symbol', '}')])
        code = generator.process_while(node)
        self.assertEqual(code, ['label Test1', 'push this 0', 'push constant 1', 'eq', 'not', 'if-goto Test2',
                                'push constant 2', 'call Memory.test 1', 'pop temp 0', 'goto Test1', 'label Test2'])

    def test_process_let(self):
        generator = VMGenerator()
        generator.symbol_table.define('x', 'int', KIND_VAR)
        node = Node('letStatement', None,
                    [Node('keyword', 'let'), Node('identifier', 'x'), Node('symbol', '='),
                     Node('expression', None, [Node('term', None, [Node('integerConstant', '1')], 'single'),
                                               Node('symbol', '+'),
                                               Node('term', None, [Node('integerConstant', '2')], 'single'),
                                               Node('symbol', '*'),
                                               Node('term', None, [Node('identifier', 'x')], 'single')
                                               ]),
                     Node('symbol', ';')])
        code = generator.process_let(node)
        self.assertEqual(code, ['push constant 1', 'push constant 2', 'add', 'push local 0', 'call Math.multiply 2',
                                'pop local 0'])

    def test_process_do(self):
        generator = VMGenerator()
        node = Node('doStatement', None,
                    [Node('keyword', 'do'), Node('identifier', 'Memory'), Node('symbol', '.'),
                     Node('identifier', 'test'), Node('symbol', '('),
                     Node('expressionList',
                          None,
                          [Node('expression', None, [Node('term', None, [Node('integerConstant', '2')], 'single')]),
                           Node('symbol', ','),
                           Node('expression', None, [Node('term', None, [Node('integerConstant', '3')], 'single')])],
                          {'cnt': 2}),
                     Node('symbol', ')'), Node('symbol', ';')])
        self.assertEqual(generator.process_do(node), ['push constant 2', 'push constant 3', 'call Memory.test 2',
                                                      'pop temp 0'])
        generator.symbol_table.define('a', 'Object', KIND_VAR)
        node = Node('doStatement', None,
                    [Node('keyword', 'do'), Node('identifier', 'a'), Node('symbol', '.'),
                     Node('identifier', 'test'), Node('symbol', '('),
                     Node('expressionList',
                          None,
                          [Node('expression', None, [Node('term', None, [Node('integerConstant', '2')], 'single')]),
                           Node('symbol', ','),
                           Node('expression', None, [Node('term', None, [Node('integerConstant', '3')], 'single')])],
                          {'cnt': 2}),
                     Node('symbol', ')'), Node('symbol', ';')])
        self.assertEqual(generator.process_do(node),
                         ['push local 0', 'push constant 2', 'push constant 3',
                          'call Object.test 3', 'pop temp 0'])

    def test_process_return(self):
        generator = VMGenerator()
        generator.symbol_table.define('x', 'int', KIND_VAR)
        node = Node('returnStatement', None, [Node('keyword', 'return'), Node('symbol', ';')])
        self.assertEqual(generator.process_return(node), ['push constant 0', 'return'])
        node = Node('returnStatement', None,
                    [Node('keyword', 'return'),
                     Node('expression', None, [Node('term', None, [Node('identifier', 'x')], 'single')]),
                     Node('symbol', ';')])
        self.assertEqual(generator.process_return(node), ['push local 0', 'return'])

    def test_process_expression(self):
        generator = VMGenerator()
        generator.symbol_table.define('x', 'int', KIND_FIELD)
        node = Node('expression', None)
        node.children = [Node('term', None, [Node('integerConstant', '1')], 'single'),
                         Node('symbol', '+'),
                         Node('term', None, [Node('integerConstant', '2')], 'single'),
                         Node('symbol', '*'),
                         Node('term', None, [Node('identifier', 'x')], 'single')
                         ]
        code = generator.process_expression(node)
        self.assertEqual(code, ['push constant 1', 'push constant 2', 'add', 'push this 0', 'call Math.multiply 2'])

    def test_process_array(self):
        generator = VMGenerator()
        generator.symbol_table.define('a', 'Array', KIND_FIELD)
        generator.symbol_table.define('b', 'Array', KIND_FIELD)
        generator.symbol_table.define('i', 'int', KIND_VAR)
        generator.symbol_table.define('j', 'int', KIND_VAR)
        # let a[i] = b[j];
        node = Node('letStatement', None,
                    [Node('keyword', 'let'), Node('identifier', 'a'), Node('symbol', '['),
                     Node('expression', None, [Node('term', None, [Node('identifier', 'i')], 'single')]),
                     Node('symbol', ']'),
                     Node('symbol', '='),
                     Node('expression', None,
                          [Node('term', None,
                                [Node('identifier', 'b'), Node('symbol', '['),
                                 Node('expression', None, [Node('term', None, [Node('identifier', 'j')], 'single')]),
                                 Node('symbol', ']')], 'var[exp]')]),
                     Node('symbol', ';')
                     ])
        code = generator.process_let(node)
        self.assertEqual(code, ['push this 0', 'push local 0', 'add',
                                'push this 1', 'push local 1', 'add',
                                'pop pointer 1', 'push that 0', 'pop temp 0',
                                'pop pointer 1', 'push temp 0', 'pop that 0'])

    def test_process_term(self):
        generator = VMGenerator()
        exp1 = Node('expression', None)
        exp1.children = [Node('term', None, [Node('integerConstant', '1')], desc='single'),
                         Node('symbol', '+'),
                         Node('term', None, [Node('integerConstant', '2')], desc='single')]

        exp2 = Node('expression', None)
        exp2.children = [Node('term', None, [Node('integerConstant', '1')], desc='single'),
                         Node('symbol', '*'),
                         Node('term', None, [Node('integerConstant', '2')], desc='single')]

        # (exp)
        node = Node('term', None, desc='(exp)')
        node.children = [Node('symbol', '('), exp1, Node('symbol', ')')]
        self.assertEqual(generator.process_term(node), ['push constant 1', 'push constant 2', 'add'])

        # unop(exp)
        node = Node('term', None, desc='unop(exp)')
        node.children = [Node('symbol', '-'),
                         Node('term', None, [Node('symbol', '('), exp1, Node('symbol', ')')], '(exp)')]
        self.assertEqual(generator.process_term(node), ['push constant 1', 'push constant 2', 'add', 'neg'])

        # a.b(exps)
        node = Node('term', None, desc='a.b(exps)')
        node.children = [Node('identifier', 'SquareGame'), Node('symbol', '.'), Node('identifier', 'new'),
                         Node('symbol', '('),
                         Node('expressionList', None, [exp1, Node('symbol', ','), exp2], {'cnt': 2}),
                         Node('symbol', ')')]
        self.assertEqual(generator.process_term(node),
                         ['push constant 1', 'push constant 2', 'add', 'push constant 1', 'push constant 2',
                          'call Math.multiply 2', 'call SquareGame.new 2'])
        generator.symbol_table.define('a', 'Object', KIND_VAR)
        node = Node('term', None, desc='a.b(exps)')
        node.children = [Node('identifier', 'a'), Node('symbol', '.'), Node('identifier', 'test'),
                         Node('symbol', '('),
                         Node('expressionList', None, [exp1, Node('symbol', ','), exp2], {'cnt': 2}),
                         Node('symbol', ')')]
        self.assertEqual(generator.process_term(node),
                         ['push local 0', 'push constant 1', 'push constant 2', 'add', 'push constant 1',
                          'push constant 2', 'call Math.multiply 2', 'call Object.test 3'])

    def test_process_string(self):
        generator = VMGenerator()
        node = Node('stringConstant', 'apple')
        code = generator.process_string(node)
        expected = ['push constant 5', 'call String.new 1',
                    'push constant 97', 'call String.appendChar 2',
                    'push constant 112', 'call String.appendChar 2',
                    'push constant 112', 'call String.appendChar 2',
                    'push constant 108', 'call String.appendChar 2',
                    'push constant 101', 'call String.appendChar 2']
        self.assertEqual(code, expected)
        node = Node('term', None, [Node('stringConstant', 'apple')], 'single')
        code = generator.process_term(node)
        self.assertEqual(code, expected)

    def test_make_variable(self):
        generator = VMGenerator()
        generator.symbol_table.define("a", "int", KIND_STATIC)
        generator.symbol_table.define("b", "Object", KIND_FIELD)
        generator.symbol_table.define("c", "string", KIND_ARGUMENT)
        generator.symbol_table.define("d", "int", KIND_VAR)
        self.assertEqual(generator.make_variable(Node('identifier', 'a')), 'static 0')
        self.assertEqual(generator.make_variable(Node('identifier', 'b')), 'this 0')
        self.assertEqual(generator.make_variable(Node('identifier', 'c')), 'argument 0')
        self.assertEqual(generator.make_variable(Node('identifier', 'd')), 'local 0')
        self.assertEqual(generator.make_variable(Node('integerConstant', 7)), 'constant 7')

    def test_make_function(self):
        generator = VMGenerator()
        generator.current_class = 'MyObject'
        generator.symbol_table.define('this', 'MyObject', KIND_ARGUMENT)
        generator.symbol_table.define("a", "Object1", KIND_FIELD)
        generator.symbol_table.define("b", "Object2", KIND_STATIC)
        self.assertEqual(generator.make_function('this', 'foo', 0), ['call MyObject.foo 1'])
        self.assertEqual(generator.make_function('a', 'foo', 1), ['call Object1.foo 2'])
        self.assertEqual(generator.make_function('b', 'foo', 2), ['call Object2.foo 3'])
        self.assertEqual(generator.make_function('Object3', 'foo', 3), ['call Object3.foo 3'])

    def test_constructor(self):
        generator = VMGenerator()
        generator.current_class = 'Point'
        generator.symbol_table.define('x', 'int', KIND_FIELD)
        generator.symbol_table.define('y', 'int', KIND_FIELD)
        generator.symbol_table.define('pointCount', 'int', KIND_STATIC)
        statements = Node('statements', None, [
            Node('letStatement', None,
                 [Node('keyword', 'let'), Node('identifier', 'x'), Node('symbol', '='),
                  Node('expression', None, [Node('term', None, [Node('identifier', 'ax')], 'single')]),
                  Node('symbol', ';')
                  ]),

            Node('letStatement', None,
                 [Node('keyword', 'let'), Node('identifier', 'y'), Node('symbol', '='),
                  Node('expression', None, [Node('term', None, [Node('identifier', 'ay')], 'single')]),
                  Node('symbol', ';')
                  ]),

            Node('letStatement', None,
                 [Node('keyword', 'let'), Node('identifier', 'pointCount'), Node('symbol', '='),
                  Node('expression', None, [Node('term', None, [Node('identifier', 'pointCount')], 'single'),
                                            Node('symbol', '+'),
                                            Node('term', None, [Node('integerConstant', '1')], 'single')
                                            ]),
                  Node('symbol', ';')
                  ]),
            Node('returnStatement', None,
                 [Node('keyword', 'return'),
                  Node('expression', None, [Node('term', None, [Node('identifier', 'this')], 'single')]),
                  Node('symbol', ';')])
        ])
        param_list = Node('parameterList', None, [Node('keyword', 'int'), Node('identifier', 'ax'), Node('symbol', ','),
                                                  Node('keyword', 'int'), Node('identifier', 'ay')])
        node = Node('subroutineDec', None,
                    [Node('keyword', 'constructor'), Node('identifier', 'Point'), Node('identifier', 'new'),
                     Node('symbol', '('), param_list, Node('symbol', ')'),
                     Node('subroutineBody', None,
                          [Node('symbol', '{'), statements, Node('symbol', '}')])])
        code = generator.process_subroutine(node)
        self.assertEqual(code, ['function Point.new 0', 'push constant 2', 'call Memory.alloc 1', 'pop pointer 0',
                                'push argument 0', 'pop this 0', 'push argument 1', 'pop this 1',
                                'push static 0', 'push constant 1', 'add', 'pop static 0', 'push pointer 0',
                                'return'])

    def test_method_definition(self):
        generator = VMGenerator()
        generator.current_class = 'Point'
        generator.symbol_table.define('x', 'int', KIND_FIELD)
        generator.symbol_table.define('y', 'int', KIND_FIELD)
        param_list = Node('parameterList', None, [Node('identifier', 'Point'), Node('identifier', 'other')])
        var_declare = Node('varDec', None, [
            Node('keyword', 'var'), Node('keyword', 'int'), Node('identifier', 'dx'), Node('symbol', ','),
            Node('identifier', 'dy'), Node('symbol', ';')
        ])
        statements = Node('statements', None, [
            # let dx = x - other.getx();
            Node('letStatement', None,
                 [Node('keyword', 'let'), Node('identifier', 'dx'),
                  Node('symbol', '='),
                  Node('expression', None,
                       [Node('term', None, [Node('identifier', 'x')], 'single'),
                        Node('symbol', '-'),
                        Node('term', None,
                             [Node('identifier', 'other'), Node('symbol', '.'), Node('identifier', 'getx'),
                              Node('symbol', '('), Node('expressionList', None, [], {'cnt': 0}), Node('symbol', ')')],
                             'a.b(exps)'),
                        ]),
                  Node('symbol', ';')
                  ]),
            # let dy = y - other.gety();
            Node('letStatement', None,
                 [Node('keyword', 'let'), Node('identifier', 'dy'),
                  Node('symbol', '='),
                  Node('expression', None,
                       [Node('term', None, [Node('identifier', 'y')], 'single'),
                        Node('symbol', '-'),
                        Node('term', None,
                             [Node('identifier', 'other'), Node('symbol', '.'), Node('identifier', 'gety'),
                              Node('symbol', '('), Node('expressionList', None, [], {'cnt': 0}), Node('symbol', ')')],
                             'a.b(exps)'),
                        ]),
                  Node('symbol', ';')
                  ]),
            # return Math.sqrt((dx * dx) + (dy * dy));
            Node('returnStatement', None,
                 [Node('keyword', 'return'),
                  Node('expression', None,
                       [
                           Node('term', None,
                                [Node('identifier', 'Math'), Node('symbol', '.'), Node('identifier', 'sqrt'),
                                 Node('symbol', '('),
                                 Node('expressionList', None,
                                      [
                                          Node('expression', None,
                                               [Node('term', None, [
                                                   Node('symbol', '('),
                                                   Node('expression', None, [
                                                       Node('term', None, [Node('identifier', 'dx')],
                                                            'single'),
                                                       Node('symbol', '*'),
                                                       Node('term', None, [Node('identifier', 'dx')],
                                                            'single')
                                                   ]),
                                                   Node('symbol', ')')
                                               ], '(exp)'),
                                                Node('symbol', '+'),
                                                Node('term', None, [
                                                    Node('symbol', '('),
                                                    Node('expression', None, [
                                                        Node('term', None, [Node('identifier', 'dy')],
                                                             'single'),
                                                        Node('symbol', '*'),
                                                        Node('term', None, [Node('identifier', 'dy')],
                                                             'single')
                                                    ]),
                                                    Node('symbol', ')')
                                                ], '(exp)')]),
                                      ], {'cnt': 1}),
                                 Node('symbol', ')')], 'a.b(exps)'),
                       ]),
                  Node('symbol', ';')])
        ])
        node = Node('subroutineDec', None,
                    [Node('keyword', 'method'), Node('keyword', 'int'), Node('identifier', 'distance'),
                     Node('symbol', '('), param_list, Node('symbol', ')'),
                     Node('subroutineBody', None,
                          [Node('symbol', '{'), var_declare, statements, Node('symbol', '}')])])
        code = generator.process_subroutine(node)
        print(code)
        self.assertEqual(code, ['function Point.distance 2', 'push argument 0', 'pop pointer 0',
                                'push this 0', 'push argument 1', 'call Point.getx 1', 'sub', 'pop local 0',
                                'push this 1', 'push argument 1', 'call Point.gety 1', 'sub', 'pop local 1',
                                'push local 0', 'push local 0', 'call Math.multiply 2',
                                'push local 1', 'push local 1', 'call Math.multiply 2',
                                'add', 'call Math.sqrt 1', 'return'])


if __name__ == '__main__':
    unittest.main()
