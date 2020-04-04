import os
import sys

from CompilationEngine import CompilationEngine
from VMGenerator import VMGenerator


class JackCompiler:
    def __init__(self, path):
        file_names = os.listdir(path)
        for filename in file_names:
            if filename[-5:] == '.jack':
                compiler = CompilationEngine(path + '/' + filename)
                root_node = compiler.compile()
                generator = VMGenerator()
                output_path = ''.join([path, '/', filename[:-5], '.vm'])
                generator.generate_vm_file(root_node, output_path)


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: python path")
        exit(1)
    JackCompiler(sys.argv[1])
