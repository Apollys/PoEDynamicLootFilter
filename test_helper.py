def AssertEqual(left, right):
    if (left != right):
        raise RuntimeError('AssertEqual failed:\n  left parameter is: {}\n'
                '  right parameter is: {}'.format(left, right))
# End AssertEqual

def AssertTrue(value):
    if (value != True):
        raise RuntimeError('AssertTrue failed:\n  value is: {}'.format(value))
# End AssertTrue

def AssertFalse(value):
    if (value != False):
        raise RuntimeError('AssertFalse failed:\n  value is: {}'.format(value))
# End AssertFalse