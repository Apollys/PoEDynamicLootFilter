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
    # Potential TODO: check if new_profile_name already exists as a profile
    # Query required config values
    config_values = {}
    # Required keywords: 'DownloadDirectory', 'PathOfExileDirectory', 'DownloadedLootFilterFilename'
    print('\nStep 3: Tell DLF where to find and put your filters')
    # Prompt Download directory
    while (True):
        config_values['DownloadDirectory'] = input('Download directory fullpath: ').strip('"')
        if (os.path.isdir(config_values['DownloadDirectory'])):
            print('Download directory verified!')
            break
        else:
            print('\nThe given directory "{}" does not exist, please paste the full path exactly'.format(
                    download_directory))
    # Prompt downloaded filter name
    config_values['DownloadedLootFilterFilename'] = input(
            'Downloaded filter filename (e.g. "NeversinkReguler.filter"): ').strip('"')
    # Prompt Path of Exile directory
    print('\nNow your Path of Exile filters directory')
    print('Note: this is not the game install location, but rather the "Documents" location.')
    print('This is where your PoE loot filters go, and it should also have a "Screenshots" directory.')
    while (True):
        config_values['PathOfExileDirectory'] = input('Path of Exile filters directory fullpath: ').strip('"')
        if (os.path.isdir(config_values['PathOfExileDirectory'])):
            print('Path of Exile filters directory verified!')
            break
        else:
            print('\nThe given directory "{}" does not exist, please paste the full path exactly'.format(
                    path_of_exile_directory))
    # Generate new profile from config values
    created_profile = profile.CreateNewProfile(new_profile_name, config_values)
    print('\nProfile "{}" created!'.format(new_profile_name))
    # Setup complete
    print('Config data saved to "{}".'.format(created_profile.config_path))
    print('You can edit this file at any time later to update these settings.')
    print('\nSetup complete! Enjoy PoE Dynamic Loot Filter!')
# End main

if __name__ == '__main__':
    main()