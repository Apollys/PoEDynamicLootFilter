'''
[Implemented]
This script runs plyint with the -E flag to report all static errors in the
python code contained in the current directory.

[TODO - NYI]
This script also performs very minor code formatting for each .py file
in the current directory, consisting of the following:
 - Strip any trailing whitespace from each line
 - Ensure each file ends with a single blank line
'''

import os
import os.path

from consts import kBackendDirectory

kPylintCommand = 'pylint -E {}'.format(kBackendDirectory)

def main():
    print('Running: "{}"'.format(kPylintCommand))
    os.system(kPylintCommand)
    print('\nCode checks completetd.')

if (__name__ == '__main__'):
    main()
