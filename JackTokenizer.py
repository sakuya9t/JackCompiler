import FileHandler
import re


class Token:
    def __init__(self, type, value):
        self.type = type
        self.value = value

    def __str__(self):
        return self.to_xml()

    def to_xml(self):
        c = self.value
        if c == '<':
            c = '&lt;'
        elif c == '>':
            c = '&gt;'
        elif c == '&':
            c = '&amp;'
        return "<{}>{}</{}>".format(self.type, c, self.type)

    @staticmethod
    def load_xml(xml_string):
        type = xml_string[xml_string.index('<')+1:xml_string.index('>')]
        value = re.sub(r"<[^<>]*>", "", xml_string)
        return Token(type, value)


class JackTokenizer:
    def __init__(self, filename):
        self.fileContent = []
        self.curr = None
        self.currIndex = -1
        self.tokens = []
        if not filename:
            return
        if filename[-4:] != "jack":
            raise TypeError("Type error: Should input a .jack script file!")
        fileHandler = FileHandler.FileHandler(filename)
        in_comment = False
        for s in fileHandler.fileContent:
            s = self.removeComment(s)
            if not in_comment and '/*' in s:
                s = s[:s.index('/*')]
                in_comment = True
            elif in_comment and '*/' in s:
                s = s[s.index('*/') + 2:]
                in_comment = False
            elif in_comment:
                continue
            if len(s) > 0:
                self.fileContent.append(s)
        for content in self.fileContent:
            self.parse(content)

    def output_tokens(self, filename):
        file = FileHandler.FileHandler(None)
        file.fileContent.append('<tokens>')
        file.fileContent.extend([x.to_xml() for x in self.tokens])
        file.fileContent.append('</tokens>')
        file.write(filename)

    def tokenType(self, token):
        if token in ["class", "method", "function", "constructor", "int", "boolean", "char",
                     "void", "var", "static", "field", "let", "do", "if", "else", "while",
                     "return", "true", "false", "null", "this"]:
            return Token("keyword", token)
        if token in ["{", "}", "(", ")", "[", "]", ".", ",", ";", "+", "-", "*", "/", "&", "|",
                     "<", ">", "=", "~", "&lt;", "&gt;", "&amp;"]:
            return Token("symbol", token)
        if token[0] == '\"' and token[-1] == '\"':
            return Token("stringConstant", token.replace('\"', ''))
        if re.search(r"^[0-9]+$", token) != None:
            return Token("integerConstant", int(token))
        return Token("identifier", token)

    def parse(self, line):
        str_flag = False
        curr = ""
        for c in line:
            if c != '\"' and str_flag:
                curr += c
                continue
            if c in ['{', '}', '(', ')', '[', ']', '.', ',', ';', '+', '-', '*', '/', '&', '|',
                     '<', '>', '=', '~']:
                if len(curr) > 0:
                    self.tokens.append(self.tokenType(curr))
                    curr = ""
                self.tokens.append(self.tokenType(c))
                continue
            if c == ' ' and not str_flag:
                if len(curr) > 0:
                    self.tokens.append(self.tokenType(curr))
                curr = ""
                continue
            if c == "\"":
                curr += c
                str_flag = not str_flag
                if not str_flag:
                    self.tokens.append(self.tokenType(curr))
                    curr = ""
            else:
                curr += c
        if len(curr) > 0:
            self.tokens.append(self.tokenType(curr))

    def removeComment(self, s):
        ns = re.sub(r"//.*$", "", s)  # remove \\ comments
        ns = re.sub(r"/\*.*\*/", "", ns)  # remove /**/ comments
        ns = re.sub(r"^\s+", "", ns)  # remove spaces ahead
        ns = re.sub(r"\s+$", "", ns)  # remove spaces in the end
        ns = ns.replace('\n', '')  # remove newline
        ns = ns.replace('\t', '')  # remove tab symbol
        return ns

    def hasMoreTokens(self):
        return self.currIndex < len(self.tokens) - 1

    def advance(self):
        self.currIndex += 1
        self.curr = self.tokens[self.currIndex]

