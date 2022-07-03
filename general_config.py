import os.path

import file_helper

kGeneralConfigPath = os.path.join('config', 'general.config')

class GeneralConfigKeywords:
    kActiveProfile = 'Active Profile'
    kToggleGuiHotkey = 'Toggle GUI Hotkey'
    kWriteFilterHotkey = 'Write Filter Hotkey'
    kReloadFilterHotkey = 'Reload Filter Hotkey'

    kKeywordsList = [kActiveProfile, kToggleGuiHotkey, kWriteFilterHotkey, kReloadFilterHotkey]
# End class GeneralConfigKeywords

kDefaultConfigValues = {
    GeneralConfigKeywords.kActiveProfile: None,
    GeneralConfigKeywords.kToggleGuiHotkey: 'F7',
    GeneralConfigKeywords.kWriteFilterHotkey: 'F8',
    GeneralConfigKeywords.kReloadFilterHotkey: 'F9'
}

kGeneralConfigTemplateTemplate = \
'''# Profile
{0}: {4}

# Hotkeys
{1}: {4}
{2}: {4}
{3}: {4}
'''

kGeneralConfigTemplate = kGeneralConfigTemplateTemplate.format(
        *(GeneralConfigKeywords.kKeywordsList + ['{}']))

class GeneralConfig:
    '''
    This class manages the general.config file.

    Member variables:
     - self.path: str (default: kGeneralConfigPath defined above)
     - self.keyword_value_dict: dict[str, str] mapping keywords (defined above) to values
     - Allows keyword_value_dict to be manipulated directly via [] operator
    '''

    def __init__(self, general_config_path=kGeneralConfigPath):
        self.path = general_config_path
        self.keyword_value_dict = file_helper.ReadFileToDict(self.path)
        # Fill in default values for missing keywords
        for keyword in GeneralConfigKeywords.kKeywordsList:
            if (keyword not in self.keyword_value_dict):
                self.keyword_value_dict[keyword] = kDefaultConfigValues[keyword]

    def SaveToFile(self):
        values = [self.keyword_value_dict[keyword]
                for keyword in GeneralConfigKeywords.kKeywordsList]
        general_config_string = kGeneralConfigTemplate.format(*values)
        file_helper.WriteToFile(general_config_string, self.path)

    def __contains__(self, key):
        return key in self.keyword_value_dict

    def __getitem__(self, key):
        return self.keyword_value_dict[key]

    def __setitem__(self, key, value):
        self.keyword_value_dict[key] = value

# End class GeneralConfig