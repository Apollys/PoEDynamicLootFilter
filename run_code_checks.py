'''
[TODO - NYI]
This script first performs very minor code formatting for each .py file
in the current directory, consisting of the following:
 - Strip any trailing whitespace from each line
 - Ensure each file ends with a single blank line

[Implemented]
It then also runs plyint with the -E flag to report all static errors in the
python code contained in the current directory.
'''

import os
import os.path

kStartingDirectoryName = os.path.dirname(os.path.realpath(__file__))
kPylintCommand= 'cd .. && pylint -E {}'.format(kStartingDirectoryName)

def main():
    print('Running: "{}"'.format(kPylintCommand))
    os.system(kPylintCommand)

if (__name__ == '__main__'):
    main()
