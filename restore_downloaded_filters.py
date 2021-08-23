import os
import os.path
import shutil

import config

def main():
    for filename in os.listdir(config.kInputLootFilterDirectory):
        if (filename.endswith('.filter')):
            source_fullpath = os.path.join(config.kInputLootFilterDirectory, filename)
            destination_fullpath = os.path.join(config.kDownloadDirectory, filename)
            shutil.copyfile(source_fullpath, destination_fullpath)
            print('Restored {}'.format(destination_fullpath))

if __name__ == '__main__':
    main()
