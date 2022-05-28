from collections import OrderedDict
from enum import Enum
import os
import os.path

import file_manip
import helper
import simple_parser
from type_checker import CheckType

kProfileDirectory = 'Profiles'
kGeneralConfigFilename = 'general.config'
kGeneralConfigFullpath = os.path.join(kProfileDirectory, kGeneralConfigFilename)

def GetProfileConfigFullpath(profile_name: str) -> str:
    return os.path.join(kProfileDirectory, profile_name + '.config')
# End GetProfileConfigFullpath
    
def GetProfileRulesFullpath(profile_name: str) -> str:
    return os.path.join(kProfileDirectory, profile_name + '.rules')
# End GetProfileRulesFullpath
    
def GetProfileChangesFullpath(profile_name: str) -> str:
    return os.path.join(kProfileDirectory, profile_name + '.changes')
# End GetProfileChangesFullpath

kActiveProfileTemplate = 'Active profile: {}'

kProfileConfigTemplate = \
'''# Profile config file for profile: "{}"

# Note: all blank lines and lines beginning with '#' are ignored
# Values after the colons may be modified, values before the
# colons are keyphrases and should be kept as-is.

# Loot filter file locations
Download directory: {}
Input (backup) loot filter directory: {}
# Location of Path of Exile filters (not the game client)
Path of Exile directory: {}
Downloaded loot filter filename: {}
Output (Path of Exile) loot filter filename: {}

# Remove filter from downloads directory when importing?
# Filter will still be saved in Input directory even if this is True
Remove downloaded filter: {}

# Loot filter options
Hide maps below tier: {}
Add chaos recipe rules: {}
Chaos recipe weapon classes, any height: {}
Chaos recipe weapon classes, max height 3: {}'''

# Map of keyphrases from config file to keywords used in the config_data dictionary
kProfileConfigKeyphraseToKeywordOrderedMap = OrderedDict([
        ('Download directory', 'DownloadDirectory'),
        ('Input (backup) loot filter directory', 'InputLootFilterDirectory'),
        ('Path of Exile directory', 'PathOfExileDirectory'),
        ('Downloaded loot filter filename', 'DownloadedLootFilterFilename'),
        ('Output (Path of Exile) loot filter filename', 'OutputLootFilterFilename'),
        ('Remove downloaded filter', 'RemoveDownloadedFilter'),
        ('Hide maps below tier', 'HideMapsBelowTier'),
        ('Add chaos recipe rules', 'AddChaosRecipeRules'),
        ('Chaos recipe weapon classes, any height', 'ChaosRecipeWeaponClassesAnyHeight'),
        ('Chaos recipe weapon classes, max height 3', 'ChaosRecipeWeaponClassesMaxHeight3')])

# Note: required values do not have a default value
kDefaultConfigValues = {
        # 'DownloadDirectory' : None,
        'InputLootFilterDirectory' : None,
        # 'PathOfExileDirectory' : None,
        # 'DownloadedLootFilterFilename' : None,
        'OutputLootFilterFilename' : 'DynamicLootFilter.filter',
        'RemoveDownloadedFilter' : True,
        'HideMapsBelowTier' : 0,
        'AddChaosRecipeRules' : True,
        'ChaosRecipeWeaponClassesAnyHeight' : 'Daggers, Rune Daggers, Wands',
        'ChaosRecipeWeaponClassesMaxHeight3' : 'Bows'}
        
kRequiredConfigKewords = [
        'DownloadDirectory',
        'PathOfExileDirectory',
        'DownloadedLootFilterFilename']

# Returns a (keyword, value) pair, or None
def ParseProfileConfigLine(line: str):
    CheckType(line, 'line', str)
    stripped_line = line.strip()
    if ((stripped_line == '') or stripped_line.startswith('#')):
        return None
    # Parse line
    parse_success, parse_results = simple_parser.ParseFromTemplate(stripped_line, '{}:{}')
    if (not parse_success):
        raise RuntimeError('failed to parse line {} of {}.config file'.format(
                line_number, profile_name))
    [keyphrase, value] = [s.strip() for s in parse_results]
    keyword = kProfileConfigKeyphraseToKeywordOrderedMap[keyphrase]
    # Perform additional specialized parsing for non-string types
    if (keyword in ('RemoveDownloadedFilter', 'AddChaosRecipeRules')):
        value = (value.lower() != 'false')
    elif (keyword == 'HideMapsBelowTier'):
        value = int(value)
    # Convert comma-separated chaos recipe classes to quote-enclosed classes
    elif ((keyword == 'ChaosRecipeWeaponClassesAnyHeight') or
          (keyword == 'ChaosRecipeWeaponClassesMaxHeight3')):
        classes_list = [s.strip() for s in value.split(',')]
        value = '"' + '" "'.join(classes_list) + '"'
    return keyword, value
# End ParseProfileConfigLine

'''
Exampe Profile config_values:

ProfileName : DefaultProfile (str)
DownloadDirectory : FiltersDownload (str)
InputLootFilterDirectory : FiltersInput (str) (derived)
PathOfExileDirectory : FiltersPathOfExile (str)
DownloadedLootFilterFilename : BrandLeaguestart.filter (str)
OutputLootFilterFilename : DynamicLootFilter.filter (str)
RemoveDownloadedFilter : False (bool)
HideMapsBelowTier : 0 (int)
AddChaosRecipeRules : True (str)
ChaosRecipeWeaponClassesAnyHeight : "Daggers" "Rune Daggers" "Wands" (str)
ChaosRecipeWeaponClassesMaxHeight3 : "Bows" (str)
DownloadedLootFilterFullpath : FiltersDownload/BrandLeaguestart.filter (str) (derived)
InputLootFilterFullpath : FiltersInput/BrandLeaguestart.filter (str) (derived)
OutputLootFilterFullpath : FiltersPathOfExile/DynamicLootFilter.filter (str) (derived)
'''

class Profile:
    '''
    Member variables:
     - name: str
     - config_path: str
     - changes_path: str
     - rules_path: str
     - config_values: dict {keyword : value}
    '''
    
    # ------------------------------ Public API ------------------------------
    
    # If profile of given name exists, parses the config.
    # If profile does not exist, creates a new profile with given config values.
    # Note: config_values should be empty (default) for existing profile,
    # and should contain all required config values for creating a new profile.
    def __init__(self, name: str, config_values: dict = {}):
        CheckType(name, 'name', str)
        self.name = name
        path_basename = os.path.join(kProfileDirectory, self.name)
        self.config_path = path_basename + '.config'
        self.changes_path = path_basename + '.changes'
        self.rules_path = path_basename + '.rules'
        # Initialize config_values to default values
        self.config_values = {k : v for k, v in kDefaultConfigValues.items()}
        # If profile exists, parse config_values from file
        if (os.path.isfile(self.config_path)):
            self.LoadConfigs()
        # If profile does not exist, load passed in config_values
        else:
            for k, v in config_values.items():
                self.config_values[k] = v
        self.UpdateAndValidateConfigValues()
    # End __init__

    def LoadConfigs(self):
        if (os.path.isfile(self.config_path)):
            with open(self.config_path) as config_file:
                for line in config_file:
                    parse_result = ParseProfileConfigLine(line)
                    if (parse_result):
                        keyword, value = parse_result
                        self.config_values[keyword] = value
        else:
            raise RuntimeError('Config file {} does not exist'.format(self.config_path))
        # TODO (maybe): also load .rules and .changes files?
    # End LoadConfigs
    
    def WriteConfigs(self):
        self.UpdateAndValidateConfigValues()
        # Write .config file
        keywords = [v for k, v in kProfileConfigKeyphraseToKeywordOrderedMap.items()]
        format_params = [self.name] + [self.config_values[keyword] for keyword in keywords]
        config_string = kProfileConfigTemplate.format(*format_params)
        helper.WriteToFile(config_string, self.config_path)
        # Create blank .changes file, if does not exist
        if (not os.path.isfile(self.changes_path)):
            helper.WriteToFile('', self.changes_path)
        # Create blank .rules file, if does not exist
        if (not os.path.isfile(self.rules_path)):
            helper.WriteToFile('', self.rules_path)
    # End WriteConfigs
        
    # ------------------------------ Helper Functions ------------------------------
    
    # Update and Validate config values:
    # 1. Verifies that all required config values are present.
    # 2. Re-computes all derived config values.
    # 3. Checks for missing files and directories:
    #    - Creates them if absense is not an error
    #    - Raises an error otherwise
    def UpdateAndValidateConfigValues(self):
        # Verify that all required config values are present
        for keyword in kRequiredConfigKewords:
            if (keyword not in self.config_values):
                raise RuntimeError('Profile {} missing required field: "{}"'.format(
                        self.name, keyword))
        # Compute derived config values
        self.config_values['DownloadedLootFilterFullpath'] = os.path.join(
                self.config_values['DownloadDirectory'], self.config_values['DownloadedLootFilterFilename'])
        self.config_values['InputLootFilterDirectory'] = os.path.join(
                self.config_values['PathOfExileDirectory'], self.name + 'InputFilters')
        self.config_values['InputLootFilterFullpath'] = os.path.join(
                self.config_values['InputLootFilterDirectory'], self.config_values['DownloadedLootFilterFilename'])
        self.config_values['OutputLootFilterFullpath'] = os.path.join(
                self.config_values['PathOfExileDirectory'], self.config_values['OutputLootFilterFilename'])
        # For convenience, add changes path to config, because it's used by backend_cli.py
        self.config_values['ChangesFullpath'] = self.changes_path
        # Check that required directories exist, raise error if not
        if (not os.path.isdir(self.config_values['DownloadDirectory'])):
            raise RuntimeError('download directory: "{}" does not exist'.format(
                    self.config_values['DownloadDirectory']))
        if (not os.path.isdir(self.config_values['PathOfExileDirectory'])):
            raise RuntimeError('Path of Exile directory: "{}" does not exist'.format(
                    self.config_values['PathOfExileDirectory']))
        # Create missing optional directories
        os.makedirs(self.config_values['InputLootFilterDirectory'], exist_ok = True)
        # TODO: create blank .changes and .rules files if don't exist?
    # End UpdateAndValidateConfigValues
        
# End class Profile

# Returns a bool indicating whether or not there is a .config file
# corresponding to the given profile name.
def ProfileExists(profile_name: str) -> bool:
    return os.path.isfile(os.path.join(kProfileDirectory, profile_name + '.config'))

def GetActiveProfileName() -> str:
    if (not os.path.isdir(kProfileDirectory)):
        raise RuntimeError('Profile directory: "{}" does not exist'.format(kProfileDirectory))
    if (not os.path.isfile(kGeneralConfigFullpath)):
        raise RuntimeError('General config: "{}" does not exist'.format(kGeneralConfigFullpath))
    general_config_lines = [line.strip() for line in helper.ReadFile(kGeneralConfigFullpath)]
    nonempty_lines = [line for line in general_config_lines if line != '']
    if (len(nonempty_lines) == 0):
        return None
    parse_success, parse_results = simple_parser.ParseFromTemplate(
            nonempty_lines[0], kActiveProfileTemplate)
    return  parse_results[0] if parse_success else None
# End GetActiveProfileName

# Sets the currently active profile to the profile of the given name.
# Raises an error if the given profile does not exist.
def SetActiveProfile(profile_name: str):
    if (not os.path.isdir(kProfileDirectory)):
        raise RuntimeError('Profile directory: "{}" does not exist'.format(kProfileDirectory))
    profile_config_path = os.path.join(kProfileDirectory, profile_name + '.config')
    if (not ProfileExists(profile_name)):
        raise RuntimeError('Profile "{}" does not exist'.format(profile_name))
    with open(kGeneralConfigFullpath, 'w') as general_config_file:
        general_config_file.write(kActiveProfileTemplate.format(profile_name))
# End SetActiveProfile

# Checks if the active profile as defined in general config exists.
# If it does not exist, sets the first found profile as the active profile.
# Returns a list of strings, each string containing the name of a profile.
# The first item in the list is the currently active profile.
def GetAllProfileNames() -> list[str]:
    if (not os.path.isdir(kProfileDirectory)):
        raise RuntimeError('Profile directory: "{}" does not exist'.format(kProfileDirectory))
    active_profile_name = GetActiveProfileName()
    profile_names: list[str] = [active_profile_name] if active_profile_name else ['']
    profile_files_list: list[str] = file_manip.ListFilesInDirectory(kProfileDirectory)
    found_active_profile: bool = False
    for filename in profile_files_list:
        if (filename == 'general.config'):
            continue
        profile_name, extension = os.path.splitext(filename)
        if (extension == '.config'):
            if (profile_name == active_profile_name):
                found_active_profile = True
            else:
                profile_names.append(profile_name)
    # If we did not find the active profile name, it must have been deleted.
    # Make the first found profile the active profile.
    if (not found_active_profile):
        profile_names = profile_names[1:]
        SetActiveProfile(profile_names[0])
    return profile_names
# End GetAllProfileNames

# Returns the created Profile, or None if the profile already exists.
# config_values must contain the required keywords:
#   'DownloadDirectory', 'PathOfExileDirectory', 'DownloadedLootFilterFilename'
# Note: config_values is dict of string -> string here, but may expect other types later
def CreateNewProfile(profile_name: str, config_values: dict) -> Profile:
    CheckType(profile_name, 'profile_name', str)
    CheckType(config_values, 'config_values', dict)
    if (profile_name in GetAllProfileNames()):
        return None
    new_profile = Profile(profile_name, config_values)
    new_profile.WriteConfigs()
    SetActiveProfile(profile_name)
    return new_profile
# End CreateNewProfile

def Test():
    print('Test')
    active_profile_name = GetActiveProfileName()
    print('active_profile_name =', active_profile_name)
    all_profile_names = GetAllProfileNames()
    print('all_profile_names =', all_profile_names)
    print()
    
    # parsed_config_data = ParseProfileConfig('DefaultProfile')
    # print('parsed config data:')
    #for key, value in parsed_config_data.items():
        #print('{} : {} ({})'.format(key, value, type(value).__name__))
# End Test

def TestCreateProfile():
    print('TestCreateProfile')
    config_values = {
            'DownloadDirectory' : 'FiltersDownload',
            'PathOfExileDirectory' : 'FiltersPathOfExile',
            'DownloadedLootFilterFilename' : 'MySpecialFilter.filter'}
    new_profile = CreateNewProfile('NewProfile', config_values)
    active_profile_name = GetActiveProfileName()
    print('active_profile_name =', active_profile_name)
    print()
# End TestCreateProfile

def TestLoadProfile():
    print('TestLoadProfile')
    profile = Profile('Apollys')
    for key, value in profile.config_values.items():
        print('{} : {} ({})'.format(key, value, type(value).__name__))
    print()

# Test()
# TestCreateProfile()
# TestLoadProfile()