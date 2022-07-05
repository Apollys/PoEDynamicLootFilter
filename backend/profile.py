'''
Auxiliary free functions:
 - GetProfileConfigFullpath(profile_name: str) -> str
 - GetProfileChangesFullpath(profile_name: str) -> str
 - GetProfileRulesFullpath(profile_name: str) -> str
 - ListProfilesRaw() -> List[str]
 - ProfileExists(profile_name: str) -> bool
 - GetActiveProfileName() -> str
 - SetActiveProfile(profile_name: str)
 - GetAllProfileNames() -> List[str]

Higher level profile functions:
 - CreateNewProfile(profile_name: str, config_values: dict) -> Profile
 - RenameProfile(original_profile_name: str, new_profile_name: str)
 - DeleteProfile(profile_name: str)

Internal helper functions:
 - ParseProfileConfigLine(line: str) -> Tuple[str, Any]

It also defines a class Profile for manipulating profiles.
'''

from collections import OrderedDict
from enum import Enum
import os
import os.path
from typing import Any, List, Tuple

from consts import kProfileDirectory
import file_helper
from general_config import GeneralConfig, GeneralConfigKeywords, kGeneralConfigPath
import simple_parser
from type_checker import CheckType

def GetProfileConfigFullpath(profile_name: str) -> str:
    return os.path.join(kProfileDirectory, profile_name + '.config')
# End GetProfileConfigFullpath

def GetProfileChangesFullpath(profile_name: str) -> str:
    return os.path.join(kProfileDirectory, profile_name + '.changes')
# End GetProfileChangesFullpath

def GetProfileRulesFullpath(profile_name: str) -> str:
    return os.path.join(kProfileDirectory, profile_name + '.rules')
# End GetProfileRulesFullpath

# Returns a list of profile names as defined by:
#  - files of extensions 'config' whose name is not 'general.config'
# Does not perform any additional validation or modification of general.config.
def ListProfilesRaw() -> List[str]:
    profile_files_list: list[str] = file_helper.ListFilesInDirectory(kProfileDirectory)
    profile_names = []
    for filename in profile_files_list:
        # This is not needed any more, but for backwards compatibility for previous version,
        # we will retain it for a little while.
        if (filename == 'general.config'):
            continue
        profile_name, extension = os.path.splitext(filename)
        if (extension == '.config'):
            profile_names.append(profile_name)
    return profile_names
# End ListProfilesRaw

# Returns a bool indicating whether or not there is a .config file
# corresponding to the given profile name.
def ProfileExists(profile_name: str) -> bool:
    return profile_name in ListProfilesRaw()
# End ProfileExists

# Returns the active profile name as a string, or None.
def GetActiveProfileName() -> str:
    if (not os.path.isfile(kGeneralConfigPath)):
        return None
    general_config_obj = GeneralConfig()
    return general_config_obj[GeneralConfigKeywords.kActiveProfile]
# End GetActiveProfileName

# Sets the currently active profile to the profile of the given name.
# Raises an error if the given profile does not exist.
def SetActiveProfile(profile_name: str):

    general_config_obj = GeneralConfig()
    general_config_obj[GeneralConfigKeywords.kActiveProfile] = profile_name
    general_config_obj.SaveToFile()
# End SetActiveProfile

# Returns a list of strings containing all the profile names.
# If the list is nonempty, the first item is the active profile.
# Enforces consistency between existing profiles and general.config.
# Consistent states are either:
#  - general.config does not exist / is empty, and there are no profiles, or
#  - general.config contains a valid active profile, and at least one profile exists
# If there is an inconsistency, this is fixed by setting general.config
# to have some valid profile as the active profile.
def GetAllProfileNames() -> List[str]:
    raw_profile_list = ListProfilesRaw()
    if (len(raw_profile_list) == 0):
        file_helper.RemoveFileIfExists(kGeneralConfigPath)
        return []
    active_profile_name = GetActiveProfileName()
    if (active_profile_name not in raw_profile_list):
        SetActiveProfile(raw_profile_list[0])
        return raw_profile_list
    # Otherwise, active profile name is valid and in raw_profile_list
    # We need to place the active profile in the first position in raw_profile_list
    i = raw_profile_list.index(active_profile_name)
    if (i != 0):
        raw_profile_list[0], raw_profile_list[i] = raw_profile_list[i], raw_profile_list[0]
    return raw_profile_list
# End GetAllProfileNames

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
def ParseProfileConfigLine(line: str) -> Tuple[str, Any]:
    CheckType(line, 'line', str)
    stripped_line = line.strip()
    if ((stripped_line == '') or stripped_line.startswith('#')):
        return None
    # Parse line
    parse_success, parse_results = simple_parser.ParseFromTemplate(stripped_line, '{}:{}')
    if (not parse_success):
        raise RuntimeError('failed to parse profile config line: {} '.format(stripped_line))
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
            with open(self.config_path, encoding='utf-8') as config_file:
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
        file_helper.WriteToFile(config_string, self.config_path)
        # Create blank .changes file, if does not exist
        if (not os.path.isfile(self.changes_path)):
            file_helper.WriteToFile('', self.changes_path)
        # Create blank .rules file, if does not exist
        if (not os.path.isfile(self.rules_path)):
            file_helper.WriteToFile('', self.rules_path)
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
        self.config_values['ProfileName'] = self.name
        self.config_values['DownloadedLootFilterFullpath'] = os.path.join(
                self.config_values['DownloadDirectory'], self.config_values['DownloadedLootFilterFilename'])
        self.config_values['InputLootFilterDirectory'] = os.path.join(
                self.config_values['PathOfExileDirectory'], self.name + 'InputFilters')
        self.config_values['InputLootFilterFullpath'] = os.path.join(
                self.config_values['InputLootFilterDirectory'], self.config_values['DownloadedLootFilterFilename'])
        self.config_values['OutputLootFilterFullpath'] = os.path.join(
                self.config_values['PathOfExileDirectory'], self.config_values['OutputLootFilterFilename'])
        # These are still used in backend_cli.py - keep them for convenience for now
        self.config_values['ConfigFullpath'] = self.config_path
        self.config_values['ChangesFullpath'] = self.changes_path
        self.config_values['RulesFullpath'] = self.rules_path
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

# Returns the created Profile, or None if the profile already exists.
# config_values must contain the required keywords:
#   'DownloadDirectory', 'PathOfExileDirectory', 'DownloadedLootFilterFilename'
# Note: config_values is dict of string -> string here, but may expect other types later
def CreateNewProfile(profile_name: str, config_values: dict) -> Profile:
    CheckType(profile_name, 'profile_name', str)
    CheckType(config_values, 'config_values', dict)
    # Return None if profile already exists
    if (profile_name in GetAllProfileNames()):
        return None
    # Create new profile
    new_profile = Profile(profile_name, config_values)
    new_profile.WriteConfigs()
    SetActiveProfile(profile_name)
    return new_profile
# End CreateNewProfile

# TODO: If original_profile_name is the currently active profile,
# update the active profile in general.config.
def RenameProfile(original_profile_name: str, new_profile_name: str):
    CheckType(original_profile_name, 'original_profile_name', str)
    CheckType(new_profile_name, 'new_profile_name', str)
    if (original_profile_name not in ListProfilesRaw()):
        raise RuntimeError('profile {} does not exist'.format(original_profile_name))
    # Rename all files with basename equal to original_profile_name
    for filename in file_helper.ListFilesInDirectory(kProfileDirectory):
        profile_name, extension = os.path.splitext(filename)
        if (profile_name == original_profile_name):
            source_path = os.path.join(kProfileDirectory, filename)
            target_path = os.path.join(kProfileDirectory, new_profile_name + extension)
            file_helper.MoveFile(source_path, target_path)
# End RenameProfile

# Raises an error if the profile does not exist.
def DeleteProfile(profile_name: str):
    CheckType(profile_name, 'profile_name', str)
    if (not ProfileExists(profile_name)):
        raise RuntimeError('profile {} does not exist'.format(profile_name))
    # Remove all files with basename equal to profile_name
    for filepath in file_helper.ListFilesInDirectory(kProfileDirectory, fullpath=True):
        if (file_helper.FilenameWithoutExtension(filepath) == profile_name):
            os.remove(filepath)
    # Update general.config if we deleted the active profile
    if (GetActiveProfileName() == profile_name):
        # A little hacky, since GetAllProfileNames enforces the consistency
        # between general.config and profiles that we desire, we just call it.
        GetAllProfileNames()
# DeleteProfile
