def write_push(segment, index=None):
    if not index:
        return 'push {}'.format(segment)
    return 'push {} {}'.format(segment, index)


def write_pop(segment, index):
    return 'pop {} {}'.format(segment, index)


def write_arithmetic(command):
    return command


def write_label(label):
    return 'label {}'.format(label)


def write_goto(label):
    return 'goto {}'.format(label)


def write_if(label):
    return 'if-goto {}'.format(label)


def write_call(name, nargs=None):
    if not nargs:
        return 'call {}'.format(name)
    return 'call {} {}'.format(name, nargs)


def write_function(name, nargs):
    return 'function {} {}'.format(name, nargs)


def write_return():
    return 'return'
