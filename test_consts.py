import os.path

kTestResourcesDirectory = 'TestResources'

kTestBaseFilter = os.path.join(
        kTestResourcesDirectory, 'TestNeversinkStrict.filter')

kTestWorkingDirectory = 'TestWorkingDirectory'

# Test profile parameters
kTestProfileName = 'TestProfile_jNG19OR2BASyGiKbgKvY'
kTestProfileDownloadDirectory = os.path.join(
        kTestWorkingDirectory, 'FiltersDownload')
kTestProfilePathOfExileDirectory = os.path.join(
        kTestWorkingDirectory, 'FiltersPathOfExile')
kTestProfileDownloadedFilterFilename = 'TestNeversinkStrict.filter'
kTestProfileDownloadedFilterFullpath = os.path.join(
        kTestProfileDownloadDirectory, 'TestNeversinkStrict.filter')
# Config dict to construct profile
kTestProfileConfigValues = {
    'DownloadDirectory' : kTestProfileDownloadDirectory,
    'PathOfExileDirectory' : kTestProfilePathOfExileDirectory,
    'DownloadedLootFilterFilename' : kTestProfileDownloadedFilterFilename}

