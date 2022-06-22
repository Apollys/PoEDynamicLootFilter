import os
import subprocess

import profile
import test_consts
from test_assertions import AssertEqual, AssertTrue, AssertFalse
import test_helper

kToggleGuiHotkey = '^F1'
kReloadFilterHotkey = '+F2'

def GenerateSetupInputString() -> str:
    input_list = [
            kToggleGuiHotkey,
            kReloadFilterHotkey,
            test_consts.kTestProfileName,
            test_consts.kTestProfileDownloadDirectory,
            test_consts.kTestProfileDownloadedFilterFilename,
            test_consts.kTestProfilePathOfExileDirectory,
            '']  # script ends with "Press Enter to close"
    return '\n'.join(input_list) + '\n'
# End GenerateSetupInput
    
def TestSetupPy():
    test_helper.SetUp(create_profile=False)
    # Communicate with subprocess: https://stackoverflow.com/a/165662
    p = subprocess.run(['python', '-u', 'setup.py'], stdout=subprocess.PIPE,
            input=GenerateSetupInputString(), encoding='utf-8')
    # print('\nSTDOUT:\n{}'.format(p.stdout))
    AssertEqual(p.returncode, 0)
    print('TestSetupPy passed!')

def main():
    TestSetupPy()
    test_helper.TearDown()
    print('All tests passed!')

if (__name__ == '__main__'):
    main()