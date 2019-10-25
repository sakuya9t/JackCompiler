from CompilationEngine import CompilationEngine
import sys
import os


class JackAnalyzer:
    def __init__(self, path):
        filenames = os.listdir(path)
        for filename in filenames:
            if filename[-5:] == '.jack':
                compiler = CompilationEngine(path + '/' + filename)
                output_name = filename[:-5] + '.xml'
                compiler.compile().to_file(path + '/' + output_name)


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: python filename")
        exit(1)
    JackAnalyzer(sys.argv[1])
