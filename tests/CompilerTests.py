import unittest

from default.CompilationEngine import TOKEN_KEYWORD, TOKEN_IDENTIFIER, TOKEN_SYMBOL, CompilationEngine, match_bracket
from default.JackTokenizer import Token

FILE_SQUARE_MAIN = '/home/sakuya/Dev/Nand2Tetris/nand2tetris/projects/10/Square/Main.jack'
FILE_ARRAY_MAIN = '/home/sakuya/Dev/Nand2Tetris/nand2tetris/projects/10/ArrayTest/Main.jack'
FILE_SQUARE_SQUARE = '/home/sakuya/Dev/Nand2Tetris/nand2tetris/projects/10/Square/Square.jack'


class CompilerTest(unittest.TestCase):
    def test_classVarDec(self):
        tokens = [Token(TOKEN_KEYWORD, 'field'), Token(TOKEN_KEYWORD, 'int'), Token(TOKEN_IDENTIFIER, 'x'),
                  Token(TOKEN_SYMBOL, ','), Token(TOKEN_IDENTIFIER, 'y'), Token(TOKEN_SYMBOL, ';')]
        compiler = CompilationEngine(None)
        compiler.tokens = tokens
        self.assertTrue(compiler.isClassVarDec(0, len(tokens) - 1))
        node = compiler.compileClassVarDec(0, len(tokens) - 1)
        self.assertEqual(len(node.children), 6)

    def test_match_bracket(self):
        compiler = CompilationEngine(FILE_SQUARE_MAIN)
        brackets = match_bracket(compiler.tokens, opening='{', closing='}')
        self.assertEqual(brackets, {12: 42, 67: 89, 91: 119, 48: 122, 2: 123})

    def test_subroutine(self):
        compiler = CompilationEngine(FILE_ARRAY_MAIN)
        self.assertTrue(compiler.isSubroutine(3, 138))
        self.assertFalse(compiler.isSubroutine(48, 75))
        node = compiler.compileSubroutine(3, 138)
        self.assertEqual(len(node.children), 7)
        compiler = CompilationEngine(FILE_SQUARE_SQUARE)
        self.assertTrue(compiler.isSubroutine(13, 50))
        node = compiler.compileSubroutine(13, 50)
        self.assertEqual(len(node.children), 7)

    def test_compileParameterList(self):
        compiler = CompilationEngine(FILE_SQUARE_SQUARE)
        node = compiler.compileParameterList(17, 24)
        self.assertEqual(len(node.children), 8)
        compiler = CompilationEngine(FILE_SQUARE_MAIN)
        node = compiler.compileParameterList(13, 12)
        self.assertEqual(len(node.children), 0)


def _read_tokens(filename, start, end):
    with open(filename, 'r') as file:
        content = file.readlines()
    lines = content[start:end]
    tokens = []
    for line in lines:
        tokens.append(Token.load_xml(line.strip()))
    return tokens


if __name__ == '__main__':
    unittest.main()
