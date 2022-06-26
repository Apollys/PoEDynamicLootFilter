from type_checker import CheckType, CheckTypesMatch

from test_assertions import AssertEqual, AssertFailure

def TestCorrectTypes():
    # Single string
    s = 'hello'
    CheckType(s, 's', str)
    # List of ints
    int_list = [1, 2, 3]
    CheckType(int_list, 'int_list', list, int)
    print('TestCorrectTypes passed!')

def TestIncorrectTypes():
    str_list = ['a', 'b', 'c']
    try:
        CheckType(str_list, 'str_list', list, int)
    except TypeError:  # this should happen
        pass
    else:  # this shouldn't happen
        AssertFailure()
    print('TestIncorrectTypes passed!')

def TestTypesMatch():
    an_integer = 5
    another_integer = 4509745487
    CheckTypesMatch(an_integer, 'an_integer', another_integer, 'another_integer')
    some_string = 'The quick brown fox'
    another_string = 'jumps over the lazy dog'
    CheckTypesMatch(some_string, 'some_string', another_string, 'another_string')
    # Expect mismatch between int and string
    try:
        CheckTypesMatch(an_integer, 'an_integer', some_string, 'some_string')
    except TypeError:  # this should happen
        pass
    else:  # this shouldn't happen
        AssertFailure()
    print('TestTypesMatch passed!')

def main():
    TestCorrectTypes()
    TestIncorrectTypes()
    TestTypesMatch()

if (__name__ == '__main__'):
    main()