def AssertEqual(left, right):
    if (left != right):
        raise RuntimeError('AssertEqual failed:\n  left parameter is: {}\n'
                '  right parameter is: {}'.format(left, right))
# End AssertEqual