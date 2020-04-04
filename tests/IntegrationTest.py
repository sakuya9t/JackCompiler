import os
import unittest

from CompilationEngine import CompilationEngine
from FileHandler import FileHandler
from VMGenerator import VMGenerator
from constant import HOME_PATH, ROOT_DIR

FILE_SEVEN = HOME_PATH + '/Nand2Tetris/nand2tetris/projects/11/Seven/Main.jack'
CONVERT_TO_BIN = HOME_PATH + '/Nand2Tetris/nand2tetris/projects/11/ConvertToBin/Main.jack'
SQUARE_DIR = HOME_PATH + '/Nand2Tetris/nand2tetris/projects/11/Square'
AVERAGE = HOME_PATH + '/Nand2Tetris/nand2tetris/projects/11/Average/Main.jack'
PONG_DIR = HOME_PATH + '/Nand2Tetris/nand2tetris/projects/11/Pong'
COMPLEX_ARRAY = HOME_PATH + '/Nand2Tetris/nand2tetris/projects/11/ComplexArrays/Main.jack'


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

    def test_square(self):
        file_names = os.listdir(SQUARE_DIR)
        for filename in file_names:
            if filename[-5:] == '.jack':
                compiler = CompilationEngine(SQUARE_DIR + '/' + filename)
                root_node = compiler.compile()
                generator = VMGenerator()
                code = generator.process(root_node)
                correct_code = FileHandler(''.join([ROOT_DIR, '/output/Square/', filename[:-5], '.vm'])).fileContent
                self.assertEqual(correct_code, code)

    def test_average(self):
        compiler = CompilationEngine(AVERAGE)
        root_node = compiler.compile()
        generator = VMGenerator()
        code = generator.process(root_node)
        correct_code = FileHandler(ROOT_DIR + '/output/Average/Main.vm').fileContent
        self.assertEqual(correct_code, code)

    def test_pong(self):
        file_names = os.listdir(PONG_DIR)
        for filename in file_names:
            if filename[-5:] == '.jack':
                compiler = CompilationEngine(PONG_DIR + '/' + filename)
                root_node = compiler.compile()
                generator = VMGenerator()
                code = generator.process(root_node)
                correct_code = FileHandler(''.join([ROOT_DIR, '/output/Pong/', filename[:-5], '.vm'])).fileContent
                self.assertEqual(correct_code, code)

    def test_complex_array(self):
        compiler = CompilationEngine(COMPLEX_ARRAY)
        root_node = compiler.compile()
        generator = VMGenerator()
        code = generator.process(root_node)
        correct_code = FileHandler(ROOT_DIR + '/output/ComplexArrays/Main.vm').fileContent
        self.assertEqual(correct_code, code)


if __name__ == '__main__':
    unittest.main()
