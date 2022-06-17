import os

import file_helper

kHorizontalSeparator = '================================================================================'

def main():
    filenames = file_helper.ListFilesInDirectory('.')
    unit_test_filenames = [f for f in filenames if f.endswith('_test.py')]
    failed_unit_tests = []
    print(kHorizontalSeparator)
    # Run all unit tests
    for unit_test_filename in unit_test_filenames:
        command = 'python {}'.format(unit_test_filename)
        print('Running: {} ...\n'.format(unit_test_filename))
        return_code = os.system(command)
        passed_flag = (return_code == 0)
        if (not passed_flag):
            failed_unit_tests.append(unit_test_filename)
        print('\n{} {}!'.format(unit_test_filename, 'passed' if passed_flag else 'FAILED'))
        print(kHorizontalSeparator)
    # Print a message indicating whether all tests passed, or some failed
    if (len(failed_unit_tests) > 0):
        print('Error: The following unit tests FAILED:')
        for failed_unit_test in failed_unit_tests:
            print(' • {}'.format(failed_unit_test))
    else:
        print('Congratulations! All unit tests passed:')
        for passed_unit_test in unit_test_filenames:
            print(' • {}'.format(passed_unit_test))
    print(kHorizontalSeparator)

if (__name__ == '__main__'):
    main()