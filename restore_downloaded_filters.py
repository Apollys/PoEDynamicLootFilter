import shutil

import config

def main():
    shutil.copyfile(config.kInputLootFilterFullpath, config.kDownloadedLootFilterFullpath)

if __name__ == '__main__':
    main()
