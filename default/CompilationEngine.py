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
        node.children.append(self.compileParameterList(left_para + 1, right_para - 1))
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
        node.children.append(Node(self.tokens[start].type, self.tokens[start].value))  # {
        slow = start + 1
        fast = start + 1

        while slow < end:
            if self._token_value(slow) != 'var':
                break
            if self.isVarDec(slow, fast):
                node.children.append(self.compileVarDec(slow, fast))
                slow = fast + 1
                fast = fast + 1
            else:
                fast += 1
        node.children.append(self.compileStatements(slow, end - 1))
        node.children.append(Node(self.tokens[end].type, self.tokens[end].value))  # }
        return node

    def isVarDec(self, start, end):
        if self._token_value(start) != 'var':
            return False
        index = start
        while index < end:
            if self._token_value(index) == ';':
                return False
            index += 1
        return self._token_value(end) == ';'

    def compileVarDec(self, start, end):
        node = Node('varDec', None)
        curr = start
        while curr <= end:
            node.children.append(Node(self.tokens[curr].type, self.tokens[curr].value))
            curr += 1
        return node

    def compileStatements(self, start, end):
        node = Node('statements', None)
        slow = start
        fast = start
        while slow <= end:
            if self.isIf(slow, fast):
                node.children.append(self.compileIf(slow, fast))
                slow = fast + 1
                fast = fast + 1
            elif self.isLet(slow, fast):
                node.children.append(self.compileLet(slow, fast))
                slow = fast + 1
                fast = fast + 1
            elif self.isWhile(slow, fast):
                node.children.append(self.compileWhile(slow, fast))
                slow = fast + 1
                fast = fast + 1
            elif self.isDo(slow, fast):
                node.children.append(self.compileDo(slow, fast))
                slow = fast + 1
                fast = fast + 1
            elif self.isReturn(slow, fast):
                node.children.append(self.compileReturn(slow, fast))
                slow = fast + 1
                fast = fast + 1
            else:
                fast += 1
        return node

    def isDo(self, start, end):
        if self._token_value(start) != 'do' or self._token_value(end) != ';':
            return False
        left_para = -1
        curr = start
        while curr < end:
            if self._token_value(curr) == '(':
                if left_para != -1:
                    return False
                left_para = curr
                curr = self.parenthesis[curr]
            curr += 1
        return left_para != -1

    def compileDo(self, start, end):
        node = Node('doStatement', None)
        node.children.append(Node(self.tokens[start].type, self.tokens[start].value))
        curr = start + 1
        while self._token_value(curr) != '(':
            node.children.append(Node(self.tokens[curr].type, self.tokens[curr].value))
            curr += 1
        node.children.append(Node(self.tokens[curr].type, self.tokens[curr].value))  # (
        node.children.append(self.compileExpressionList(curr + 1, self.parenthesis[curr] - 1))
        curr = self.parenthesis[curr]
        node.children.append(Node(self.tokens[curr].type, self.tokens[curr].value))  # )
        node.children.append(Node(self.tokens[end].type, self.tokens[end].value))  # ;
        return node

    def isLet(self, start, end):
        return self._token_value(start) == 'let' and self._token_value(end) == ';'

    def compileLet(self, start, end):
        node = Node('letStatement', None)
        curr = start
        while curr <= end and self._token_value(curr) != '[' and self._token_value(curr) != '=':
            node.children.append(Node(self.tokens[curr].type, self.tokens[curr].value))
            curr += 1
        if curr > end:
            return node
        if self._token_value(curr) == '[':
            node.children.append(Node(self.tokens[curr].type, self.tokens[curr].value))  # [
            node.children.append(self.compileExpression(curr + 1, self.square_bracket[curr] - 1))
            curr = self.square_bracket[curr]
            node.children.append(Node(self.tokens[curr].type, self.tokens[curr].value))  # ]
            curr += 1
        node.children.append(Node(self.tokens[curr].type, self.tokens[curr].value))  # =
        node.children.append(self.compileExpression(curr + 1, end - 1))
        node.children.append(Node(self.tokens[end].type, self.tokens[end].value))  # ;
        return node

    def isWhile(self, start, end):
        if self._token_value(start) != 'while':
            return False
        curr = start + 1
        if self._token_value(curr) != '(' or curr not in self.parenthesis.keys():
            return False
        curr = self.parenthesis[curr]
        curr += 1
        if self._token_value(curr) != '{' or curr not in self.bracket_map.keys():
            return False
        curr = self.bracket_map[curr]
        return curr == end

    def compileWhile(self, start, end):
        curr = start
        node = Node('whileStatement', None)
        node.children.append(Node(self.tokens[curr].type, self.tokens[curr].value))  # while
        curr += 1
        node.children.append(Node(self.tokens[curr].type, self.tokens[curr].value))  # (
        node.children.append(self.compileExpression(curr + 1, self.parenthesis[curr] - 1))
        curr = self.parenthesis[curr]
        node.children.append(Node(self.tokens[curr].type, self.tokens[curr].value))  # )
        curr += 1
        node.children.append(Node(self.tokens[curr].type, self.tokens[curr].value))  # {
        node.children.append(self.compileStatements(curr + 1, self.bracket_map[curr] - 1))
        node.children.append(Node(self.tokens[end].type, self.tokens[end].value))
        return node

    def isReturn(self, start, end):
        return self._token_value(start) == 'return' and self._token_value(end) == ';'

    def compileReturn(self, start, end):
        node = Node('returnStatement', None)
        node.children.append(Node(self.tokens[start].type, self.tokens[start].value))
        if start + 1 < end:
            node.children.append(self.compileExpression(start + 1, end - 1))
        node.children.append(Node(self.tokens[end].type, self.tokens[end].value))
        return node

    def isIf(self, start, end):
        if self._token_value(start) != 'if':
            return False
        curr = start + 1
        if self._token_value(curr) != '(' or curr not in self.parenthesis.keys():
            return False
        curr = self.parenthesis[curr] + 1  # {
        if self._token_value(curr) != '{' or curr not in self.bracket_map.keys():
            return False
        curr = self.bracket_map[curr]
        if curr == end:
            return self._token_value(curr + 1) != 'else'
        # have else
        curr += 1
        if self._token_value(curr) != 'else':
            return False
        curr += 1
        if self._token_value(curr) != '{' or curr not in self.bracket_map.keys():
            return False
        curr = self.bracket_map[curr]
        return curr == end

    def compileIf(self, start, end):
        curr = start
        node = Node('ifStatement', None)
        while self._token_value(curr) != '(':
            node.children.append(Node(self.tokens[curr].type, self.tokens[curr].value))
            curr += 1
        node.children.append(Node(self.tokens[curr].type, self.tokens[curr].value))  # (
        node.children.append(self.compileExpression(curr + 1, self.parenthesis[curr] - 1))
        curr = self.parenthesis[curr]
        node.children.append(Node(self.tokens[curr].type, self.tokens[curr].value))  # )
        curr += 1
        # {
        node.children.append(Node(self.tokens[curr].type, self.tokens[curr].value))
        node.children.append(self.compileStatements(curr + 1, self.bracket_map[curr] - 1))
        curr = self.bracket_map[curr]
        node.children.append(Node(self.tokens[curr].type, self.tokens[curr].value))  # }
        if curr == end:
            return node
        curr += 1
        node.children.append(Node(self.tokens[curr].type, self.tokens[curr].value))  # else
        curr += 1
        node.children.append(Node(self.tokens[curr].type, self.tokens[curr].value))  # {
        node.children.append(self.compileStatements(curr + 1, self.bracket_map[curr] - 1))
        curr = self.bracket_map[curr]
        node.children.append(Node(self.tokens[curr].type, self.tokens[curr].value))  # }
        return node

    def compileExpressionList(self, start, end):
        return Node('expressionList', None)

    def compileExpression(self, start, end):
        return Node('expression', None)

    def compileTerm(self):
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
