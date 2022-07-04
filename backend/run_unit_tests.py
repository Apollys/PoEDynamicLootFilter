'''
By default, skips slow tests (tests that take more than a few seconds).

Usage: python run_unit_tests <(optional) run_all_tests: int = 0>
'''

import os
import sys

import consts
import file_helper

kSlowTestFilenames = ['backend_cli_test.py']

kHorizontalSeparator = '=' * 80

def main():
    print(sys.argv)
    run_all_tests = False
    if ((len(sys.argv) >= 2) and bool(int(sys.argv[1]))):
        run_all_tests = True
    fullpaths = file_helper.ListFilesInDirectory(consts.kBackendDirectory, fullpath=True)
    unit_test_fullpaths = [f for f in fullpaths if f.endswith('_test.py')]
    failed_unit_tests = []
    print(kHorizontalSeparator)
    # Run tests
    for unit_test_fullpath in unit_test_fullpaths:
        unit_test_filename = os.path.basename(unit_test_fullpath)
        if (not run_all_tests and unit_test_filename in kSlowTestFilenames):
            continue
        command = 'python {}'.format(unit_test_fullpath)
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
        for passed_unit_test in unit_test_fullpaths:
            print(' • {}'.format(passed_unit_test))
    print(kHorizontalSeparator)

if (__name__ == '__main__'):
    main()