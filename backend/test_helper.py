import os

import file_helper
import profile
import test_consts

# Creates filter directories and downloaded filter file.
# Optionally specify whether or not to create the profile.
# Optionally pass profile config values.
# Note: calls TearDown() first to ensure clean start.
def SetUp(*, create_profile=True, profile_config_values=test_consts.kTestProfileConfigValues):
    TearDown()
    # Make dirs if missing
    os.makedirs(test_consts.kTestWorkingDirectory, exist_ok=True)
    os.makedirs(profile_config_values['DownloadDirectory'], exist_ok=True)
    os.makedirs(profile_config_values['PathOfExileDirectory'], exist_ok=True)
    # Copy test filter to download directory
    base_filter_filename = profile_config_values['DownloadedLootFilterFilename']
    base_filter_fullpath = os.path.join(test_consts.kTestResourcesDirectory, base_filter_filename)
    file_helper.CopyFile(base_filter_fullpath, os.path.join(
            profile_config_values['DownloadDirectory'], base_filter_filename))
    # Optionally, create test profile
    if (create_profile):
        profile_obj = profile.CreateNewProfile(test_consts.kTestProfileName, profile_config_values)
        file_helper.CopyFile(test_consts.kTestProfileRulesFullpath, profile_obj.rules_path)
# End SetUp

def TearDown():
    # Delete test profile if it exists
    if (profile.ProfileExists(test_consts.kTestProfileName)):
        profile.DeleteProfile(test_consts.kTestProfileName)
    # Delete test working directory and all its contents
    file_helper.ClearAndRemoveDirectory(test_consts.kTestWorkingDirectory)
# End TearDown