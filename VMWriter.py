from FileHandler import FileHandler


class VMWriter:
    def __init__(self):
        self.file = FileHandler(None)

    def write_push(self, segment, index):
        self.file.fileContent.append('push {} {}'.format(segment, index))

    def write_pop(self, segment, index):
        self.file.fileContent.append('pop {} {}'.format(segment, index))

    def write_arithmetic(self, command):
        self.file.fileContent.append(command)

    def write_label(self, label):
        self.file.fileContent.append('label {}'.format(label))

    def write_goto(self, label):
        self.file.fileContent.append('goto {}'.format(label))

    def write_if(self, label):
        self.file.fileContent.append('if-goto {}'.format(label))

    def write_call(self, name, nargs):
        self.file.fileContent.append('call {} {}'.format(name, nargs))

    def write_function(self, name, nargs):
        self.file.fileContent.append('function {} {}'.format(name, nargs))

    def write_return(self):
        self.file.fileContent.append('return')

    def output_file(self, filename):
        self.file.write(filename)
