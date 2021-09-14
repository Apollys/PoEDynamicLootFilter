'''
The purpose of this file is to provide file manipulation functions that do not generate errors,
but rather do what you would naturally expect them to do to fix whatever errors they encounter.
For example, when copying a file from A to B, the standard file copy functions throw an error
if the directory of B does not exist, but here we create the directory if it doesn't exist.
Note: we will still generate an error if the source file does not exist, as there is no clear
natural way to recover from such an error - the user must be notified their copy failed.

Functions:
 - CopyFile(source_path, destination_path)
 - MoveFile(source_path, destination_path)
 - RemoveFileIfExists(filepath)
 - ClearFileIfExists(filepath)

'''

import os
import os.path
import shutil

from type_checker import CheckType

def IsFileEmpty(filepath: str) -> bool:
    CheckType(filepath, 'filepath', str)
    return os.path.isfile(filepath) and (os.path.getsize(filepath) == 0)
# End IsFileEmpty

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

def ListFilesInDirectory(directory_path: str):
    return [f for f in os.listdir(directory_path)
            if os.path.isfile(os.path.join(directory_path, f))]
# End ListFilesInDirectory
