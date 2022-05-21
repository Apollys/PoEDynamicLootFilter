# First-time setup script for PoE DLF
#  1. Checks the python major version is correct (3)
#  2. Prompts the user for a profile name, and creates the new profile
#  3. Prompts the user for:
#    - Download directory, and validates it exists
#    - Downloaded filter name (does not validate it exists)
#    - Path of Exile filters diretory, and validates it exists
#  4. Optional: queries the user about other general config parameters [NYI]
#  5. Saves all info to the newly created profile

import os.path
import sys

import helper
import profile

kDownloadDirectoryPrefix = 'Download directory:'
kPathOfExileDirectoryPrefix = 'Path of Exile directory:'
kInputDirectoryPrefix = 'Input (backup) loot filter directory:'
kDownloadedFilterPrefix = 'Downloaded loot filter filename:'

def main():
    print('Welcome to the first-time setup script for PoE DLF!')
    # Check python major version
    print('\nStep 1: Checking python version...')
    python_major_version = sys.version_info[0]
    if (python_major_version < 3):
        print('Python version {} detected, Python 3 required'.format(
                python_major_version))
        sys.exit()
    print('Python version {} detected, success!'.format(python_major_version))
    # Create new profile
    print('\nStep 2: Create your profile')
    new_profile_name = input('Enter new profile name: ')
    profile.CreateNewProfile(new_profile_name)
    print('Profile "{}" created!'.format(new_profile_name))
    # Get Download and Path of Exile directories
    print('\nStep 3: Tell DLF where to find and put your filters')
    # Prompt Download directory
    download_directory = ''
    while (True):
        download_directory = input('Download directory fullpath: ').strip('"')
        if (os.path.isdir(download_directory)):
            print('Download directory verified!')
            break
        else:
            print('\nThe given directory "{}" does not exist, please paste the full path exactly'.format(
                    download_directory))
    # Prompt downloaded filter name
    downloaded_filter_filename = input('Downloaded filter filename (e.g. "NeversinkReguler.filter"): ').strip('"')
    # Prompt Path of Exile directory
    print('\nNow your Path of Exile filters directory')
    print('Note: this is not the game install location, but rather the "Documents" location.')
    print('This is where your PoE loot filters go, and it should also have a "Screenshots" directory.')
    path_of_exile_directory = ''
    while (True):
        path_of_exile_directory = input('Path of Exile filters directory fullpath: ').strip('"')
        if (os.path.isdir(path_of_exile_directory)):
            print('Path of Exile filters directory verified!')
            break
        else:
            print('\nThe given directory "{}" does not exist, please paste the full path exactly'.format(
                    path_of_exile_directory))
    # Infer Input directory from Path of Exile directory
    input_directory = os.path.join(path_of_exile_directory, 'InputFiltersBackup')
    # Write info to the newly created profile
    config_path = os.path.join(profile.kProfileDirectory, new_profile_name + '.config')
    config_lines = helper.ReadFile(config_path, retain_newlines = False)
    for i in range(len(config_lines)):
        if (config_lines[i].startswith(kDownloadDirectoryPrefix)):
            config_lines[i] = kDownloadDirectoryPrefix + ' ' + download_directory
        if (config_lines[i].startswith(kDownloadedFilterPrefix)):
            config_lines[i] = kDownloadedFilterPrefix + ' ' + downloaded_filter_filename
        elif (config_lines[i].startswith(kPathOfExileDirectoryPrefix)):
            config_lines[i] = kPathOfExileDirectoryPrefix + ' ' + path_of_exile_directory
        elif (config_lines[i].startswith(kInputDirectoryPrefix)):
            config_lines[i] = kInputDirectoryPrefix + ' ' + input_directory
    helper.WriteToFile(config_lines, config_path)
    # Setup complete
    config_path = os.path.join(profile.kProfileDirectory, new_profile_name + '.profile')
    print('\nConfig "{}" updated successfully!'.format(config_path))
    print('You can edit this file at any time later to update these settings.')
    print('\nSetup complete! Enjoy PoE Dynamic Loot Filter!')
# End main

if __name__ == '__main__':
    main()