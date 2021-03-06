'''
The purpose of this file is to provide file-related functions that do not generate errors,
but rather do what you would naturally expect them to do to fix whatever errors they encounter.
For example, when copying a file from A to B, the standard file copy functions throw an error
if the directory of B does not exist, but here we create the directory if it doesn't exist.

Note: we will still generate an error if the source file does not exist, as there is no clear
natural way to recover from such an error - the user must be notified their copy failed.

File read/write functions:
 - ReadFile(filepath: str, *, strip=False, discard_empty_lines=False) -> List[str]
 - ReadFileToDict(filepath) -> dict
 - WriteToFile(data, filepath)
 - NumLines(filepath) -> int
 - IsFileEmpty(filepath) -> bool

File manipulation functions:
 - CopyFile(source_path, destination_path)
 - MoveFile(source_path, destination_path)
 - RemoveFileIfExists(filepath)
 - ClearFileIfExists(filepath)
 - ClearAndRemoveDirectory(path)

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

# Read lines of a file to a list of strings, such that joining this result with newlines
# yields the exact file contents (as long as additional options are all False).
# Safe against file not existing.
def ReadFile(filepath: str, *, strip=False, discard_empty_lines=False) -> List[str]:
    CheckType(filepath, 'filepath', str)
    CheckType(strip, 'strip', bool)
    CheckType(discard_empty_lines, 'discard_empty_lines', bool)
    lines: List[str] = []
    try:
        with open(filepath, encoding='utf-8') as input_file:
            ends_with_newline = True
            for line in input_file:
                ends_with_newline = line.endswith('\n')
                line = line.rstrip('\n')
                line = line.strip() if strip else line
                if (not discard_empty_lines or (line != '')):
                    lines.append(line)
            # Append final blank line if file ends with newline
            if (ends_with_newline and not discard_empty_lines):
                lines.append('')
            return lines
    except FileNotFoundError:
        return []
# End ReadFile

# Parses each line of the input file as <key>:<value>, or as <key><separator><value>.
# Ignores empty lines, and lines whose first non-whitespace character is '#'.
# Strips key and value before inserting into dict.  Ignores lines missing separator.
def ReadFileToDict(filepath: str, separator=':') -> dict:
    CheckType(filepath, 'filepath', str)
    try:
        result_dict = {}
        with open(filepath, encoding='utf-8') as input_file:
            for line in input_file:
                stripped_line = line.strip()
                if ((stripped_line != '') and not stripped_line.startswith('#')
                        and (separator in stripped_line)):
                    key, value = line.split(':', 1)  # maxsplit = 1
                    result_dict[key.strip()] = value.strip()
        return result_dict
    except FileNotFoundError:
        return {}
# End ReadFile

# Writes data to the file determined by filepath.
# Overwrites the given file if it already exists.
# If data is a non-string iterable type, then it is written as newline-separated items,
# otherwise, str(data) is written directly to file.
# Safe against directory not existing (creates directory if missing).
def WriteToFile(data, filepath: str):
    CheckType(filepath, 'filepath', str)
    parent_directory = os.path.dirname(filepath)
    if (parent_directory != ''):
        os.makedirs(parent_directory, exist_ok=True)
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

# Appends data to the file determined by filepath.
# If data is a non-string iterable type, then it is written as newline-separated items,
# otherwise str(data) is written directly.
# Safe against file or directory not existing (creates file or directory if missing).
def AppendToFile(data, filepath):
    CheckType(filepath, 'filepath', str)
    parent_directory = os.path.dirname(filepath)
    if (parent_directory != ''):
        os.makedirs(parent_directory, exist_ok=True)
    with open(filepath, 'a', encoding='utf-8') as f:
        if (isinstance(data, str)):
            f.write(data)
        else:
            try:
                iter(data)
                data_list = list(data)
                f.write('\n'.join(str(x) for x in data_list))
            except TypeError:
                f.write(str(data))
# End AppendToFile

def NumLines(filepath) -> int:
    num_lines = 0
    with open(filepath) as f:
        for line in f:
            num_lines += 1
    return num_lines
# End NumLines

# Returns True if the file exists and is empty.
# Returns False if the file is nonempty, or does not exist.
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
    if (destination_directory != ''):
        os.makedirs(destination_directory, exist_ok=True)
    # Copies source file to destination, overwriting if destination exists
    shutil.copyfile(source_path, destination_path)
# End CopyFile

# Makes directories on path to destination if not exists
# Overwrites destination if exists
def MoveFile(source_path: str, destination_path: str):
    CheckType(source_path, 'source_path', str)
    CheckType(destination_path, 'destination_path', str)
    destination_directory: str = os.path.dirname(destination_path)
    os.makedirs(destination_directory, exist_ok=True)
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

# Removes the directory and deletes all its contents, if it exists.
# Does nothing if the directory does not exist.
def ClearAndRemoveDirectory(path: str):
    CheckType(path, 'path', str)
    shutil.rmtree(path, ignore_errors=True)
# End ClearAndRemoveDirectory

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