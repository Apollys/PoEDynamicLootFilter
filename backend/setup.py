# First-time setup script for PoE DLF
#  1. Checks the python major version is correct (3)
#  2. Prompts the user to set their hotkeys
#  3. Prompts the user for a profile name, and creates the new profile
#  4. Prompts the user for:
#    - Download directory, and validates it exists
#    - Downloaded filter name (does not validate it exists)
#    - Path of Exile filters diretory, and validates it exists
#  5. Optional: queries the user about other general config parameters [NYI]
#  6. Saves all info to the newly created profile

import os
import os.path
import sys
import unicodedata

from consts import kRepositoryRootDirectory, kBackendDirectory
import file_helper
import profile

kDlfAhkPath = os.path.join(kRepositoryRootDirectory, 'dynamic_loot_filter.ahk')
kDownloadDirectoryPrefix = 'Download directory:'
kPathOfExileDirectoryPrefix = 'Path of Exile directory:'
kInputDirectoryPrefix = 'Input (backup) loot filter directory:'
kDownloadedFilterPrefix = 'Downloaded loot filter filename:'

kAhkToggleGuiHotkeyTag = '$toggle_gui_hotkey_line'
kAhkWriteFilterHotkeyTag = '$write_filter_hotkey_line'
kAhkReloadFilterHotkeyTag = '$reload_filter_hotkey_line'
kToggleGuiDefaultHotkey = 'F7'
kWriteFilterDefaultHotkey = 'F8'
kReloadFilterDefaultHotkey = 'F9'

kHotkeyModifierChars = '^+!'

# Splits a hotkey string into modifier characters and key characters.
# Returns a pair of (modifier_string, key_string), or (None, None) if input is ill-formed.
def SplitHotkeyString(hotkey_string: str):
    modifier_string: str = ''
    key_string: str = ''
    in_modifier: bool = True
    for c in hotkey_string:
        if (c in kHotkeyModifierChars):
            if (in_modifier):
                modifier_string += c
            else:  # not in_modifier
                print('IsHotkeyStringValid("{}"): all modifiers must come before any key characters'.format(
                    hotkey_string))
                return None, None  # see modifier char after done with modifier -> invalid
        else:  # c is not a modifier character
            in_modifier = False
            key_string += c
    return modifier_string, key_string
# End SplitHotkeyString

# Determines if the given hotkey_string is a valid AHK hotkey.
# Note: the full list of valid keys is here: https://www.autohotkey.com/docs/KeyList.htm.
# This function only checks for the subset of most commonly used keys.
def IsHotkeyStringValid(hotkey_string: str) -> bool:
    # Check for any non-(letter/number/punctuation/symbol) characters
    for c in hotkey_string:
        if (unicodedata.category(c)[0] not in 'LNPS'):
            print('IsHotkeyStringValid("{}"): invalid character "{}"'.format(
                    hotkey_string, c))
            return False
    # Separate into modifier characters and key characters
    modifier_string, key_string = SplitHotkeyString(hotkey_string)
    if (key_string == None):
        return False
    # Check key_string is valid, which means it is one of the following:
    #  - length 1
    #  - F{#} or f{#}, where # is 1-12
    #  - Numpad{#}, where # is 0-9
    #  - XButton1 or XButton2
    if (len(key_string) == 0):
        return False
    elif (len(key_string) == 1):
        return True
    # F{#} or f{#}, where # is 1-12
    elif (key_string[0] in 'Ff'):
        if (key_string[1:] in (str(i) for i in range(1, 13))):
            return True
    # Numpad{#}, where # is 0-9
    elif (key_string.startswith('Numpad')):
        if (key_string[6:] in (str(i) for i in range(0, 10))):
            return True
    # XButton1 or XButton2
    elif (key_string in ('XButton1', 'XButton2')):
        return True
    return False
# End IsHotkeyStringValid

def SetHotkey(tag: str, hotkey_string: str):
    dlf_ahk_script_lines = file_helper.ReadFile(kDlfAhkPath, retain_newlines=False)
    found_flag = False
    for i in range(len(dlf_ahk_script_lines)):
        if (tag in dlf_ahk_script_lines[i]):
            found_flag = True
            split_result = dlf_ahk_script_lines[i].split('::', maxsplit=1)
            split_result[0] = hotkey_string
            dlf_ahk_script_lines[i] = '::'.join(split_result)
    if (not found_flag):
        raise RuntimeError('tag {} not found in {}'.format(tag, kDlfAhkPath))
    file_helper.WriteToFile(dlf_ahk_script_lines, kDlfAhkPath)
# End SetHotkey

def main():
    print('Welcome to the first-time setup script for PoE DLF!')

    # 1. Check python major version
    print('\nStep 1: Checking python version...')
    python_major_version = sys.version_info[0]
    if (python_major_version < 3):
        print('Python version {} detected, Python 3 required'.format(
                python_major_version))
        sys.exit()
    print('Python version {} detected, success!'.format(python_major_version))

    # 2a. Query toggle GUI hotkey
    print('\nStep 2: Set your hotkeys')
    hotkey_string = ''
    while (True):
        print('\nHotkey format: Ctrl = "^", Shift = "+", Alt = "!"')
        print('Example: Ctrl-Shift-a = "^+a"')
        print('Function keys may be typed as "F1" or "f1", ...')
        print()
        hotkey_string = input('Type your toggle GUI hotkey (leave blank for default: '
                '"{}"): '.format(kToggleGuiDefaultHotkey))
        if (hotkey_string == ''):
            hotkey_string = kToggleGuiDefaultHotkey
        if (IsHotkeyStringValid(hotkey_string)):
            break
        print('Invalid hotkey entered: "{}"'.format(hotkey_string))
    SetHotkey(kAhkToggleGuiHotkeyTag, hotkey_string)
    print('\nToggle GUI hotkey set to: "{}"'.format(hotkey_string))

    # 2b. Query write filter hotkey
    print('\nStep 2: Set write filter hotkey')
    hotkey_string = ''
    while (True):
        hotkey_string = input('Type your reload filter hotkey (leave blank for default: '
                '"{}"): '.format(kWriteFilterDefaultHotkey))
        if (hotkey_string == ''):
            hotkey_string = kWriteFilterDefaultHotkey
        if (IsHotkeyStringValid(hotkey_string)):
            break
        print('Invalid hotkey entered: "{}"'.format(hotkey_string))
    SetHotkey(kAhkWriteFilterHotkeyTag, hotkey_string)
    print('\nReload Filter hotkey set to: "{}"'.format(hotkey_string))

    # 2c. Query reload filter hotkey
    print('\nStep 2: Set reload filter hotkey')
    hotkey_string = ''
    while (True):
        hotkey_string = input('Type your reload filter hotkey (leave blank for default: '
                '"{}"): '.format(kReloadFilterDefaultHotkey))
        if (hotkey_string == ''):
            hotkey_string = kReloadFilterDefaultHotkey
        if (IsHotkeyStringValid(hotkey_string)):
            break
        print('Invalid hotkey entered: "{}"'.format(hotkey_string))
    SetHotkey(kAhkReloadFilterHotkeyTag, hotkey_string)
    print('\nReload Filter hotkey set to: "{}"'.format(hotkey_string))
    print('To change your hotkeys later, either edit them directly at the bottom of {}'.format(kDlfAhkPath))
    print('or re-run this script, and use Ctrl-C to exit after this step.')

    # 3. Create new profile
    print('\nStep 3: Create your profile')
    while (True):
        new_profile_name = input('Enter new profile name: ')
        if (new_profile_name == ''):
            print('Profile name cannot be empty')
        elif (new_profile_name in profile.GetAllProfileNames()):
            print('Profile "{}" already exists!\n'.format(new_profile_name))
        else:
            print('Profile name validated! [{}]\n'.format(new_profile_name))
            break

    # 4. Query required config values
    config_values = {}
    # Required keywords: 'DownloadDirectory', 'PathOfExileDirectory', 'DownloadedLootFilterFilename'
    print('\nStep 4: Tell DLF where to find and put your filters')
    # 4a. Prompt Download directory
    while (True):
        config_values['DownloadDirectory'] = input('Download directory fullpath: ').strip('"')
        if (os.path.isdir(config_values['DownloadDirectory'])):
            print('Download directory found! [{}]'.format(config_values['DownloadDirectory']))
            break
        else:
            print('\nThe given directory "{}" does not exist, please paste the full path exactly'.format(
                    config_values['DownloadDirectory']))
    # 4b. Prompt downloaded filter name
    while (True):
        config_values['DownloadedLootFilterFilename'] = input(
                'Downloaded filter filename (e.g. "NeversinkRegular.filter"): ').strip('"')
        downloaded_filter_fullpath = os.path.join(config_values['DownloadDirectory'], config_values['DownloadedLootFilterFilename'])
        if (os.path.isfile(downloaded_filter_fullpath)):
            print('Downloaded filter found! [{}]'.format(downloaded_filter_fullpath))
            break
        else:
            print('\nDownloaded filter "{}" not found, please ensure it is present and the name is correct'.format(
                downloaded_filter_fullpath))
    # 4c. Prompt Path of Exile directory
    print('\nNow your Path of Exile filters directory')
    print('Note: this is not the game install location, but rather the "Documents" location.')
    print('This is where your PoE loot filters go, and it should also have a "Screenshots" directory.')
    while (True):
        config_values['PathOfExileDirectory'] = input('Path of Exile filters directory fullpath: ').strip('"')
        if (os.path.isdir(config_values['PathOfExileDirectory'])):
            print('Path of Exile filters directory found! [{}]'.format(config_values['PathOfExileDirectory']))
            break
        else:
            print('\nThe given directory "{}" does not exist, please paste the full path exactly'.format(
                    config_values['PathOfExileDirectory']))

    # 5. Query additional profile options
    # [NYI]

    # 6. Generate new profile from config values
    created_profile = profile.CreateNewProfile(new_profile_name, config_values)
    print('\nProfile "{}" created!'.format(new_profile_name))

    # Temporary fix - Import filter here
    # Just in case, we'll also delete the Path of Exile filter, if it exists
    file_helper.RemoveFileIfExists(created_profile.config_values['OutputLootFilterFullpath'])
    backend_cli_py = os.path.join(kBackendDirectory, 'backend_cli.py')
    os.system('python {} import_downloaded_filter {}'.format(backend_cli_py, new_profile_name))

    # Setup complete
    print('Config data saved to "{}".'.format(created_profile.config_path))
    print('You can edit this file at any time later to update these settings.')

    print('\nSetup complete! Enjoy PoE Dynamic Loot Filter!')
    input('Press Enter to close setup.py')
# End main

if __name__ == '__main__':
    main()