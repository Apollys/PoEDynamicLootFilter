form enum import Enum
import os
import os.path

import file_manip
import helper
import simple_parser
from type_checker import CheckType

kProfileDirectory = 'Profiles'
kGeneralConfigFilename = 'general.config'
kGeneralConfigFullpath = os.path.join(kProfileDirectory, kGeneralConfigFilename)

kActiveProfileTemplate = 'Active profile: {}'

kProfileConfigTemplate = \
'''# Profile config file for profile: "{}"

# Note: all blank lines and lines beginning with '#' are ignored
# Values after the colons may be modified, values before the
# colons are keyphrases and should be kept as-is.

# Loot filter file locations
Download directory: FiltersDownload
Input (backup) loot filter directory: FiltersInput
# Location of Path of Exile filters (not the game client)
Path of Exile directory: FiltersPathOfExile
Downloaded loot filter filename: NeversinkRegular.filter
Output (Path of Exile) loot filter filename: DynamicLootFilter.filter

# Remove filter from downloads directory when importing?
# Filter will still be saved in Input directory even if this is True
Remove downloaded filter: True

# Loot filter options
Hide maps below tier: 0
Add chaos recipe rules: True
Chaos recipe weapon classes, any height: Daggers, Rune Daggers, Wands
Chaos recipe weapon classes, max height 3: Bows'''

# Map of keyphrases from config file to keywords used in the config_data dictionary
kProfileConfigKeyphraseMap = {
        'Download directory' : 'DownloadDirectory',
        'Input (backup) loot filter directory' : 'InputLootFilterDirectory',
        'Path of Exile directory' : 'PathOfExileDirectory',
        'Downloaded loot filter filename' : 'DownloadedLootFilterFilename',
        'Output (Path of Exile) loot filter filename' : 'OutputLootFilterFilename',
        'Remove downloaded filter' : 'RemoveDownloadedFilter',
        'Hide maps below tier' : 'HideMapsBelowTier',
        'Add chaos recipe rules' : 'AddChaosRecipeRules',
        'Chaos recipe weapon classes, any height' : 'ChaosRecipeWeaponClassesAnyHeight',
        'Chaos recipe weapon classes, max height 3' : 'ChaosRecipeWeaponClassesMaxHeight3'}

class ConstructProfileEnum(Enum):
    kConstructNew = 1
    kParseConfig = 2
# End ConstructProfileEnum

class Profile:
    '''
    Member variables:
     - name: str
     - config_path: str
     - changes_path: str
     - rules_path: str
     - config_data: dict {keyphrase : value}
    '''
    
    # Note: do not call directly, instead use ConstructNewProfile or ParseProfileConfig
    # defined below.
    def __init__(self, name: str, construct_profile_enum: ConstructProfileEnum):
        CheckType(name, 'name', str)
        CheckType(construct_profile_enum, 'construct_profile_enumv', ConstructProfileEnum)
        self.name = name
        path_basename = os.path.join(kProfileDirectory, self.name)
        self.config_path = path_basename + '.config'
        self.changes_path = path_basename + '.changes'
        self.rules_path = path_basename + '.rules'
        if (construct_profile_enum == ConstructProfileEnum::kConstructNew):
            pass
        elif (construct_profile_enum == ConstructProfileEnum::kParseConfig):
            pass
    # End init

    def LoadConfig(self):
        pass
    
    def WriteConfig(self):
        pass
        
    def 
# End class Profile

def GetActiveProfileName() -> str:
    if (not os.path.isdir(kProfileDirectory)):
        raise RuntimeError('Profile directory: "{}" does not exist'.format(kProfileDirectory))
    if (not os.path.isfile(kGeneralConfigFullpath)):
        return None
    general_config_lines = [line.strip() for line in helper.ReadFile(kGeneralConfigFullpath)]
    nonempty_lines = [line for line in general_config_lines if line != '']
    if (len(nonempty_lines) == 0):
        return None
    parse_success, parse_results = simple_parser.ParseFromTemplate(
            nonempty_lines[0], kActiveProfileTemplate)
    return  parse_results[0] if parse_success else None
# End GetActiveProfileName

def SetActiveProfile(profile_name: str):
    if (not os.path.isdir(kProfileDirectory)):
        raise RuntimeError('Profile directory: "{}" does not exist'.format(kProfileDirectory))
    with open(kGeneralConfigFullpath, 'w') as general_config_file:
        general_config_file.write(kActiveProfileTemplate.format(profile_name))
# End SetActiveProfile

# Returns a list of strings, each string containing the name of a profile
# The first item in the list is the currently active profile
def GetAllProfileNames() -> list:
    if (not os.path.isdir(kProfileDirectory)):
        raise RuntimeError('Profile directory: "{}" does not exist'.format(kProfileDirectory))
    active_profile_name = GetActiveProfileName()
    profile_names: list[str] = [active_profile_name] if active_profile_name else ['']
    profile_files_list: list[str] = file_manip.ListFilesInDirectory(kProfileDirectory)
    for filename in profile_files_list:
        if (filename == 'general.config'):
            continue
        profile_name, extension = os.path.splitext(filename)
        if ((extension == '.config') and (profile_name != profile_names[0])):
            profile_names.append(profile_name)
    return profile_names
# End GetAllProfileNames

# Returns true if new profile was created, false if profile already exists
def CreateNewProfile(new_profile_name: str) -> bool:
    CheckType(new_profile_name, 'new_profile_name', str)
    if (new_profile_name in GetAllProfileNames()):
        return False
    new_profile_config_text = kProfileConfigTemplate.format(new_profile_name)
    new_profile_config_fullpath = os.path.join(kProfileDirectory, new_profile_name + '.config')
    helper.WriteToFile(new_profile_config_text, new_profile_config_fullpath)
    helper.WriteToFile('', os.path.join(kProfileDirectory, new_profile_name + '.changes'))
    helper.WriteToFile('', os.path.join(kProfileDirectory, new_profile_name + '.rules'))
    SetActiveProfile(new_profile_name)
    return True
# End CreateNewProfile

def GetProfileConfigFullpath(profile_name: str) -> str:
    return os.path.join(kProfileDirectory, profile_name + '.config')
# End GetProfileConfigFullpath
    
def GetProfileRulesFullpath(profile_name: str) -> str:
    return os.path.join(kProfileDirectory, profile_name + '.rules')
# End GetProfileRulesFullpath
    
def GetProfileChangesFullpath(profile_name: str) -> str:
    return os.path.join(kProfileDirectory, profile_name + '.changes')
# End GetProfileChangesFullpath

def ParseProfileConfig(profile_name: str) -> dict:
    CheckType(profile_name, 'profile_name', str)
    config_data = {}
    config_data['ProfileName'] = profile_name
    config_data['ConfigFullpath'] = GetProfileConfigFullpath(profile_name)
    config_data['RulesFullpath'] = GetProfileRulesFullpath(profile_name)
    config_data['ChangesFullpath'] = GetProfileChangesFullpath(profile_name)
    # Config file is required, raise error if not present
    if (not os.path.isfile(config_data['ConfigFullpath'])):
        raise RuntimeError('file {} does not exist'.format(config_data['ConfigFullpath']))
    # Rules and Changes files are optional, we create them if they don't exist
    open(config_data['RulesFullpath'], 'a').close()
    open(config_data['ChangesFullpath'], 'a').close()
    # Parse config file line by line
    profile_config_lines = helper.ReadFile(config_data['ConfigFullpath'])
    line_number: int = 1
    for line in profile_config_lines:
        stripped_line = line.strip()
        if ((stripped_line == '') or (stripped_line.startswith('#'))):
            continue
        parse_success, parse_results = simple_parser.ParseFromTemplate(stripped_line, '{}:{}')
        if (not parse_success):
            raise RuntimeError('failed to parse line {} of {}.config file'.format(
                    line_number, profile_name))
        parse_results = [s.strip() for s in parse_results]
        [keyphrase, value] = parse_results
        normalized_keyphrase = kProfileConfigKeyphraseMap[keyphrase]
        # Perform additional specialized parsing for non-string types
        if (normalized_keyphrase == 'RemoveDownloadedFilter'):
            value = (value.lower() != 'false')
        elif (normalized_keyphrase == 'HideMapsBelowTier'):
            value = int(value)
        # Convert comma-separated list of chaos recipe classes to quote-enclosed list
        elif ((normalized_keyphrase == 'ChaosRecipeWeaponClassesAnyHeight') or
              (normalized_keyphrase == 'ChaosRecipeWeaponClassesMaxHeight3')):
            classes_list = [s.strip() for s in value.split(',')]
            value = '"' + '" "'.join(classes_list) + '"'
        config_data[normalized_keyphrase] = value
        line_number += 1
    # Check that config contains all required fields
    for keyphrase, normalized_keyphrase in kProfileConfigKeyphraseMap.items():
        if normalized_keyphrase not in config_data:
            raise RuntimeError('Config file {} missing required field: "{}"'.format(
                    profile_name + '.config', keyphrase))
    # Compute derived config values
    config_data['DownloadedLootFilterFullpath'] = os.path.join(
            config_data['DownloadDirectory'], config_data['DownloadedLootFilterFilename'])
    config_data['InputLootFilterFullpath'] = os.path.join(
            config_data['InputLootFilterDirectory'], config_data['DownloadedLootFilterFilename'])
    config_data['OutputLootFilterFullpath'] = os.path.join(
            config_data['PathOfExileDirectory'], config_data['OutputLootFilterFilename'])
    # Check that required directories exist, raise error if not
    if (not os.path.isdir(config_data['DownloadDirectory'])):
        raise RuntimeError('download directory: "{}" does not exist'.format(
                config_data['DownloadDirectory']))
    if (not os.path.isdir(config_data['PathOfExileDirectory'])):
        raise RuntimeError('Path of Exile directory: "{}" does not exist'.format(
                config_data['PathOfExileDirectory']))
    # Create other missing directories (for which their absence is not an error)
    os.makedirs(config_data['InputLootFilterDirectory'], exist_ok = True)
    # Done parsing
    return config_data
# End ParseProfileConfig

def Test():
    active_profile_name = GetActiveProfileName()
    print('active_profile_name =', active_profile_name)
    all_profile_names = GetAllProfileNames()
    print('all_profile_names =', all_profile_names)
    print()
    
    parsed_config_data = ParseProfileConfig('DefaultProfile')
    print('parsed config data:')
    for key, value in parsed_config_data.items():
        print('{} : {} ({})'.format(key, value, type(value).__name__))
# End Test

# Test()

'''
Exampe parsed config data:

ProfileName : DefaultProfile (str)
ConfigFullpath : Profiles/DefaultProfile.config (str)
RulesFullpath : Profiles/DefaultProfile.rules (str)
ChangesFullpath : Profiles/DefaultProfile.changes (str)
DownloadDirectory : FiltersDownload (str)
InputLootFilterDirectory : FiltersInput (str)
PathOfExileDirectory : FiltersPathOfExile (str)
DownloadedLootFilterFilename : BrandLeaguestart.filter (str)
OutputLootFilterFilename : DynamicLootFilter.filter (str)
RemoveDownloadedFilter : False (bool)
HideMapsBelowTier : 0 (int)
AddChaosRecipeRules : True (str)
ChaosRecipeWeaponClassesAnyHeight : "Daggers" "Rune Daggers" "Wands" (str)
ChaosRecipeWeaponClassesMaxHeight3 : "Bows" (str)
DownloadedLootFilterFullpath : FiltersDownload/BrandLeaguestart.filter (str)
InputLootFilterFullpath : FiltersInput/BrandLeaguestart.filter (str)
OutputLootFilterFullpath : FiltersPathOfExile/DynamicLootFilter.filter (str)
'''
