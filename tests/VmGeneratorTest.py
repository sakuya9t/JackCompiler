import unittest
from CompilationEngine import Node
from VMGenerator import VMGenerator


class CompilerTest(unittest.TestCase):
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
        self.assertTrue(len(generator.symbol_table.class_table) == 2)

    def test_process_expression(self):
        generator = VMGenerator()
        node = Node('expression', None)
        node.children = [Node('term', None, [Node('integerConstant', '1')]),
                         Node('symbol', '+'),
                         Node('term', None, [Node('integerConstant', '2')]),
                         Node('symbol', '*'),
                         Node('term', None, [Node('identifier', 'x')])
                         ]
        code = generator.process_expression(node)
        self.assertEqual(code, ['push 1', 'push 2', 'add', 'push x', 'call multiply'])

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
        self.assertEqual(generator.process_term(node), ['push 1', 'push 2', 'add'])

        # unop(exp)
        node = Node('term', None, desc='unop(exp)')
        node.children = [Node('symbol', '-'), Node('symbol', '('), exp1, Node('symbol', ')')]
        self.assertEqual(generator.process_term(node), ['push 1', 'push 2', 'add', 'neg'])

        # a.b(exps)
        node = Node('term', None, desc='a.b(exps)')
        node.children = [Node('identifier', 'SquareGame'), Node('symbol', '.'), Node('identifier', 'new'),
                         Node('symbol', '('), Node('expressionList', None, [exp1, Node('symbol', ','), exp2]),
                         Node('symbol', ')')]
        self.assertEqual(generator.process_term(node),
                         ['push 1', 'push 2', 'add', 'push 1', 'push 2', 'call multiply', 'call SquareGame.new'])


if __name__ == '__main__':
    unittest.main()
