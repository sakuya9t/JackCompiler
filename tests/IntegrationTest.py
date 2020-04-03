import unittest

from CompilationEngine import CompilationEngine
from VMGenerator import VMGenerator
from constant import HOME_PATH, ROOT_DIR

FILE_SEVEN = HOME_PATH + '/Nand2Tetris/nand2tetris/projects/11/Seven/Main.jack'


class IntegrationTest(unittest.TestCase):
    def test_seven(self):
        compiler = CompilationEngine(FILE_SEVEN)
        root_node = compiler.compile()
        generator = VMGenerator()
        code = generator.process(root_node)
        print(code)
        generator.generate_vm_file(root_node, ROOT_DIR + '/output/Seven/Main.vm')
        self.assertTrue(True)


if __name__ == '__main__':
    unittest.main()
