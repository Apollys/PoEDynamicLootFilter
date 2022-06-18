import profile

import os
import os.path
import shutil

import file_helper
from test_helper import AssertEqual, AssertTrue, AssertFalse

kTestDirPrefix = 'TestDir_JWzKc4T0cXaZKJ5ulX6k_'
kTestConfigValues = {
    'DownloadDirectory' : kTestDirPrefix + 'Downloads',
    'PathOfExileDirectory' : kTestDirPrefix + 'PathOfExile',
    'DownloadedLootFilterFilename' : 'TestFilter.filter'}
kTestProfileNames = ['TestProfile_Xn5nxETrF3KOdUacyf8d', 'TestProfile_EketPW7aflDMiJ220H7M']

def SetUp():
    # First, ensure a clean start, in case previous tests failed and didn't tear down
    TearDown()
    # Now, make test test and empty test filter
    os.makedirs(kTestConfigValues['DownloadDirectory'])
    os.makedirs(kTestConfigValues['PathOfExileDirectory'])
    downloaded_filter_fullpath = os.path.join(kTestConfigValues['DownloadDirectory'],
            kTestConfigValues['DownloadedLootFilterFilename'])
    file_helper.WriteToFile('', downloaded_filter_fullpath)
# End SetUp

# Note: TearDown isn't guaranteed to be called unless test passes.
def TearDown():
    # Remove test directories
    shutil.rmtree(kTestConfigValues['DownloadDirectory'], ignore_errors=True)
    shutil.rmtree(kTestConfigValues['PathOfExileDirectory'], ignore_errors=True)
    # Delete test profile files
    for profile_name in kTestProfileNames:
        file_helper.RemoveFileIfExists(os.path.join(
            profile.kProfileDirectory, profile_name + '.config'))
        file_helper.RemoveFileIfExists(os.path.join(
            profile.kProfileDirectory, profile_name + '.changes'))
        file_helper.RemoveFileIfExists(os.path.join(
            profile.kProfileDirectory, profile_name + '.rules'))
# End TearDown

def TestConfigChangesRulesPaths():
    profile_name = kTestProfileNames[0]
    expected_fullpath_stem = os.path.join(profile.kProfileDirectory, profile_name)
    # Config
    config_fullpath = profile.GetProfileConfigFullpath(profile_name)
    AssertEqual(config_fullpath, expected_fullpath_stem + '.config')
    # Changes
    changes_fullpath = profile.GetProfileChangesFullpath(profile_name)
    AssertEqual(changes_fullpath, expected_fullpath_stem + '.changes')
    # Rules
    rules_fullpath = profile.GetProfileRulesFullpath(profile_name)
    AssertEqual(rules_fullpath, expected_fullpath_stem + '.rules')
    print('TestConfigChangesRulesPaths passed!')

def TestListProfileNames():
    expected_profile_names = []
    for f in os.listdir(profile.kProfileDirectory):
        filestem, extension = os.path.splitext(f)
        if ((extension == '.config') and (filestem != 'general')):
            expected_profile_names.append(filestem)
    profile_names = profile.ListProfilesRaw()
    AssertEqual(sorted(profile_names), sorted(expected_profile_names))
    print('TestListProfileNames passed!')

def TestCreateRenameDeleteProfile():
    SetUp()
    profile_name = kTestProfileNames[0]
    AssertFalse(profile.ProfileExists(profile_name))
    # Create profile
    created_profile = profile.CreateNewProfile(profile_name, kTestConfigValues)
    AssertTrue(created_profile != None)
    AssertTrue(created_profile.name == profile_name)
    AssertTrue(profile.ProfileExists(profile_name))
    # Rename profile
    new_profile_name = 'TestProfile_EketPW7aflDMiJ220H7M'
    profile.RenameProfile(profile_name, new_profile_name)
    AssertFalse(profile.ProfileExists(profile_name))
    AssertTrue(profile.ProfileExists(new_profile_name))
    # Delete profile
    profile.DeleteProfile(new_profile_name)
    AssertFalse(profile.ProfileExists(new_profile_name))
    print('TestCreateRenameDeleteProfile passed!')

def TestSetGetActiveProfile():
    SetUp()
    [profile_name, other_profile_name] = kTestProfileNames
    # Create profile and verify it is the active profile after creation
    profile.CreateNewProfile(profile_name, kTestConfigValues)
    AssertTrue(profile.ProfileExists(profile_name))
    AssertEqual(profile.GetActiveProfileName(), profile_name)
    # Create other profile similarly
    profile.CreateNewProfile(other_profile_name, kTestConfigValues)
    AssertTrue(profile.ProfileExists(other_profile_name))
    AssertEqual(profile.GetActiveProfileName(), other_profile_name)
    # Set/get active profile (profile_name)
    profile.SetActiveProfile(profile_name)
    active_profile_name = profile.GetActiveProfileName()
    AssertEqual(active_profile_name, profile_name)
    # Set/get active profile (other_profile_name)
    profile.SetActiveProfile(other_profile_name)
    active_profile_name = profile.GetActiveProfileName()
    AssertEqual(active_profile_name, other_profile_name)
    # Check GetAllProfileNames() returns active profile first
    get_all_profile_names_result = profile.GetAllProfileNames()
    AssertTrue(len(get_all_profile_names_result) >= 2)
    AssertEqual(get_all_profile_names_result[0], active_profile_name)
    # Verify that both profile names are present
    AssertTrue(profile_name in get_all_profile_names_result)
    AssertTrue(other_profile_name in get_all_profile_names_result)
    # Delete profiles and verify they are not still the active profile
    profile.DeleteProfile(profile_name)
    profile.DeleteProfile(other_profile_name)
    AssertTrue(profile.GetActiveProfileName() not in (profile_name, other_profile_name))
    print('TestSetGetActiveProfile passed!')

'''
Exampe Profile config_values:

ProfileName : DefaultProfile (str)
DownloadDirectory : FiltersDownload (str)
InputLootFilterDirectory : FiltersInput (str) (derived)
PathOfExileDirectory : FiltersPathOfExile (str)
DownloadedLootFilterFilename : BrandLeaguestart.filter (str)
OutputLootFilterFilename : DynamicLootFilter.filter (str)
RemoveDownloadedFilter : False (bool)
HideMapsBelowTier : 0 (int)  # To be removed in future
AddChaosRecipeRules : True (str)  # To be removed in future
ChaosRecipeWeaponClassesAnyHeight : "Daggers" "Rune Daggers" "Wands" (str)
ChaosRecipeWeaponClassesMaxHeight3 : "Bows" (str)
DownloadedLootFilterFullpath : FiltersDownload/BrandLeaguestart.filter (str) (derived)
InputLootFilterFullpath : FiltersInput/BrandLeaguestart.filter (str) (derived)
OutputLootFilterFullpath : FiltersPathOfExile/DynamicLootFilter.filter (str) (derived)
'''
def TestParseProfile():
    SetUp()
    profile_name = kTestProfileNames[0]
    created_profile = profile.CreateNewProfile(profile_name, kTestConfigValues)
    AssertEqual(created_profile.config_values['ProfileName'], profile_name)
    # Check required config values match exactly
    AssertEqual(created_profile.config_values['DownloadDirectory'],
            kTestConfigValues['DownloadDirectory'])
    AssertEqual(created_profile.config_values['PathOfExileDirectory'],
            kTestConfigValues['PathOfExileDirectory'])
    AssertEqual(created_profile.config_values['DownloadedLootFilterFilename'],
            kTestConfigValues['DownloadedLootFilterFilename'])
    # Check input directory config value exists
    AssertTrue(bool(created_profile.config_values['InputLootFilterDirectory']))
    AssertEqual(created_profile.config_values['OutputLootFilterFilename'], 'DynamicLootFilter.filter')
    AssertTrue(created_profile.config_values['RemoveDownloadedFilter'] in (True, False))
    # Check Chaos params exist
    AssertTrue(bool(created_profile.config_values['ChaosRecipeWeaponClassesAnyHeight']))
    AssertTrue(bool(created_profile.config_values['ChaosRecipeWeaponClassesMaxHeight3']))
    # Check derived paths are correct
    expected_downloaded_filter_fullpath = os.path.join(
            kTestConfigValues['DownloadDirectory'],
            kTestConfigValues['DownloadedLootFilterFilename'])
    expected_input_filter_fullpath = os.path.join(
            created_profile.config_values['InputLootFilterDirectory'],
            kTestConfigValues['DownloadedLootFilterFilename'])
    expected_output_filter_fullpath = os.path.join(
            created_profile.config_values['PathOfExileDirectory'], 'DynamicLootFilter.filter')
    # Cleanup: delete test profile
    profile.DeleteProfile(profile_name)
    print('TestParseProfile passed!')
    
def TestWriteProfile():
    SetUp()
    profile_name = kTestProfileNames[0]
    created_profile = profile.CreateNewProfile(profile_name, kTestConfigValues)
    config_lines = file_helper.ReadFile(
            profile.GetProfileConfigFullpath(profile_name), retain_newlines=False)
    # Just verify the paths for simplicity (doesn't test everything):
    expected_download_directory_line = 'Download directory: {}'.format(
            kTestConfigValues['DownloadDirectory'])
    expected_poe_directory_line = 'Path of Exile directory: {}'.format(
            kTestConfigValues['PathOfExileDirectory'])
    expected_downloaded_filter_filename_line = 'Downloaded loot filter filename: {}'.format(
            kTestConfigValues['DownloadedLootFilterFilename'])
    expected_output_filter_filename_line = \
            'Output (Path of Exile) loot filter filename: DynamicLootFilter.filter'
    AssertTrue(expected_download_directory_line in config_lines)
    AssertTrue(expected_poe_directory_line in config_lines)
    AssertTrue(expected_downloaded_filter_filename_line in config_lines)
    AssertTrue(expected_output_filter_filename_line in config_lines)
    # Cleanup: delete test profile
    profile.DeleteProfile(profile_name)
    print('TestWriteProfile passed!')

def main():
    TestConfigChangesRulesPaths()
    TestListProfileNames()
    TestCreateRenameDeleteProfile()
    TestSetGetActiveProfile()
    TestParseProfile()
    TestWriteProfile()
    TearDown()
    print('All tests passed!')

if (__name__ == '__main__'):
    main()