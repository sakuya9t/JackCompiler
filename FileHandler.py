class FileHandler:
    fileContent = []

    def __init__(self, filename):
        if not filename:
            return
        self.filename = filename
        file_object = open(filename)
        try:
            self.fileContent = file_object.readlines()
            self.fileContent = [s.replace("\n", "") for s in self.fileContent]
        finally:
            file_object.close()

    def write(self, filename):
        file_object = open(filename, 'w')
        file_object.writelines([x+'\n' for x in self.fileContent])
        file_object.close()

    def refresh_content(self, content):
        self.fileContent = content

    def append_enter(self):
        length = len(self.fileContent)
        for i in range(0, length - 1):
            self.fileContent[i] += "\n"
