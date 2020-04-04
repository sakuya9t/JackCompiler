import unittest

from CompilationEngine import CompilationEngine
from FileHandler import FileHandler
from VMGenerator import VMGenerator
from constant import HOME_PATH, ROOT_DIR

FILE_SEVEN = HOME_PATH + '/Nand2Tetris/nand2tetris/projects/11/Seven/Main.jack'
CONVERT_TO_BIN = HOME_PATH + '/Nand2Tetris/nand2tetris/projects/11/ConvertToBin/Main.jack'


class IntegrationTest(unittest.TestCase):
    def test_seven(self):
        compiler = CompilationEngine(FILE_SEVEN)
        root_node = compiler.compile()
        generator = VMGenerator()
        code = generator.process(root_node)
        correct_code = FileHandler(ROOT_DIR + '/output/Seven/Main.vm').fileContent
        self.assertEqual(correct_code, code)

    def test_convert_to_bin(self):
        compiler = CompilationEngine(CONVERT_TO_BIN)
        root_node = compiler.compile()
        generator = VMGenerator()
        code = generator.process(root_node)
        correct_code = FileHandler(ROOT_DIR + '/output/ConvertToBin/Main.vm').fileContent
        self.assertEqual(correct_code, code)


if __name__ == '__main__':
    unittest.main()
