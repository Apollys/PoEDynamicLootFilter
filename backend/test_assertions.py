def DictMismatchMessage(left: dict, right: dict) -> str:
    left_keys_set = set(left.keys())
    right_keys_set = set(right.keys())
    if (left_keys_set - right_keys_set):
        return ('the following keys are present in the left dict but not the right: '
                '{}'.format(left_keys_set - right_keys_set))
    elif (right_keys_set - left_keys_set):
        return ('the following keys are present in the right dict but not the left: '
                '{}'.format(right_keys_set - left_keys_set))
    else:
        for key in left:
            if (left[key] != right[key]):
                return ('Key "{}" has value "{}" in the left dict and value "{}" '
                        'in the right dict'.format(key, left[key], right[key]))
    return "Something weird happened, you shouldn't see this"
# End DictMismatchMessage

def AssertEqual(left, right):
    if (left != right):
        # Display more detailed message for dict types
        if (isinstance(left, dict) and isinstance(right, dict)):
            raise AssertionError('AssertEqual failed:\n  {}'.format(
                    DictMismatchMessage(left, right)))
        else:
            raise AssertionError('AssertEqual failed:\n  Left parameter is: {}\n'
                    '  Right parameter is: {}'.format(left, right))
# End AssertEqual

def AssertTrue(value):
    if (value != True):
        raise AssertionError('AssertTrue failed:\n  Value is: {}'.format(value))
# End AssertTrue

def AssertFalse(value):
    if (value != False):
        raise AssertionError('AssertFalse failed:\n  Value is: {}'.format(value))
# End AssertFalse

def AssertFailure():
    raise AssertionError('AssertFailure reached: this code should be unreachable')
# End AssertFalse