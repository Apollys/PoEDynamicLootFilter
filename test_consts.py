import os.path

kTestWorkingDirectory = 'TestWorkingDirectory'

kTestResourcesDirectory = os.path.join('Resources', 'Test')

# =============================== Filter Consts ===============================

kTestBaseFilterFullpath = os.path.join(
        kTestResourcesDirectory, 'TestNeversinkStrict.filter')

# ============================ Test Profile Consts ============================

# Test profile parameters
kTestProfileNames = ['TestProfile_jNG19OR2BASyGiKbgKvY',
        'TestProfile_Xn5nxETrF3KOdUacyf8d', 'TestProfile_EketPW7aflDMiJ220H7M']
kTestProfileName = kTestProfileNames[0]
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

# ================================ Item Consts ================================

kTestItemDirectory = os.path.join(kTestResourcesDirectory, 'Items')
kTestItemsFullpath = os.path.join(kTestItemDirectory, 'test_items.txt')
kItemTestCasesInputFullpath = os.path.join(kTestItemDirectory, 'item_test_cases_verified.txt')
kItemTestCasesGeneratedFullpath = os.path.join(kTestItemDirectory, 'item_test_cases_generated.txt')

kHorizontalSeparator = '=' * 80
kHorizontalSeparatorThin = '~' * 80