from test_helper import AssertEqual, AssertFailure
from type_checker import CheckType

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

def main():
    TestCorrectTypes()
    TestIncorrectTypes()

if (__name__ == '__main__'):
    main()