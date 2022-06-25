import os
import subprocess
from typing import Tuple

import profile
import test_consts
from test_assertions import AssertEqual, AssertTrue, AssertFalse
import test_helper

kToggleGuiHotkey = '^F1'
kWriteFilterHotkey = '+F2'
kReloadFilterHotkey = '!F3'

def GenerateSetupInputString(hotkeys: Tuple[str]) -> str:
    toggle_gui_hotkey, write_filter_hotkey, reload_filter_hotkey = hotkeys
    input_list = [
            toggle_gui_hotkey,
            write_filter_hotkey,
            reload_filter_hotkey,
            test_consts.kTestProfileName,
            test_consts.kTestProfileDownloadDirectory,
            test_consts.kTestProfileDownloadedFilterFilename,
            test_consts.kTestProfilePathOfExileDirectory,
            '']  # script ends with "Press Enter to close"
    return '\n'.join(input_list) + '\n'
# End GenerateSetupInput

def RunSetupPy(hotkeys: Tuple[str]):
    test_helper.SetUp(create_profile=False)
    # Communicate with subprocess: https://stackoverflow.com/a/165662
    p = subprocess.run(['python', '-u', 'setup.py'], stdout=subprocess.PIPE,
            input=GenerateSetupInputString(hotkeys),
            encoding='utf-8')
    AssertEqual(p.returncode, 0)
# End RunSetupPy

def TestSetupPy():
    # Test with control/alt codes in hotkeys
    RunSetupPy((kToggleGuiHotkey, kWriteFilterHotkey, kReloadFilterHotkey))
    # Reset default hotkeys (TODO: reset to hotkeys used before test was run)
    RunSetupPy(('', '', ''))
    print('TestSetupPy passed!')

def main():
    TestSetupPy()
    test_helper.TearDown()
    print('All tests passed!')

if (__name__ == '__main__'):
    main()