from general_config import GeneralConfig, GeneralConfigKeywords, kGeneralConfigTemplate

import os.path

import file_helper
from test_assertions import AssertEqual, AssertTrue, AssertFalse
import test_consts

kTestGeneralConfigPath = os.path.join(test_consts.kTestWorkingDirectory, 'general.config')

# Tuples of (keyword, value, another_value)
kTestGeneralConfigValues = [
    (GeneralConfigKeywords.kActiveProfile, 'TestProfile', 'OtherProfile'),
    (GeneralConfigKeywords.kToggleGuiHotkey, '^F1', '!H'),
    (GeneralConfigKeywords.kWriteFilterHotkey, '+a', '+2'),
    (GeneralConfigKeywords.kReloadFilterHotkey, '!^F12', 'Tab')]

def TestParseGeneralConfig():
    general_config_string = kGeneralConfigTemplate.format(
            *(value for keyword, value, _ in kTestGeneralConfigValues))
    file_helper.WriteToFile(general_config_string, kTestGeneralConfigPath)
    general_config_obj = GeneralConfig(kTestGeneralConfigPath)
    for keyword, value, _ in kTestGeneralConfigValues:
        AssertEqual(general_config_obj[keyword], value)
    print('TestParseGeneralConfig passed!')

def TestSaveGeneralConfig():
    # Generate and parse config as above
    general_config_string = kGeneralConfigTemplate.format(
            *(value for keyword, value, _ in kTestGeneralConfigValues))
    file_helper.WriteToFile(general_config_string, kTestGeneralConfigPath)
    general_config_obj = GeneralConfig(kTestGeneralConfigPath)
    # Update values and save updated config
    for keyword, _, new_value in kTestGeneralConfigValues:
        general_config_obj[keyword] = new_value
    general_config_obj.SaveToFile()
    # Parse updated config and verify values are correct
    general_config_obj = GeneralConfig(kTestGeneralConfigPath)
    for keyword, _, new_value in kTestGeneralConfigValues:
        AssertEqual(general_config_obj[keyword], new_value)
    print('TestSaveGeneralConfig passed!')

def TestMissingGeneralConfig():
    file_helper.ClearAndRemoveDirectory(test_consts.kTestWorkingDirectory)
    general_config_obj = GeneralConfig(kTestGeneralConfigPath)
    for keyword in GeneralConfigKeywords.kKeywordsList:
        AssertTrue(keyword in general_config_obj)
    print('TestMissingGeneralConfig passed!')

def main():
    os.makedirs(test_consts.kTestWorkingDirectory, exist_ok=True)
    TestParseGeneralConfig()
    TestSaveGeneralConfig()
    file_helper.ClearAndRemoveDirectory(test_consts.kTestWorkingDirectory)
    TestMissingGeneralConfig()
    print('All tests passed!')

if (__name__ == '__main__'):
    main()