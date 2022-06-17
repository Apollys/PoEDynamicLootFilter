'''
The purpose of this file is to provide file-related functions that do not generate errors,
but rather do what you would naturally expect them to do to fix whatever errors they encounter.
For example, when copying a file from A to B, the standard file copy functions throw an error
if the directory of B does not exist, but here we create the directory if it doesn't exist.

Note: we will still generate an error if the source file does not exist, as there is no clear
natural way to recover from such an error - the user must be notified their copy failed.

File read/write functions:
 - ReadFile(filepath, retain_newlines=True) -> List[str]
 - ReadFileToDict(filepath) -> dict
 - WriteToFile(data, filepath)
 - IsFileEmpty(filepath) -> bool

File manipulation functions:
 - CopyFile(source_path, destination_path)
 - MoveFile(source_path, destination_path)
 - RemoveFileIfExists(filepath)
 - ClearFileIfExists(filepath)

Path-related functions:
 - FilenameWithoutExtension(filepath) -> str
 - ListFilesInDirectory(directory_path, fullpath=False) -> List[str]
'''

import os
import os.path
import shutil
from typing import List

from type_checker import CheckType

# ========================== File Reading/Writing ==========================

# Read lines of a file to a list of strings
# Safe against file not existing
def ReadFile(filepath: str, retain_newlines: bool = True) -> List[str]:
    CheckType(filepath, 'filepath', str)
    CheckType(retain_newlines, 'retain_newlines', bool)
    try:
        with open(filepath, encoding='utf-8') as input_file:
            lines = input_file.readlines()
        if (not retain_newlines):
            for i in range(len(lines)):
                lines[i] = lines[i].rstrip('\n')
        return lines
    except FileNotFoundError:
        return []
# End ReadFile

# Parses each line of the input file as <key>:<value>.
# Strips key and value before inserting into dict, and ignores empty lines.
def ReadFileToDict(filepath: str) -> dict:
    CheckType(filepath, 'filepath', str)
    try:
        result_dict = {}
        with open(filepath, encoding='utf-8') as input_file:
            for line in input_file:
                if (line.strip() != ''):
                    key, value = line.split(':', 1)  # maxsplit = 1
                    result_dict[key.strip()] = value.strip()
        return result_dict
    except FileNotFoundError:
        return {}
# End ReadFile

# Writes data to the file determined by filepath
# Overwrites the given file if it already exists
# If data is a non-string iterable type, then it is written as newline-separated items
# Otherwise, str(data) is written directly to file
# Safe against directory not existing (creates directory if missing)
def WriteToFile(data, filepath: str):
    parent_directory = os.path.dirname(filepath)
    if (parent_directory != ''):
        os.makedirs(parent_directory, exist_ok = True)
    with open(filepath, 'w', encoding='utf-8') as f:
        if (isinstance(data, str)):
            f.write(data)
        else:
            try:
                iter(data)
                data_list = list(data)
                f.write('\n'.join(str(x) for x in data_list))
            except TypeError:
                f.write(str(data))
# End WriteToFile

def IsFileEmpty(filepath: str) -> bool:
    CheckType(filepath, 'filepath', str)
    return os.path.isfile(filepath) and (os.path.getsize(filepath) == 0)
# End IsFileEmpty

# ========================== File Manipulation ==========================

# Makes directories on path to destination if not exists
# Overwrites destination if exists
def CopyFile(source_path: str, destination_path: str):
    CheckType(source_path, 'source_path', str)
    CheckType(destination_path, 'destination_path', str)
    destination_directory: str = os.path.dirname(destination_path)
    os.makedirs(destination_directory, exist_ok = True)
    # Copies source file to destination, overwriting if destination exists
    shutil.copyfile(source_path, destination_path)
# End CopyFile

# Makes directories on path to destination if not exists
# Overwrites destination if exists
def MoveFile(source_path: str, destination_path: str):
    CheckType(source_path, 'source_path', str)
    CheckType(destination_path, 'destination_path', str)
    destination_directory: str = os.path.dirname(destination_path)
    os.makedirs(destination_directory, exist_ok = True)
    # Moves a file from source to destination, overwriting if destination exists
    os.replace(source_path, destination_path)
# End MoveFile

# Removes the file if it exists
# Does nothing if the file or the directory to the file does not exist
def RemoveFileIfExists(filepath: str):
    CheckType(filepath, 'filepath', str)
    if (os.path.isfile(filepath)):
        os.remove(filepath)
# End RemoveFileIfExists

# Rewrites the given file to an empty file if it exists
# Does nothing if the file or the directory to the file does not exist
def ClearFileIfExists(filepath: str):
    CheckType(filepath, 'filepath', str)
    if (os.path.isfile(filepath)):
        open(filepath, 'w').close()
# End ClearFileIfExists

# ========================== Path-related Functionality ==========================

# Example: given 'Some/Dir/Readme.md', returns 'Readme'.
def FilenameWithoutExtension(filepath: str) -> str:
    CheckType(filepath, 'filepath', str)
    return os.path.splitext(os.path.basename(filepath))[0]
# End FilenameWithoutExtension

# Lists all the files in the given directory
# By default, lists only filenames; if paths are desired, use fullpath=True
def ListFilesInDirectory(directory_path: str, fullpath=False) -> List[str]:
    filenames = [f for f in os.listdir(directory_path)
            if os.path.isfile(os.path.join(directory_path, f))]
    if (not fullpath):
        return filenames
    return [os.path.join(directory_path, filename) for filename in filenames]
# End ListFilesInDirectory