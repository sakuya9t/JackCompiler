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
        self.assertEqual(code, ['1', '2', 'add', 'x', 'call multiply'])


if __name__ == '__main__':
    unittest.main()
