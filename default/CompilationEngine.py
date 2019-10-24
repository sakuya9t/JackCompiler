from default.JackTokenizer import Token, JackTokenizer

TOKEN_KEYWORD = 'keyword'
TOKEN_SYMBOL = 'symbol'
TOKEN_INT = 'integerConstant'
TOKEN_STR = 'stringConstant'
TOKEN_IDENTIFIER = 'identifier'


class Node:
    type = None
    value = None
    children = []

    def __init__(self, type, value):
        self.type = type
        self.value = value
        self.children = []

    def __str__(self):
        if not self.children or len(self.children) == 0:
            return '({}, {})'.format(self.type, self.value)
        return '({}, {}: {})'.format(self.type, self.value, [str(x) for x in self.children])


class CompilationEngine:
    result = []
    curr = 0

    def __init__(self, filename):
        self.tknzr = JackTokenizer(filename)
        self.tokens = self.tknzr.tokens
        self.bracket_map = match_bracket(self.tokens, opening='{', closing='}')
        self.square_bracket = match_bracket(self.tokens, opening='[', closing=']')
        self.parenthesis = match_bracket(self.tokens, opening='(', closing=')')

    def _token_value(self, index):
        return self.tokens[index].value

    def compile(self):
        if self.tokens[0].type == TOKEN_KEYWORD and self._token_value(0) == 'class':
            if self.tokens[-1].type == TOKEN_SYMBOL and self._token_value(-1) == '}':
                return self.compileClass(0, len(self.tokens) - 1)

    def compileClass(self, start, end):
        curr = start
        node = Node('class', None)
        #  class
        node.children.append(Node(TOKEN_KEYWORD, self._token_value(curr)))
        curr += 1  # identifier
        node.children.append(Node(TOKEN_IDENTIFIER, self._token_value(curr)))
        curr += 1  # {
        node.children.append(Node(TOKEN_SYMBOL, self._token_value(curr)))
        curr += 1
        fast = curr
        while fast < end:
            if self.isClassVarDec(curr, fast):
                node.children.append(self.compileClassVarDec(curr, fast))
                curr = fast + 1
            elif self.isSubroutine(curr, fast):
                node.children.append(self.compileSubroutine(curr, fast))
                curr = fast + 1
            else:
                fast += 1
        # }
        node.children.append(Node(self.tokens[-1].type, self._token_value(-1)))
        return node

    def isClassVarDec(self, start, end):
        return self.tokens[start].type == TOKEN_KEYWORD \
               and self._token_value(start) in ['static', 'field'] \
               and self.tokens[end].type == TOKEN_SYMBOL \
               and self._token_value(end) == ';'


    def compileClassVarDec(self, start, end):
        node = Node('classVarDec', None)
        curr = start
        while curr <= end:
            node.children.append(Node(self.tokens[curr].type, self.tokens[curr].value))
            curr += 1
        return node

    def isSubroutine(self, start, end):
        curr = start
        if self._token_value(curr) not in ['constructor', 'function', 'method']:
            return False
        while curr <= end and self._token_value(curr) != ')':
            curr += 1
        if curr >= end:
            return False
        curr += 1
        if self._token_value(curr) != '{':
            return False
        closing = self.bracket_map[curr]
        return end == closing

    def compileSubroutine(self, start, end):
        node = Node('subroutineDec', None)
        curr = start
        while self._token_value(curr) != '(':
            node.children.append(Node(self.tokens[curr].type, self.tokens[curr].value))
            curr += 1
        node.children.append(Node(self.tokens[curr].type, self.tokens[curr].value))
        left_para = curr
        right_para = self.parenthesis[curr]
        node.children.append(self.compileParameterList(left_para+1, right_para-1))
        curr = right_para
        node.children.append(Node(self.tokens[curr].type, self.tokens[curr].value))
        curr += 1
        body = self.compileSubroutineBody(curr, end)
        node.children.append(body)
        return node

    def compileParameterList(self, start, end):
        node = Node('parameterList', None)
        curr = start
        while curr <= end:
            node.children.append(Node(self.tokens[curr].type, self.tokens[curr].value))
            curr += 1
        return node

    def compileSubroutineBody(self, start, end):
        node = Node('subroutineBody', None)
        return node


    def compileVarDec(self):
        pass

    def compileStatements(self):
        pass

    def compileDo(self):
        pass

    def compileLet(self):
        pass

    def compileWhile(self):
        pass

    def compileReturn(self):
        pass

    def compileIf(self):
        pass

    def compileExpression(self):
        pass

    def compileTerm(self):
        pass

    def compileExpressionList(self):
        pass


def match_bracket(tokens, opening, closing):
    res = {}
    stack = []
    for index in range(0, len(tokens)):
        token = tokens[index]
        value = token.value
        if value == opening:
            stack.append(index)
        elif value == closing:
            left = stack.pop()
            res[left] = index
    return res
