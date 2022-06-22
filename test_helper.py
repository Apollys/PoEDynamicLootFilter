import os

import file_helper
import profile
import test_consts

# Creates filter directories and downloaded filter file.
# Optionally also creates the test profile.
# Note: calls TearDown() first to ensure clean start.
def SetUp(create_profile=True):
    TearDown()
    # Make dirs if missing
    os.makedirs(test_consts.kTestWorkingDirectory, exist_ok=True)
    os.makedirs(test_consts.kTestProfileDownloadDirectory, exist_ok=True)
    os.makedirs(test_consts.kTestProfilePathOfExileDirectory, exist_ok=True)
    # Copy test filter to download directory
    file_helper.CopyFile(test_consts.kTestBaseFilterFullpath, 
            test_consts.kTestProfileDownloadedFilterFullpath)
    # Optionallty, create test profile
    if (create_profile):
        profile.CreateNewProfile(test_consts.kTestProfileName,
                test_consts.kTestProfileConfigValues)
# End SetUp

def TearDown():
    # Delete test profile if it exists
    if (profile.ProfileExists(test_consts.kTestProfileName)):
        profile.DeleteProfile(test_consts.kTestProfileName)
    # Delete test working directory and all its contents
    file_helper.ClearAndRemoveDirectory(test_consts.kTestWorkingDirectory)
# End TearDown