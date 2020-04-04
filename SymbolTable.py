from constant import KIND_STATIC, KIND_FIELD, KIND_ARGUMENT, KIND_VAR, KIND_POINTER


class SymbolTable:
    kind_map = {KIND_STATIC: KIND_STATIC, KIND_FIELD: 'this', KIND_ARGUMENT: KIND_ARGUMENT, KIND_VAR: 'local',
                KIND_POINTER: 'pointer'}

    def __init__(self):
        self.class_table = {}
        self.subroutine_table = {}
        self.seq = {KIND_STATIC: 0, KIND_FIELD: 0, KIND_ARGUMENT: 0, KIND_VAR: 0, KIND_POINTER: 0}

    def start_subroutine(self):
        self.subroutine_table = {}
        self.__clear_seq(KIND_ARGUMENT)
        self.__clear_seq(KIND_VAR)

    def define(self, name: str, type: str, kind: str):
        if kind in [KIND_STATIC, KIND_FIELD]:
            if name in self.class_table.keys():
                raise ValueError('Duplicate Definition of variable {}.'.format(name))
            self.class_table[name] = {"type": type, "kind": kind, "id": self.__next_val(kind)}
        else:
            if name in self.subroutine_table.keys():
                raise ValueError('Duplicate Definition of variable {}.'.format(name))
            self.subroutine_table[name] = {"type": type, "kind": kind, "id": self.__next_val(kind)}

    def var_count(self, kind):
        if kind in [KIND_STATIC, KIND_FIELD]:
            return len([x for x in self.class_table.values() if x['kind'] == kind])
        return len([x for x in self.subroutine_table.values() if x['kind'] == kind])

    def kind_of(self, name):
        if name in self.subroutine_table.keys():
            return self.subroutine_table[name]['kind']
        elif name in self.class_table.keys():
            return self.class_table[name]['kind']
        raise ValueError('Symbol with name {} not found.'.format(name))

    def vm_kind_of(self, name):
        return self.kind_map[self.kind_of(name)]

    def is_variable(self, name):
        return name in self.subroutine_table.keys() or name in self.class_table.keys()

    def type_of(self, name):
        if name in self.subroutine_table.keys():
            return self.subroutine_table[name]['type']
        elif name in self.class_table.keys():
            return self.class_table[name]['type']
        raise ValueError('Symbol with name {} not found.'.format(name))

    def index_of(self, name):
        if name in self.subroutine_table.keys():
            return self.subroutine_table[name]['id']
        elif name in self.class_table.keys():
            return self.class_table[name]['id']
        raise ValueError('Symbol with name {} not found.'.format(name))

    def local_cnt(self):
        return len([x for x in self.subroutine_table.values() if x['kind'] == KIND_VAR])

    def __clear_seq(self, kind):
        self.seq[kind] = 0

    def __next_val(self, seq):
        value = self.seq[seq]
        self.seq[seq] += 1
        return value
