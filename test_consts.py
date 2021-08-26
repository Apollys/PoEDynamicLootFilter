import os.path

import config

kTestDirectory = 'TestData'

kProfileName = 'TestProfile'

kLogFilename = 'test.log'

kDownloadDirectory = os.path.join(kTestDirectory, 'FiltersDownload')
kInputLootFilterDirectory = os.path.join(kTestDirectory, 'FiltersInput')
kPathOfExileDirectory = os.path.join(kTestDirectory, 'FiltersPathOfExile')

kDownloadedLootFilterFilename = 'BrandLeaguestart.filter'
kPathOfExileLootFilterFilename = 'Test_DynamicLootFilter.filter'

kDownloadedLootFilterFullpath = os.path.join(kDownloadDirectory, kDownloadedLootFilterFilename)
kInputLootFilterFullpath = os.path.join(kInputLootFilterDirectory, kDownloadedLootFilterFilename)
kPathOfExileLootFilterFullpath = os.path.join(kPathOfExileDirectory, kPathOfExileLootFilterFilename)

kProfileFullpath = os.path.join(config.kProfileDirectory, kProfileName + '.profile')

kLogFullpath = os.path.join(kTestDirectory, kLogFilename)

kTestBatchFullpath = os.path.join(kTestDirectory, 'backend_cli.test_input')
