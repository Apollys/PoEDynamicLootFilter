import os
import os.path
import shutil

kInputLootFilterDirectory = 'FiltersInput'
kDownloadDirectory = 'FiltersDownload'

def main():
    for filename in os.listdir(kInputLootFilterDirectory):
        if (filename.endswith('.filter')):
            source_fullpath = os.path.join(kInputLootFilterDirectory, filename)
            destination_fullpath = os.path.join(kDownloadDirectory, filename)
            shutil.copyfile(source_fullpath, destination_fullpath)
            print('Restored {}'.format(destination_fullpath))

if __name__ == '__main__':
    main()
