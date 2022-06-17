from type_checker import CheckType

def main():
    # Single string
    s = 'hello'
    CheckType(s, 's', str)
    # List of ints
    int_list = [1, 2, 3]
    CheckType(int_list, 'int_list', list, int)
    print('No-error tests passed!')
    # Expect error
    print('Next test should raise an error:')
    str_list_error_check = ['a', 'b', 'c']
    CheckType(str_list_error_check, 'str_list_error_check', list, int)

if (__name__ == '__main__'):
    main()