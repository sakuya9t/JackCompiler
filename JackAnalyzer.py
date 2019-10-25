from CompilationEngine import CompilationEngine
import sys


class JackAnalyzer:
    def __init__(self, filename):
        ext = filename[-5:]
        if ext != '.jack':
            raise TypeError('Should input a .jack file')
        compiler = CompilationEngine(filename)
        output_name = filename[:-5] + '.xml'
        compiler.compile().to_file(output_name)


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: python filename")
        exit(1)
    JackAnalyzer(sys.argv[1])
