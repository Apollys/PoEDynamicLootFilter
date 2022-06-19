import os
import subprocess

import file_helper
import profile
import test_consts
from test_helper import AssertEqual, AssertTrue, AssertFalse

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

# Copied almost exactly from loot_filter_test.py
def SetUp():
    TearDown()
    # Make dirs if missing
    os.makedirs(test_consts.kTestWorkingDirectory, exist_ok=True)
    os.makedirs(test_consts.kTestProfileDownloadDirectory, exist_ok=True)
    os.makedirs(test_consts.kTestProfilePathOfExileDirectory, exist_ok=True)
    # Copy test filter to download directory
    file_helper.CopyFile(test_consts.kTestBaseFilter, 
            test_consts.kTestProfileDownloadedFilterFullpath)
# End SetUp

# Copied from loot_filter_test.py
def TearDown():
    # Delete test profile if it exists
    if (profile.ProfileExists(test_consts.kTestProfileName)):
        profile.DeleteProfile(test_consts.kTestProfileName)
    # Delete test working directory and all its contents
    file_helper.ClearAndRemoveDirectory(test_consts.kTestWorkingDirectory)
# End TearDown
    
def TestSetupPy():
    SetUp()
    # Communicate with subprocess: https://stackoverflow.com/a/165662
    p = subprocess.run(['python', '-u', 'setup.py'], stdout=subprocess.PIPE,
            input=GenerateSetupInputString(), encoding='utf-8')
    # print('\nSTDOUT:\n{}'.format(p.stdout))
    AssertEqual(p.returncode, 0)
    print('TestSetupPy passed!')

def main():
    TestSetupPy()
    TearDown()
    print('All tests passed!')

if (__name__ == '__main__'):
    main()