def write_push(value):
    return 'push {}'.format(value)


def write_pop(value):
    return 'pop {}'.format(value)


def write_arithmetic(command):
    return command


def write_label(label):
    return 'label {}'.format(label)


def write_goto(label):
    return 'goto {}'.format(label)


def write_if(label):
    return 'if-goto {}'.format(label)


def write_call(name, nargs=None):
    if nargs is None:
        return 'call {}'.format(name)
    return 'call {} {}'.format(name, nargs)


def write_function(name, nargs):
    return 'function {} {}'.format(name, nargs)


def write_return():
    return 'return'
