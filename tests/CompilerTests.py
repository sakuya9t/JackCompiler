import unittest

from default.CompilationEngine import TOKEN_KEYWORD, TOKEN_IDENTIFIER, TOKEN_SYMBOL, CompilationEngine, match_bracket
from default.JackTokenizer import Token

FILE_SQUARE_MAIN = '/home/sakuya/Dev/Nand2Tetris/nand2tetris/projects/10/Square/Main.jack'
FILE_ARRAY_MAIN = '/home/sakuya/Dev/Nand2Tetris/nand2tetris/projects/10/ArrayTest/Main.jack'
FILE_SQUARE_SQUARE = '/home/sakuya/Dev/Nand2Tetris/nand2tetris/projects/10/Square/Square.jack'
FILE_SQUARE_SQUAREGAME = '/home/sakuya/Dev/Nand2Tetris/nand2tetris/projects/10/Square/SquareGame.jack'
FILE_EXPRESSIONLESS_MAIN = '/home/sakuya/Dev/Nand2Tetris/nand2tetris/projects/10/ExpressionLessSquare/Main.jack'


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

    def test_varDec(self):
        compiler = CompilationEngine(FILE_ARRAY_MAIN)
        self.assertTrue(compiler.isVarDec(9, 12))
        self.assertTrue(compiler.isVarDec(13, 16))
        self.assertFalse(compiler.isVarDec(9, 16))
        node = compiler.compileVarDec(9, 12)
        self.assertEqual(len(node.children), 4)

    def test_if(self):
        compiler = CompilationEngine(FILE_SQUARE_MAIN)
        self.assertTrue(compiler.isIf(63, 119))
        node = compiler.compileIf(63, 119)
        self.assertEqual(len(node.children), 11)
        self.assertFalse(compiler.isIf(63, 89))
        self.assertFalse(compiler.isIf(90, 119))
        compiler = CompilationEngine(FILE_SQUARE_SQUARE)
        self.assertTrue(compiler.isIf(396, 468))
        node = compiler.compileIf(396, 468)
        self.assertEqual(len(node.children), 7)

    def test_return(self):
        compiler = CompilationEngine(FILE_ARRAY_MAIN)
        self.assertTrue(compiler.isReturn(136, 137))
        node = compiler.compileReturn(136, 137)
        self.assertEqual(len(node.children), 2)
        compiler = CompilationEngine(FILE_SQUARE_SQUARE)
        self.assertTrue(compiler.isReturn(47, 49))
        node = compiler.compileReturn(47, 49)
        self.assertEqual(len(node.children), 3)

    def test_do(self):
        compiler = CompilationEngine(FILE_ARRAY_MAIN)
        self.assertTrue(compiler.isDo(111, 118))
        self.assertTrue(compiler.isDo(119, 128))
        self.assertTrue(compiler.isDo(129, 135))
        self.assertFalse(compiler.isDo(111, 135))
        node = compiler.compileDo(111, 118)
        self.assertEqual(len(node.children), 8)
        node = compiler.compileDo(119, 128)
        self.assertEqual(len(node.children), 8)
        node = compiler.compileDo(129, 135)
        self.assertEqual(len(node.children), 8)
        compiler = CompilationEngine(FILE_SQUARE_SQUAREGAME)
        self.assertTrue(compiler.isDo(182, 186))
        node = compiler.compileDo(182, 186)
        self.assertEqual(len(node.children), 6)

    def test_let(self):
        compiler = CompilationEngine(FILE_SQUARE_MAIN)
        self.assertTrue(compiler.isLet(112, 118))
        node = compiler.compileLet(112, 118)
        self.assertEqual(len(node.children), 5)
        self.assertTrue(compiler.isLet(102, 111))
        node = compiler.compileLet(102, 111)
        self.assertEqual(len(node.children), 5)
        self.assertTrue(compiler.isLet(78, 88))
        node = compiler.compileLet(78, 88)
        self.assertEqual(len(node.children), 8)

    def test_while(self):
        compiler = CompilationEngine(FILE_ARRAY_MAIN)
        self.assertTrue(compiler.isWhile(86, 110))
        node = compiler.compileWhile(86, 110)
        self.assertEqual(len(node.children), 7)
        self.assertTrue(compiler.isWhile(48, 75))
        node = compiler.compileWhile(48, 75)
        self.assertEqual(len(node.children), 7)

    def test_statements(self):
        compiler = CompilationEngine(FILE_ARRAY_MAIN)
        node = compiler.compileStatements(23, 137)
        self.assertEqual(len(node.children), 11)
        node = compiler.compileStatements(55, 74)
        self.assertEqual(len(node.children), 2)

    def test_subroutine_body(self):
        compiler = CompilationEngine(FILE_ARRAY_MAIN)
        node = compiler.compileSubroutineBody(8, 138)
        self.assertEqual(len(node.children), 6)
        compiler = CompilationEngine(FILE_SQUARE_SQUARE)
        node = compiler.compileSubroutineBody(26, 50)
        self.assertEqual(len(node.children), 3)

    def test_print_xml(self):
        compiler = CompilationEngine(FILE_EXPRESSIONLESS_MAIN)
        node = compiler.compile()
        xml = node.to_xml()
        node.to_file('noexp_main.xml')


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
